import sys
import json
import os
from ai_utils import analyze_with_llm, create_pdf_report

DAST_SYSTEM_PROMPT = "You are an expert penetration tester."

def parse_dast_results(file_path):
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return []
        
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[!] Invalid JSON in {file_path}: {e}")
            return []

def extract_zap_vulnerabilities(data):
    """
    Extracts nested ZAP alerts if it's following the standard ZAP JSON structure.
    """
    vulns = []
    # If the root is a dictionary and contains site
    if isinstance(data, dict) and "site" in data:
        for site in data["site"]:
            if "alerts" in site:
                vulns.extend(site["alerts"])
    elif isinstance(data, list):
        vulns = data
    return vulns

def main():
    input_file = "zap-report.json"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"[{input_file}] not found. Using a dummy DAST vulnerability for demonstration.")
        raw_data = [
            {
                "name": "Cross Site Scripting (Reflected)", 
                "instances": [
                    {"uri": "http://localhost:3000/search", "param": "q", "evidence": "<script>alert(1)</script>"}
                ]
            }
        ]
    else:
        raw_data = parse_dast_results(input_file)

    vulnerabilities = extract_zap_vulnerabilities(raw_data)
    
    if not vulnerabilities:
        vulnerabilities = raw_data if isinstance(raw_data, list) else []

    results = []
    
    for count, vuln in enumerate(vulnerabilities):
        vuln_type = vuln.get("name", vuln.get("alert", "Unknown DAST Vulnerability"))
        instances = vuln.get("instances", [{}])
        
        # We'll just analyze the first instance for brevity
        first_instance = instances[0] if instances else {}
        url = first_instance.get("uri", first_instance.get("url", "Unknown URL"))
        param = first_instance.get("param", "Unknown Parameter")
        payload = first_instance.get("evidence", first_instance.get("attack", "Unknown Payload"))
        
        user_prompt = f"""Analyze this vulnerability detected by a DAST tool:

URL: {url}
Parameter: {param}
Payload: {payload}
Type: {vuln_type}

Provide:
- Is this likely exploitable
- How to exploit it step by step (educational purpose)
- Risk level
- Fix recommendation
"""
        print(f"[*] Analyzing DAST vulnerability: {vuln_type} on {url}...")
        llm_response = analyze_with_llm(DAST_SYSTEM_PROMPT, user_prompt)
        
        results.append({
            "vuln_id": f"DAST-VULN-{count+1}",
            "type": vuln_type,
            "url": url,
            "parameter": param,
            "payload": payload,
            "llm_analysis": llm_response
        })
        
    with open("ai_dast_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("[+] Saved ai_dast_output.json")
    
    if results:
        create_pdf_report("AI DAST Analysis Report", results, "ai_dast_report.pdf")
        print("[+] Saved ai_dast_report.pdf")
    else:
        print("[-] No vulnerabilities found to report on.")

if __name__ == "__main__":
    main()
