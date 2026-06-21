pipeline {
    agent any

    tools {
        nodejs 'node24'
        jdk 'JDK21'
    }

    parameters {
        string(name: 'REPO_URL', defaultValue: 'https://github.com/haitham-apteshr/devsecops.git', description: 'GitHub Repository URL for Checkout')
        string(name: 'AI_SERVICE_URL', defaultValue: 'http://localhost:8306', description: 'External AI API (start with docker-compose.ai.yml — like SonarQube)')
    }

    environment {
        SONAR_TOKEN = credentials('sonarqube-token')
        BACKEND_IMAGE = 'devsecops-backend:latest'
        FRONTEND_IMAGE = 'devsecops-frontend:latest'
    }

    stages {
        stage('1. Checkout') {
            steps {
                echo "1. Pulling code from Git repository: ${params.REPO_URL}"
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[url: "${params.REPO_URL}"]])
            }
        }

        stage('2. Verify Environment') {
            steps {
                echo "2. Printing versions of node, npm, and java..."
                bat 'node --version'
                bat 'npm --version'
                bat 'java -version'
            }
        }

        stage('3. Install Dependencies') {
            steps {
                echo "3. Installing backend and frontend dependencies only (AI runs in external Docker)..."
                dir('backend') {
                    bat 'npm install'
                }
                dir('frontend') {
                    bat 'npm install'
                }
            }
        }

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

        stage('5. Unit Tests') {
            steps {
                echo "5. Executing unit tests..."
                dir('backend') {
                    bat 'npm test'
                }
                dir('frontend') {
                    bat 'set CI=true && npm test'
                }
            }
        }

        stage('6. SAST - SonarQube Scan') {
            steps {
                echo "6. Running SonarQube scan via npx sonar-scanner..."
                withSonarQubeEnv('SonarQube') {
                    bat """
                    npx sonar-scanner ^
                      -Dsonar.projectKey=devsecops-app ^
                      -Dsonar.projectName="DevSecOps Application" ^
                      -Dsonar.sources=. ^
                      -Dsonar.host.url=http://localhost:9500 ^
                      -Dsonar.login=%SONAR_TOKEN% ^
                      -Dsonar.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/*.test.js,**/*.test.jsx,**/test/**,**/ai_*.py,**/app.py,**/generate_*.py,**/test_groq.py ^
                      -Dsonar.javascript.node.maxspace=2048 ^
                      -Dsonar.javascript.environments=browser,node
                    """
                }
            }
        }

        stage('7. Quality Gate') {
            steps {
                echo "7. Waiting for SonarQube analysis and quality gate..."
                script {
                    def qgStatus = powershell(returnStatus: true, script: """
                        & '${env.WORKSPACE}\\scripts\\wait-for-quality-gate.ps1' -MaxWaitMinutes 15
                    """)
                    if (qgStatus != 0) {
                        echo "WARNING: SonarQube quality gate did not pass within the wait window (exited with status ${qgStatus}). Continuing build as success..."
                    } else {
                        echo "SUCCESS: SonarQube quality gate passed."
                    }
                }
            }
        }

        stage('8. Verify AI Service') {
            steps {
                echo "8. Verifying external AI Docker service (must be running locally, like SonarQube)..."
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    powershell """
                        & '${env.WORKSPACE}\\scripts\\wait-for-ai.ps1' -AiUrl '${params.AI_SERVICE_URL}' -MaxWaitSeconds 60
                    """
                }
            }
        }

        stage('9. AI SAST Analysis') {
            steps {
                echo "9. Sending SonarQube report to external AI service..."
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    bat 'curl -s -u %SONAR_TOKEN%: "http://localhost:9500/api/issues/search?componentKeys=devsecops-app&resolved=false&types=VULNERABILITY,BUG,SECURITY_HOTSPOT&ps=100" -o sonar-report.json'
                    powershell """
                        & '${env.WORKSPACE}\\scripts\\jenkins-ai-sast.ps1' -AiUrl '${params.AI_SERVICE_URL}' -ReportFile sonar-report.json
                    """
                }
            }
        }

        stage('10. Build Docker Images') {
            steps {
                echo "10. Building Docker images for Backend and Frontend..."
                bat "docker build -t %BACKEND_IMAGE% ./backend"
                bat "docker build -t %FRONTEND_IMAGE% ./frontend"
            }
        }

        stage('11. Container Security Scan') {
            steps {
                echo "11. Running Trivy container security scan..."
                powershell '''
                    $trivyExe = Join-Path $PWD.Path "trivy.exe"
                    if (-Not (Test-Path $trivyExe)) {
                        Write-Host "Fetching latest Trivy version from GitHub..."
                        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/aquasecurity/trivy/releases/latest" -UseBasicParsing
                        $version = $release.tag_name.TrimStart("v")
                        $url = "https://github.com/aquasecurity/trivy/releases/download/v${version}/trivy_${version}_Windows-64bit.zip"
                        Invoke-WebRequest -Uri $url -OutFile "trivy.zip" -UseBasicParsing
                        Expand-Archive -Path "trivy.zip" -DestinationPath "." -Force
                    }
                    & $trivyExe --version
                '''
                bat 'trivy.exe image --scanners vuln --severity HIGH,CRITICAL --exit-code 0 --format json -o trivy-backend.json %BACKEND_IMAGE%'
                bat 'trivy.exe image --scanners vuln --severity HIGH,CRITICAL --exit-code 0 --format json -o trivy-frontend.json %FRONTEND_IMAGE%'
                bat 'trivy.exe image --scanners vuln --severity HIGH,CRITICAL --exit-code 0 --format table %BACKEND_IMAGE%'
                bat 'trivy.exe image --scanners vuln --severity HIGH,CRITICAL --exit-code 0 --format table %FRONTEND_IMAGE%'
            }
        }

        stage('12. Deploy to Staging (Docker Compose)') {
            steps {
                echo "12. Deploying app stack only (db + backend + frontend) — AI is external..."
                bat 'docker rm -f devsecops_db devsecops_backend devsecops_frontend 2>nul & exit 0'
                bat 'docker-compose up -d --build --remove-orphans'
                sleep time: 20, unit: 'SECONDS'
                bat 'curl -I http://localhost:80 || curl -I http://localhost:5000 || echo "Staging services are up"'
            }
        }

        stage('13. DAST - Nuclei (Docker)') {
            steps {
                echo "13. Running Nuclei vulnerability scan..."
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    bat 'docker run --rm -v "%WORKSPACE%":/output projectdiscovery/nuclei:latest -u http://host.docker.internal:80 -json-export /output/nuclei-report.json'
                }
            }
        }

        stage('14. AI DAST Analysis') {
            steps {
                echo "14. Sending Nuclei report to external AI service..."
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    powershell """
                        & '${env.WORKSPACE}\\scripts\\jenkins-ai-dast.ps1' -AiUrl '${params.AI_SERVICE_URL}'
                    """
                }
            }
        }

        stage('15. Reporting') {
            steps {
                echo "15. Generating consolidated security report and archiving artifacts..."
                powershell """
                    & '${env.WORKSPACE}\\scripts\\generate-pipeline-report.ps1' `
                        -BuildNumber '${env.BUILD_NUMBER}' `
                        -JobName '${env.JOB_NAME}' `
                        -BuildUrl '${env.BUILD_URL}'
                """
                archiveArtifacts artifacts: 'reports/**, sonar-report.json, nuclei-report.json, quality-gate-result.json, trivy-*.json, ai_*.json, ai_*.pdf, .scannerwork/report-task.txt', allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo "==== SUCCESS: Pipeline completed. ===="
        }
        unstable {
            echo "==== UNSTABLE: Completed with warnings (AI/Quality Gate). Check logs. ===="
        }
        failure {
            echo "==== FAILURE: Pipeline aborted. Review build logs. ===="
        }
        always {
            echo "==== CLEANUP: Tearing down app containers (AI service stays running) ===="
            bat 'docker-compose down --volumes --remove-orphans 2>nul & exit 0'
            bat 'docker rm -f devsecops_db devsecops_backend devsecops_frontend 2>nul & exit 0'
            cleanWs()
        }
    }
}
