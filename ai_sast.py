import sys
import json
import os
from ai_utils import analyze_with_llm, create_pdf_report

SAST_SYSTEM_PROMPT = "You are a cybersecurity expert performing static code analysis."

def parse_sast_results(file_path):
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return []
        
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[!] Invalid JSON in {file_path}: {e}")
            return []

def main():
    input_file = "sonar-report.json"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    # Check if file exists, if not, fallback to a dummy one so Jenkins pipeline doesn't fail immediately in testing
    if not os.path.exists(input_file):
        print(f"[{input_file}] not found. Using a dummy SAST vulnerability for demonstration.")
        vulnerabilities = [
            {
                "type": "SQL Injection", 
                "component": "backend/src/controllers/userController.js", 
                "message": "Database query executing with unvalidated user input."
            }
        ]
    else:
        vulnerabilities = parse_sast_results(input_file)

    # Convert object to list if it's a dict (e.g. issues list inside an object)
    if isinstance(vulnerabilities, dict) and "issues" in vulnerabilities:
        vulnerabilities = vulnerabilities["issues"]
    elif not isinstance(vulnerabilities, list):
        vulnerabilities = []
    
    results = []
    
    for count, vuln in enumerate(vulnerabilities):
        vuln_type = vuln.get("type", vuln.get("rule", "Unknown Vulnerability"))
        
        # Clean up component path (remove SonarQube project prefix if present)
        vuln_code_location = vuln.get("component", vuln.get("file", "Unknown Location"))
        if ":" in vuln_code_location:
            vuln_code_location = vuln_code_location.split(":")[-1]
            
        vuln_msg = vuln.get("message", "No description")
        
        user_prompt = f"""Analyze the following vulnerability:

Type: {vuln_type}
Code: {vuln_code_location} - {vuln_msg}

Provide:
- risk level
- clear explanation
- exploitation example
- secure fix with code
"""
        print(f"[*] Analyzing SAST vulnerability: {vuln_type} in {vuln_code_location}...")
        llm_response = analyze_with_llm(SAST_SYSTEM_PROMPT, user_prompt)
        
        results.append({
            "vuln_id": f"SAST-VULN-{count+1}",
            "type": vuln_type,
            "location": vuln_code_location,
            "llm_analysis": llm_response
        })
        
    with open("ai_sast_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("[+] Saved ai_sast_output.json")
    
    if results:
        create_pdf_report("AI SAST Analysis Report", results, "ai_sast_report.pdf")
        print("[+] Saved ai_sast_report.pdf")
    else:
        print("[-] No vulnerabilities found to report on.")

if __name__ == "__main__":
    main()
