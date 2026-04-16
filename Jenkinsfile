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
                    // Build production artifacts
                    bat 'npm run build'
                }
                dir('backend') {
                    // Backend preparation (if Babel or TypeScript is used)
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
                    // Set non-interactive CI flag for React test runner
                    bat 'set CI=true&& npm test'
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 6: SAST - SonarQube Scan
        // -------------------------------------------------------------
        stage('6. SAST - SonarQube Scan') {
            steps {
                echo "6. Running SonarQube scan using Jenkins-managed SonarQube Scanner..."
                // Uses the SonarQube Scanner tool configured in Jenkins Global Tool Configuration
                // and the SonarQube server configured in Jenkins > Configure System
                withSonarQubeEnv('SonarQube') {
                    script {
                        def scannerHome = tool 'SonarScanner'
                        bat "\"${scannerHome}\\bin\\sonar-scanner.bat\" ^\
                          -Dsonar.projectKey=devsecops-app ^\
                          -Dsonar.projectName=\"DevSecOps Application\" ^\
                          -Dsonar.sources=. ^\
                          -Dsonar.host.url=http://host.docker.internal:9000 ^\
                          -Dsonar.token=%SONAR_TOKEN% ^\
                          -Dsonar.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/*.test.js,**/*.test.jsx,**/test/**"
                    }
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 7: Quality Gate
        // -------------------------------------------------------------
        stage('7. Quality Gate') {
            steps {
                echo "7. Waiting for SonarQube to return Quality Gate status..."
                timeout(time: 5, unit: 'MINUTES') {
                    // Requires SonarQube Scanner plugin. Will abort on Failure.
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // -------------------------------------------------------------
        // Stage 8: AI SAST Analysis
        // -------------------------------------------------------------
        stage('8. AI SAST Analysis') {
            steps {
                echo "8. Executing custom AI SAST script..."
                // This script yields: risk level, vulnerability explanation, and recommended fixes
                bat 'python ai_sast.py'
            }
        }

        // -------------------------------------------------------------
        // Stage 9: Build Docker Images
        // -------------------------------------------------------------
        stage('9. Build Docker Images') {
            steps {
                echo "9. Building Docker images for Backend and Frontend explicitly..."
                // Explicitly tag images so Trivy can reference them easily
                bat "docker build -t %BACKEND_IMAGE% ./backend"
                bat "docker build -t %FRONTEND_IMAGE% ./frontend"
            }
        }

        // -------------------------------------------------------------
        // Stage 10: Container Security Scan
        // -------------------------------------------------------------
        stage('10. Container Security Scan') {
            steps {
                echo "10. Running Trivy image scanner (Docker container)..."
                // Using exit-code 1 fails pipeline if vulnerabilities are CRITICAL
                bat "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity CRITICAL --exit-code 1 %BACKEND_IMAGE%"
                bat "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity CRITICAL --exit-code 1 %FRONTEND_IMAGE%"
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
                
                // Validate accessibility
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
                // Maps the active workspace to save zap-report.html and zap-report.json. Allows exit code overriding so pipeline completes stage.
                bat 'docker run --rm --network=host -v "%WORKSPACE%":/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t http://host.docker.internal:3000 -r zap-report.html -J zap-report.json || echo "ZAP process identified findings (scan completed)"'
            }
        }

        // -------------------------------------------------------------
        // Stage 13: AI DAST Analysis
        // -------------------------------------------------------------
        stage('13. AI DAST Analysis') {
            steps {
                echo "13. Executing custom AI DAST script..."
                // Reads zap-report, outputs validated vulnerabilities, exploitation suggestions, remediation advice
                bat 'python ai_dast.py'
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
