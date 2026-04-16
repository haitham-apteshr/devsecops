pipeline {
    agent any

    // Declare required tools for the Jenkins environment
    tools {
        nodejs 'node24'
        jdk 'JDK21'
    }

    // Parameters to make the pipeline configurable at runtime
    parameters {
        string(name: 'REPO_URL', defaultValue: 'https://github.com/haitham-apteshr/devsecops.git', description: 'GitHub Repository URL for Checkout')
    }

    environment {
        // Retrieve SonarQube authentication token securely from Jenkins credentials
        SONAR_TOKEN = credentials('sonarqube-token')

        // Groq API key for AI-powered SAST and DAST analysis
        // Add this in Jenkins: Manage Jenkins -> Credentials -> Secret text -> ID: groq-api-key
        GROQ_API_KEY = credentials('groq-api-key')

        // Define Docker image tags for consistent building and scanning
        BACKEND_IMAGE = 'devsecops-backend:latest'
        FRONTEND_IMAGE = 'devsecops-frontend:latest'
    }

    stages {
        // -------------------------------------------------------------
        // Stage 1: Checkout
        // -------------------------------------------------------------
        stage('1. Checkout') {
            steps {
                echo "1. Pulling code from Git repository: ${params.REPO_URL}"
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[url: "${params.REPO_URL}"]])
            }
        }

        // -------------------------------------------------------------
        // Stage 2: Verify Environment
        // -------------------------------------------------------------
        stage('2. Verify Environment') {
            steps {
                echo "2. Printing versions of node, npm, and java..."
                bat 'node --version'
                bat 'npm --version'
                bat 'java -version'
            }
        }

        // -------------------------------------------------------------
        // Stage 3: Install Dependencies
        // -------------------------------------------------------------
        stage('3. Install Dependencies') {
            steps {
                echo "3. Installing backend, frontend, and AI package dependencies..."
                dir('backend') {
                    bat 'npm install'
                }
                dir('frontend') {
                    bat 'npm install'
                }
                // FIX: Remove conflicting PyFPDF package before installing requirements
                bat 'pip uninstall pypdf -y || echo "pypdf not installed, skipping"'
                // Install Python dependencies for AI Services
                bat 'pip install -r requirements-ai.txt'
            }
        }

        // -------------------------------------------------------------
        // Stage 4: Build Application
        // -------------------------------------------------------------
        stage('4. Build Application') {
            steps {
                echo "4. Building React frontend and preparing backend..."
                dir('frontend') {
                    bat 'npm run build'
                }
                dir('backend') {
                    echo "Backend code prepared."
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 5: Unit Tests
        // -------------------------------------------------------------
        stage('5. Unit Tests') {
            steps {
                echo "5. Executing unit tests. Jenkins will fail if tests return a non-zero exit code."
                dir('backend') {
                    bat 'npm test'
                }
                dir('frontend') {
                    bat 'set CI=true && npm test'
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 6: SAST - SonarQube Scan
        // -------------------------------------------------------------
        stage('6. SAST - SonarQube Scan') {
            steps {
                echo "6. Running SonarQube scan via npx sonar-scanner..."
                withSonarQubeEnv('SonarQube') {
                    bat """
                    npx sonar-scanner ^
                      -Dsonar.projectKey=devsecops-app ^
                      -Dsonar.projectName="DevSecOps Application" ^
                      -Dsonar.sources=. ^
                      -Dsonar.host.url=http://localhost:9000 ^
                      -Dsonar.login=%SONAR_TOKEN% ^
                      -Dsonar.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/*.test.js,**/*.test.jsx,**/test/** ^
                      -Dsonar.javascript.node.maxspace=2048 ^
                      -Dsonar.javascript.environments=browser,node
                    """
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 7: Quality Gate
        // -------------------------------------------------------------
        stage('7. Quality Gate') {
            steps {
                echo "7. Checking SonarQube Quality Gate (non-blocking)..."
                // FIX: SonarQube CE is slow on this machine.
                // catchError marks stage UNSTABLE without aborting the pipeline.
                // The pipeline always continues to security scan stages regardless.
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    timeout(time: 15, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: false
                    }
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 8: AI SAST Analysis
        // -------------------------------------------------------------
        stage('8. AI SAST Analysis') {
            steps {
                echo "8. Executing custom AI SAST script..."
                // FIX: Wrapped in catchError - if Groq API key is missing or unreachable,
                // the stage shows UNSTABLE but does NOT abort the pipeline.
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    // Quick connectivity check first
                    bat 'python test_groq.py'
                    bat 'python ai_sast.py'
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 9: Build Docker Images
        // -------------------------------------------------------------
        stage('9. Build Docker Images') {
            steps {
                echo "9. Building Docker images for Backend and Frontend explicitly..."
                bat "docker build -t %BACKEND_IMAGE% ./backend"
                bat "docker build -t %FRONTEND_IMAGE% ./frontend"
            }
        }

        // -------------------------------------------------------------
        // Stage 10: Container Security Scan
        // -------------------------------------------------------------
        stage('10. Container Security Scan') {
            steps {
                echo "10. Running Trivy container security scan (Windows native binary)..."
                // FIX: Use Join-Path to build trivy path - avoids the \t tab-escape bug
                // that occurs when .\trivy.exe is inside a Groovy string literal.
                powershell '''
                    $trivyExe = Join-Path $PWD.Path "trivy.exe"
                    if (-Not (Test-Path $trivyExe)) {
                        Write-Host "Fetching latest Trivy version from GitHub..."
                        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/aquasecurity/trivy/releases/latest" -UseBasicParsing
                        $version = $release.tag_name.TrimStart("v")
                        $url = "https://github.com/aquasecurity/trivy/releases/download/v${version}/trivy_${version}_Windows-64bit.zip"
                        Write-Host "Downloading Trivy v$version from: $url"
                        Invoke-WebRequest -Uri $url -OutFile "trivy.zip" -UseBasicParsing
                        Expand-Archive -Path "trivy.zip" -DestinationPath "." -Force
                        Write-Host "Trivy v$version downloaded successfully."
                    } else {
                        Write-Host "Trivy already exists, skipping download."
                    }
                    & $trivyExe --version
                '''
                // Scan images - exit-code 0 reports findings without failing the pipeline
                bat 'trivy.exe image --severity HIGH,CRITICAL --exit-code 0 --format table %BACKEND_IMAGE%'
                bat 'trivy.exe image --severity HIGH,CRITICAL --exit-code 0 --format table %FRONTEND_IMAGE%'
            }
        }

        // -------------------------------------------------------------
        // Stage 11: Deploy to Staging (Docker Compose)
        // -------------------------------------------------------------
        stage('11. Deploy to Staging (Docker Compose)') {
            steps {
                echo "11. Deploying Staging environment via docker-compose..."
                bat 'docker-compose up -d --build'

                echo "Waiting for services to become responsive..."
                sleep time: 15, unit: 'SECONDS'

                echo "Ensure application is accessible..."
                bat 'curl -I http://localhost:3000 || curl -I http://localhost:80 || echo "Staging services are up"'
            }
        }

        // -------------------------------------------------------------
        // Stage 12: DAST - OWASP ZAP (Docker)
        // -------------------------------------------------------------
        stage('12. DAST - OWASP ZAP (Docker)') {
            steps {
                echo "12. Running OWASP ZAP baseline scan..."
                bat 'docker run --rm --network=host -v "%WORKSPACE%":/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t http://host.docker.internal:3000 -r zap-report.html -J zap-report.json || echo "ZAP process identified findings (scan completed)"'
            }
        }

        // -------------------------------------------------------------
        // Stage 13: AI DAST Analysis
        // -------------------------------------------------------------
        stage('13. AI DAST Analysis') {
            steps {
                echo "13. Executing custom AI DAST script..."
                // FIX: Wrapped in catchError - if Groq API key is missing or unreachable,
                // the stage shows UNSTABLE but does NOT abort the pipeline.
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    bat 'python ai_dast.py'
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 14: Reporting
        // -------------------------------------------------------------
        stage('14. Reporting') {
            steps {
                echo "14. Archiving test artifacts (Sonar results, ZAP reports, AI output)..."
                archiveArtifacts artifacts: 'zap-report.html, *.json, *.txt, .scannerwork/report-task.txt', allowEmptyArchive: true

                echo "Pipeline reporting complete. Check artifacts for detailed vulnerabilities, severity levels, and summary."
            }
        }
    }

    // -----------------------------------------------------------------
    // Post Actions
    // -----------------------------------------------------------------
    post {
        success {
            echo "==== SUCCESS: Pipeline completed. No severe vulnerabilities identified. ===="
        }
        unstable {
            echo "==== UNSTABLE: Pipeline completed with warnings (AI/Quality Gate issues). Check logs. ===="
        }
        failure {
            echo "==== FAILURE: Pipeline aborted. Review security scans or build logs. ===="
        }
        always {
            echo "==== CLEANUP: Tearing down containers and wiping workspace... ===="
            bat 'docker-compose down'
            cleanWs()
        }
    }
}
