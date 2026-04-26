import sys
import json
import os
from ai_utils import analyze_with_llm, create_pdf_report

DAST_SYSTEM_PROMPT = """You are an elite Penetration Tester and Offensive Security Expert.
Your goal is to validate and provide exploit paths for dynamic vulnerabilities.
When analyzing a DAST finding:
1. Explain how a real-world attacker would discover and weaponize this.
2. Provide a proof-of-concept (PoC) payload or automated script snippet.
3. Reference relevant OWASP Testing Guide (WSTG) sections.
4. Detail the impact on Confidentiality, Integrity, and Availability (CIA).
5. Provide a specific, patched code example or configuration fix.
"""

def parse_nuclei_results(file_path):
    """
    Parses Nuclei JSON output. Nuclei typically outputs JSONL (one JSON object per line).
    """
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return []
        
    vulnerabilities = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    vulnerabilities.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"[!] Invalid JSON line in {file_path}: {e}")
    return vulnerabilities

def main():
    # Look for nuclei-report.json instead of zap-report.json
    input_file = "nuclei-report.json"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"[{input_file}] not found. Using a dummy Nuclei vulnerability for demonstration.")
        vulnerabilities = [
            {
                "info": {"name": "Reflected Cross-Site Scripting", "severity": "medium"},
                "matched-at": "http://localhost:80/search?q=%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
                "template-id": "xss-reflected",
                "extracted-results": ["<script>alert(1)</script>"]
            },
            {
                "info": {"name": "SQL Injection Detection", "severity": "high"},
                "matched-at": "http://localhost:80/api/users?id=1%27%20OR%20%271%27%3D%271",
                "template-id": "sql-injection",
                "description": "Potential SQL injection detected via boolean-based technique."
            }
        ]
    else:
        vulnerabilities = parse_nuclei_results(input_file)

    # Sort vulnerabilities by severity (critical > high > medium > low > info)
    severity_priority = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4,
        "info": 5
    }
    
    vulnerabilities.sort(key=lambda x: severity_priority.get(x.get("info", {}).get("severity", "").lower(), 6))
    
    # Limit analysis to the top 10 issues for maximum quality
    vulnerabilities = vulnerabilities[:10]

    results = []
    
    for count, vuln in enumerate(vulnerabilities):
        info = vuln.get("info", {})
        vuln_type = info.get("name", vuln.get("template-id", "Unknown Nuclei Finding"))
        url = vuln.get("matched-at", "Unknown URL")
        severity = info.get("severity", "unknown")
        description = info.get("description", vuln.get("description", "No description available"))
        
        # Nuclei sometimes provides the exact payload in 'extracted-results' or it's in the URL
        extracted = vuln.get("extracted-results", [])
        payload = extracted[0] if extracted else "Refer to matched URL"
        
        user_prompt = f"""Nuclei Pentest Validation Request:
- Type: {vuln_type}
- Severity: {severity}
- URL: {url}
- Description: {description}
- Extracted Payload: {payload}

Analyze this using RAG context. Focus on exploitability and remediation."""

        print(f"[*] Analyzing Nuclei finding: {vuln_type} on {url}...")
        llm_response = analyze_with_llm(DAST_SYSTEM_PROMPT, user_prompt, use_rag=True)
        
        results.append({
            "vuln_id": f"NUCLEI-VULN-{count+1}",
            "vulnerability_type": vuln_type,
            "severity": severity,
            "target_url": url,
            "description": description,
            "ai_pentest_analysis": llm_response
        })
        
    with open("ai_dast_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("[+] Saved ai_dast_output.json")
    
    if results:
        create_pdf_report("AI-Enhanced Nuclei Pentest Report", results, "ai_dast_report.pdf")
        print("[+] Saved ai_dast_report.pdf")
    else:
        print("[-] No Nuclei findings found to report on.")

if __name__ == "__main__":
    main()
