# DevSecOps Application

This is a full-stack web application designed for normal usage as well as advanced security testing in a DevSecOps environment.

## Architecture
- **Frontend**: React.js with Vite and Tailwind CSS.
- **Backend**: Node.js, Express.js, Sequelize ORM.
- **Database**: MySQL.
- **Containerization**: Docker & Docker Compose.
- **CI/CD**: Jenkinsfile included for SAST, DAST, and SCA scanning.

## Running the Application

### 1. Requirements
- Docker and Docker Compose installed on your machine.

### 2. Setup
Navigate to the root directory and build the containers:
```bash
docker-compose up --build -d
```

### 3. Accessing the Application
- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:5000/api
- **Database**: Port 3306 (user: `devsecops_user`, pass: `securepassword`)

### 4. Default Users
For security testing, the database is seeded with a vulnerable static password for the admin account:
- **Email**: `admin@cmr.local`
- **Password**: `adminpassword`

## Security Testing Context (Vulnerabilities)
The backend contains a dedicated route `/api/vulnerable` populated with OWASP Top 10 vulnerabilities. These are explicitly tagged for security testing (e.g. SAST, DAST).
- **SQLi**: `GET /api/vulnerable/sqli?email=...`
- **Command Injection**: `POST /api/vulnerable/cmdi`
- **IDOR**: `GET /api/vulnerable/idor/:id`
- **XSS**: `GET /api/vulnerable/xss?search=...`
- **Insecure Deserialization**: `POST /api/vulnerable/deserialize`






 AI SecOps Platform Walkthrough
I have successfully developed and integrated the production-ready AI services for your DevSecOps platform!

🏗️ What Was Built
We created a modular and extensible architecture tailored for Jenkins automation while also providing an excellent user experience via an interactive web interface.

1. ai_utils.py
Serves as the core integration hub. It contains:

Secure connection to Groq LLaMA-3.3-70b-versatile using the provided API key.
Professional PDF Generation logic using fpdf2 that creates human-readable security reports (ai_sast_report.pdf, ai_dast_report.pdf).
2. ai_sast.py (Static Analysis)
Input: Automatically looks for sonar-report.json (or any file via CLI argument python ai_sast.py <file>).
Processing: Loops through vulnerability JSON, generating specialized LLM prompts containing the vulnerability type, code component, and message.
Output: Generates ai_sast_output.json and a formatted ai_sast_report.pdf output containing step-by-step risk explanation and secure code fixes.
3. ai_dast.py (Dynamic/Pentest Analysis)
Input: Automatically looks for OWASP ZAP's output zap-report.json.
Processing: Extracts nested ZAP alerts to find the attack URL, parameter, and payload. Requests exploit feasibility checks from the LLM.
Output: Generates ai_dast_output.json and ai_dast_report.pdf which detail whether the vulnerability is likely a false positive, and how to reproduce it and fix it.
4. app.py (Interactive Web UI & Chatbot)
We used Streamlit to build a modern, high-quality DevSecOps dashboard.
Users can manually upload SAST or DAST JSON files into respective tabs to generate on-the-fly AI reports.
Pentest Assistant Chatbot: A fully interactive chat interface retaining conversation history where developers or security engineers can ask conversational questions (e.g. “How to fix an XSS in my React component?”).
🚀 How to Run
In Jenkins / CI Pipeline
You don't need to change your Jenkinsfile. The pipeline is already configured to run:

bash
python ai_sast.py
python ai_dast.py
(Make sure to pip install -r requirements-ai.txt in your Jenkins worker before running these scripts!)

Running the Web Interface
To launch the interactive dashboard and Chatbot mode locally:

bash
pip install -r requirements-ai.txt
streamlit run app.py
This will open the web server on your local browser (typically http://localhost:8501).

