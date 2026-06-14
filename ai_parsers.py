"""
Unified parsers for SAST (SonarQube) and DAST (Nuclei / OWASP ZAP) scan reports.
"""
import json
import os


def _read_json_file(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_sonar_issue(issue):
    component = issue.get("component", issue.get("file", "Unknown Location"))
    if ":" in component:
        component = component.split(":")[-1]

    severity = issue.get("severity", issue.get("impactSeverity", "UNKNOWN"))
    issue_type = issue.get("type", issue.get("rule", "Unknown"))

    return {
        "type": issue_type,
        "severity": severity,
        "component": component,
        "message": issue.get("message", "No description"),
        "rule": issue.get("rule", ""),
        "line": issue.get("line") or issue.get("textRange", {}).get("startLine"),
        "effort": issue.get("effort", ""),
        "tags": issue.get("tags", []),
        "raw": issue,
    }


def parse_sonar_report(file_path):
    """Parse SonarQube API JSON or a simplified issues array."""
    data = _read_json_file(file_path)
    if data is None:
        return []

    if isinstance(data, list):
        issues = data
    elif isinstance(data, dict):
        issues = data.get("issues", data.get("vulnerabilities", []))
    else:
        return []

    return [_normalize_sonar_issue(i) for i in issues if isinstance(i, dict)]


def sort_sonar_issues(issues):
    severity_priority = {
        "BLOCKER": 1,
        "CRITICAL": 2,
        "MAJOR": 3,
        "MINOR": 4,
        "INFO": 5,
    }
    type_priority = {
        "VULNERABILITY": 1,
        "SECURITY_HOTSPOT": 2,
        "BUG": 3,
        "CODE_SMELL": 4,
    }

    def sort_key(item):
        sev = severity_priority.get(str(item.get("severity", "")).upper(), 6)
        typ = type_priority.get(str(item.get("type", "")).upper(), 5)
        return (sev, typ)

    return sorted(issues, key=sort_key)


def _parse_nuclei_entry(entry):
    info = entry.get("info", {})
    extracted = entry.get("extracted-results", entry.get("extracted_results", []))
    return {
        "source": "nuclei",
        "type": info.get("name", entry.get("template-id", entry.get("templateID", "Unknown Finding"))),
        "severity": info.get("severity", "unknown"),
        "url": entry.get("matched-at", entry.get("host", "Unknown URL")),
        "description": info.get("description", entry.get("description", "No description available")),
        "template_id": entry.get("template-id", entry.get("templateID", "")),
        "payload": extracted[0] if extracted else "Refer to matched URL",
        "tags": info.get("tags", []),
        "raw": entry,
    }


def _parse_zap_alert(alert):
    instances = alert.get("instances", [{}])
    instance = instances[0] if instances else {}
    risk_map = {"3": "high", "2": "medium", "1": "low", "0": "info"}
    riskcode = str(alert.get("riskcode", "0"))

    return {
        "source": "zap",
        "type": alert.get("name", "Unknown ZAP Alert"),
        "severity": risk_map.get(riskcode, "unknown"),
        "url": instance.get("uri", "Unknown URL"),
        "description": alert.get("desc", alert.get("description", "No description available")),
        "template_id": alert.get("pluginid", ""),
        "payload": instance.get("attack", instance.get("evidence", "N/A")),
        "param": instance.get("param", ""),
        "method": instance.get("method", ""),
        "solution": alert.get("solution", ""),
        "raw": alert,
    }


def parse_nuclei_report(file_path):
    """Parse Nuclei output: JSON array, single object, or JSONL."""
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        return []

    findings = []

    # JSON array or single object
    if content.startswith("[") or content.startswith("{"):
        try:
            data = json.loads(content)
            if isinstance(data, list):
                findings = data
            elif isinstance(data, dict):
                findings = [data]
        except json.JSONDecodeError:
            pass

    # JSONL fallback
    if not findings:
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                findings.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return [_parse_nuclei_entry(entry) for entry in findings if isinstance(entry, dict)]


def parse_zap_report(file_path):
    """Parse OWASP ZAP JSON export."""
    data = _read_json_file(file_path)
    if not data:
        return []

    alerts = []
    for site in data.get("site", []):
        if isinstance(site, dict):
            alerts.extend(site.get("alerts", []))

    return [_parse_zap_alert(alert) for alert in alerts if isinstance(alert, dict)]


def parse_dast_report(file_path):
    """Auto-detect Nuclei vs ZAP format."""
    if not os.path.exists(file_path):
        return [], "unknown"

    with open(file_path, "r", encoding="utf-8") as f:
        head = f.read(4096).strip()

    if '"site"' in head and '"alerts"' in head:
        return parse_zap_report(file_path), "zap"

    nuclei_findings = parse_nuclei_report(file_path)
    if nuclei_findings:
        return nuclei_findings, "nuclei"

    return [], "unknown"


def sort_dast_findings(findings):
    severity_priority = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4,
        "info": 5,
    }
    return sorted(
        findings,
        key=lambda x: severity_priority.get(str(x.get("severity", "")).lower(), 6),
    )


def read_source_snippet(file_path, line_number=None, context_lines=8):
    """Read a code snippet around a reported line for richer LLM context."""
    if not file_path or not os.path.exists(file_path):
        return ""

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return ""

    if not lines:
        return ""

    if line_number is None:
        snippet = "".join(lines[: min(len(lines), 40)])
        return snippet[:3000]

    idx = max(int(line_number) - 1, 0)
    start = max(idx - context_lines, 0)
    end = min(idx + context_lines + 1, len(lines))
    numbered = []
    for i in range(start, end):
        prefix = ">>>" if i == idx else "   "
        numbered.append(f"{prefix} {i + 1:4d} | {lines[i].rstrip()}")
    return "\n".join(numbered)[:3000]


def detect_dast_input_file(preferred=None):
    """Pick the best available DAST report file."""
    candidates = [preferred] if preferred else []
    candidates.extend(["nuclei-report.json", "zap-report.json"])
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return preferred or "nuclei-report.json"
