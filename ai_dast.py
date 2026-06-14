import argparse
import json
import os
import sys

from ai_parsers import detect_dast_input_file, parse_dast_report, sort_dast_findings
from ai_utils import analyze_with_llm, create_pdf_report, generate_executive_summary

DAST_SYSTEM_PROMPT = """You are an elite Penetration Tester and Offensive Security Expert.
Validate dynamic findings with offensive depth:
1. Explain discovery and weaponization steps for a real attacker.
2. Provide a PoC payload, curl command, or short script snippet.
3. Reference OWASP WSTG sections where relevant.
4. Assess CIA impact (Confidentiality, Integrity, Availability).
5. Provide a specific patched code or configuration fix.
6. State whether this is likely a true positive or false positive and why.
Be tactical and reproducible — developers must be able to verify your PoC."""

DEMO_NUCLEI = [
    {
        "source": "nuclei",
        "type": "Reflected Cross-Site Scripting",
        "severity": "medium",
        "url": "http://localhost:80/search?q=%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
        "description": "Reflected XSS in search parameter.",
        "template_id": "xss-reflected",
        "payload": "<script>alert(1)</script>",
    },
    {
        "source": "nuclei",
        "type": "SQL Injection Detection",
        "severity": "high",
        "url": "http://localhost:80/api/appointments/search?query=1%27+OR+1%3D1--",
        "description": "Potential SQL injection via boolean-based technique.",
        "template_id": "sql-injection",
        "payload": "' OR 1=1 --",
    },
]


def analyze_dast_findings(findings, max_issues=10, include_summary=True, scanner="DAST"):
    sorted_findings = sort_dast_findings(findings)[:max_issues]
    results = []

    for count, vuln in enumerate(sorted_findings):
        user_prompt = f"""{scanner} Pentest Validation Request:
- Type: {vuln.get('type')}
- Severity: {vuln.get('severity')}
- Scanner: {vuln.get('source', scanner).upper()}
- URL: {vuln.get('url')}
- Parameter: {vuln.get('param', 'N/A')}
- Method: {vuln.get('method', 'N/A')}
- Template/Plugin: {vuln.get('template_id', 'N/A')}
- Description: {vuln.get('description')}
- Payload/Evidence: {vuln.get('payload')}
- Recommended Fix (scanner): {vuln.get('solution', 'N/A')}

Analyze exploitability and provide remediation."""

        print(f"[*] Analyzing DAST: {vuln.get('type')} @ {vuln.get('url')}...")
        llm_response = analyze_with_llm(DAST_SYSTEM_PROMPT, user_prompt, use_rag=True)

        results.append(
            {
                "vuln_id": f"DAST-VULN-{count + 1}",
                "vulnerability_type": vuln.get("type"),
                "severity": vuln.get("severity"),
                "scanner": vuln.get("source", scanner),
                "target_url": vuln.get("url"),
                "parameter": vuln.get("param", ""),
                "description": vuln.get("description"),
                "payload": vuln.get("payload"),
                "ai_pentest_analysis": llm_response,
            }
        )

    summary = None
    if include_summary and results:
        print("[*] Generating DAST executive summary...")
        summary = generate_executive_summary(f"DAST ({scanner})", results)

    return results, summary


def main():
    parser = argparse.ArgumentParser(description="AI-enhanced DAST analysis (Nuclei + ZAP)")
    parser.add_argument("input_file", nargs="?", default=None)
    parser.add_argument("--max-issues", type=int, default=10)
    parser.add_argument("--no-summary", action="store_true")
    args = parser.parse_args()

    input_file = detect_dast_input_file(args.input_file)
    scanner_label = "DAST"

    if os.path.exists(input_file):
        findings, scanner_label = parse_dast_report(input_file)
        print(f"[*] Loaded {len(findings)} findings from {input_file} ({scanner_label})")
    else:
        print(f"[{input_file}] not found. Using demo DAST findings.")
        findings = DEMO_NUCLEI
        scanner_label = "nuclei"

    if not findings:
        print("[-] No DAST findings to analyze.")
        sys.exit(0)

    results, summary = analyze_dast_findings(
        findings,
        max_issues=args.max_issues,
        include_summary=not args.no_summary,
        scanner=scanner_label.upper(),
    )

    with open("ai_dast_output.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "findings": results, "scanner": scanner_label}, f, indent=4)

    print("[+] Saved ai_dast_output.json")

    if results:
        title = f"AI-Enhanced {scanner_label.upper()} Pentest Report"
        create_pdf_report(title, results, "ai_dast_report.pdf", executive_summary=summary)
        print("[+] Saved ai_dast_report.pdf")


if __name__ == "__main__":
    main()
