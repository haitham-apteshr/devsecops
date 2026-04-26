import sys
import json
import os
from ai_utils import analyze_with_llm, create_pdf_report

SAST_SYSTEM_PROMPT = """You are a world-class Cybersecurity Architect and Static Analysis expert. 
Your goal is to provide deep technical insights into code vulnerabilities.
When analyzing a vulnerability:
1. Reference industry standards like OWASP Top 10 or SANS Top 25.
2. Provide a clear, step-by-step technical explanation of the root cause.
3. Show a realistic exploit payload or scenario.
4. Provide a production-ready, secure code fix.
5. Explain the 'Defense in Depth' strategy for this specific issue.
"""

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
            },
            {
                "type": "Cross-Site Scripting (XSS)", 
                "component": "frontend/src/components/Comments.jsx", 
                "message": "Rendering unescaped user-provided content."
            }
        ]
    else:
        vulnerabilities = parse_sast_results(input_file)

    # Convert object to list if it's a dict (e.g. issues list inside an object)
    if isinstance(vulnerabilities, dict) and "issues" in vulnerabilities:
        vulnerabilities = vulnerabilities["issues"]
    elif not isinstance(vulnerabilities, list):
        vulnerabilities = []

    # Sort vulnerabilities by type (Vulnerability > Bug > Code Smell)
    type_priority = {
        "VULNERABILITY": 1,
        "SECURITY_HOTSPOT": 2,
        "BUG": 3,
        "CODE_SMELL": 4
    }
    
    vulnerabilities.sort(key=lambda x: type_priority.get(str(x.get("type", "")).upper(), 5))
    
    # Limit analysis to the top 10 issues for maximum quality
    vulnerabilities = vulnerabilities[:10]
    
    results = []
    
    for count, vuln in enumerate(vulnerabilities):
        vuln_type = vuln.get("type", vuln.get("rule", "Unknown Vulnerability"))
        
        # Clean up component path
        vuln_code_location = vuln.get("component", vuln.get("file", "Unknown Location"))
        if ":" in vuln_code_location:
            vuln_code_location = vuln_code_location.split(":")[-1]
            
        vuln_msg = vuln.get("message", "No description")
        
        user_prompt = f"""Vulnerability Analysis Request:
- Type: {vuln_type}
- Location: {vuln_code_location}
- Issue: {vuln_msg}

Analyze this thoroughly using RAG context if available. Focus on high-impact remediation."""
        
        print(f"[*] Analyzing SAST vulnerability: {vuln_type} in {vuln_code_location}...")
        llm_response = analyze_with_llm(SAST_SYSTEM_PROMPT, user_prompt, use_rag=True)
        
        results.append({
            "vuln_id": f"SAST-VULN-{count+1}",
            "vulnerability_type": vuln_type,
            "code_location": vuln_code_location,
            "description": vuln_msg,
            "ai_expert_analysis": llm_response
        })
        
    with open("ai_sast_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("[+] Saved ai_sast_output.json")
    
    if results:
        create_pdf_report("AI-Enhanced SAST Security Analysis Report", results, "ai_sast_report.pdf")
        print("[+] Saved ai_sast_report.pdf")
    else:
        print("[-] No vulnerabilities found to report on.")

if __name__ == "__main__":
    main()
