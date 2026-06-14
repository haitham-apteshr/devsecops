import argparse
import json
import os
import sys

from ai_parsers import parse_sonar_report, read_source_snippet, sort_sonar_issues
from ai_utils import analyze_with_llm, create_pdf_report, generate_executive_summary

SAST_SYSTEM_PROMPT = """You are a world-class Cybersecurity Architect and Static Analysis expert.
Analyze code vulnerabilities with production-grade depth:
1. Map the issue to OWASP Top 10 / CWE where applicable.
2. Explain the root cause using the provided code snippet when available.
3. Provide a realistic exploit scenario or attacker workflow.
4. Deliver a secure, copy-paste-ready code fix in the same language/framework.
5. Recommend defense-in-depth controls (WAF, monitoring, SAST rules, tests).
Be precise and actionable — avoid generic textbook definitions."""

DEMO_VULNERABILITIES = [
    {
        "type": "VULNERABILITY",
        "severity": "CRITICAL",
        "component": "backend/src/controllers/userController.js",
        "message": "Database query executing with unvalidated user input.",
        "rule": "javascript:S3649",
        "line": 42,
    },
    {
        "type": "VULNERABILITY",
        "severity": "MAJOR",
        "component": "frontend/src/pages/Dashboard.jsx",
        "message": "Rendering unescaped user-provided content.",
        "rule": "javascript:S5131",
        "line": 106,
    },
]


def analyze_sast_findings(vulnerabilities, max_issues=10, include_summary=True):
    sorted_issues = sort_sonar_issues(vulnerabilities)[:max_issues]
    results = []

    for count, vuln in enumerate(sorted_issues):
        vuln_type = vuln.get("type", "Unknown")
        location = vuln.get("component", "Unknown Location")
        message = vuln.get("message", "No description")
        severity = vuln.get("severity", "UNKNOWN")
        rule = vuln.get("rule", "")
        line = vuln.get("line")

        snippet = read_source_snippet(location, line)
        extra_context = f"Source code snippet:\n{snippet}" if snippet else ""

        user_prompt = f"""SAST Finding Analysis:
- Type: {vuln_type}
- Severity: {severity}
- Rule: {rule}
- Location: {location}
- Line: {line or 'N/A'}
- Issue: {message}

Analyze thoroughly. If source code is provided, reference specific lines in your remediation."""

        print(f"[*] Analyzing SAST: {vuln_type} @ {location}...")
        llm_response = analyze_with_llm(
            SAST_SYSTEM_PROMPT,
            user_prompt,
            use_rag=True,
            extra_context=extra_context,
        )

        results.append(
            {
                "vuln_id": f"SAST-VULN-{count + 1}",
                "vulnerability_type": vuln_type,
                "severity": severity,
                "code_location": location,
                "line": line,
                "rule": rule,
                "description": message,
                "ai_expert_analysis": llm_response,
            }
        )

    summary = None
    if include_summary and results:
        print("[*] Generating SAST executive summary...")
        summary = generate_executive_summary("SAST (Static Analysis)", results)

    return results, summary


def main():
    parser = argparse.ArgumentParser(description="AI-enhanced SAST analysis")
    parser.add_argument("input_file", nargs="?", default="sonar-report.json")
    parser.add_argument("--max-issues", type=int, default=10)
    parser.add_argument("--no-summary", action="store_true")
    args = parser.parse_args()

    if os.path.exists(args.input_file):
        vulnerabilities = parse_sonar_report(args.input_file)
    else:
        print(f"[{args.input_file}] not found. Using demo SAST findings.")
        vulnerabilities = DEMO_VULNERABILITIES

    if not vulnerabilities:
        print("[-] No SAST issues found.")
        sys.exit(0)

    results, summary = analyze_sast_findings(
        vulnerabilities,
        max_issues=args.max_issues,
        include_summary=not args.no_summary,
    )

    with open("ai_sast_output.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "findings": results}, f, indent=4)

    print("[+] Saved ai_sast_output.json")

    if results:
        create_pdf_report(
            "AI-Enhanced SAST Security Analysis Report",
            results,
            "ai_sast_report.pdf",
            executive_summary=summary,
        )
        print("[+] Saved ai_sast_report.pdf")


if __name__ == "__main__":
    main()
