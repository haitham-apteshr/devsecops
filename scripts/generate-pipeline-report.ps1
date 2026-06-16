param(
    [string]$BuildNumber = $env:BUILD_NUMBER,
    [string]$JobName = $env:JOB_NAME,
    [string]$BuildUrl = $env:BUILD_URL
)

$ErrorActionPreference = "Continue"
$reportDir = "reports"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

function Read-JsonFile($path) {
    if (-not (Test-Path $path)) { return $null }
    try { return Get-Content $path -Raw | ConvertFrom-Json } catch { return $null }
}

function Read-JsonLines($path) {
    if (-not (Test-Path $path)) { return @() }
    $items = @()
    foreach ($line in Get-Content $path) {
        $line = $line.Trim()
        if (-not $line) { continue }
        try { $items += ($line | ConvertFrom-Json) } catch { }
    }
    return $items
}

function Count-TrivyVulns($path) {
    $data = Read-JsonFile $path
    if (-not $data) { return @{ total = 0; critical = 0; high = 0 } }
    $critical = 0; $high = 0; $total = 0
    foreach ($result in @($data.Results)) {
        foreach ($v in @($result.Vulnerabilities)) {
            $total++
            switch ($v.Severity) {
                "CRITICAL" { $critical++ }
                "HIGH" { $high++ }
            }
        }
    }
    return @{ total = $total; critical = $critical; high = $high }
}

function Escape-Html($text) {
    if ($null -eq $text) { return "" }
    return [System.Net.WebUtility]::HtmlEncode([string]$text)
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
$sonar = Read-JsonFile "sonar-report.json"
$aiSast = Read-JsonFile "ai_sast_output.json"
$aiDast = Read-JsonFile "ai_dast_output.json"
$qualityGate = Read-JsonFile "quality-gate-result.json"
$nucleiItems = Read-JsonLines "nuclei-report.json"
$trivyBackend = Count-TrivyVulns "trivy-backend.json"
$trivyFrontend = Count-TrivyVulns "trivy-frontend.json"

$sonarIssueCount = 0
if ($sonar -and $sonar.issues) { $sonarIssueCount = @($sonar.issues).Count }
elseif ($sonar -and $sonar.total) { $sonarIssueCount = [int]$sonar.total }

$qgStatus = "UNKNOWN"
if ($qualityGate -and $qualityGate.projectStatus) {
    $qgStatus = $qualityGate.projectStatus.status
}

$riskScore = "LOW"
if ($trivyBackend.critical + $trivyFrontend.critical -gt 0 -or $sonarIssueCount -gt 20) { $riskScore = "HIGH" }
elseif ($trivyBackend.high + $trivyFrontend.high -gt 0 -or $sonarIssueCount -gt 5) { $riskScore = "MEDIUM" }

$master = [ordered]@{
    report_version = "1.0"
    generated_at = $timestamp
    pipeline = [ordered]@{
        job = $JobName
        build = $BuildNumber
        url = $BuildUrl
    }
    executive_summary = [ordered]@{
        overall_risk = $riskScore
        quality_gate = $qgStatus
        sonar_issues = $sonarIssueCount
        nuclei_findings = $nucleiItems.Count
        ai_sast_findings = if ($aiSast -and $aiSast.findings) { @($aiSast.findings).Count } else { 0 }
        ai_dast_findings = if ($aiDast -and $aiDast.findings) { @($aiDast.findings).Count } else { 0 }
        container_vulnerabilities = [ordered]@{
            backend = $trivyBackend
            frontend = $trivyFrontend
        }
    }
    sast = [ordered]@{
        sonarqube = if ($sonar) { $sonar } else { @{} }
        ai_analysis = if ($aiSast) { $aiSast } else { @{} }
    }
    dast = [ordered]@{
        nuclei = $nucleiItems
        ai_analysis = if ($aiDast) { $aiDast } else { @{} }
    }
    container_scan = [ordered]@{
        backend = (Read-JsonFile "trivy-backend.json")
        frontend = (Read-JsonFile "trivy-frontend.json")
    }
    quality_gate = if ($qualityGate) { $qualityGate } else { @{} }
}

$master | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 "$reportDir\devsecops-security-report.json"

$summaryLines = @(
    "DEVSECOPS PIPELINE SECURITY REPORT",
    "Generated: $timestamp",
    "Build: $JobName #$BuildNumber",
    "",
    "EXECUTIVE SUMMARY",
    "  Overall risk posture : $riskScore",
    "  SonarQube quality gate: $qgStatus",
    "  SonarQube issues      : $sonarIssueCount",
    "  Nuclei DAST findings  : $($nucleiItems.Count)",
    "  AI SAST findings      : $(if ($aiSast -and $aiSast.findings) { @($aiSast.findings).Count } else { 0 })",
    "  AI DAST findings      : $(if ($aiDast -and $aiDast.findings) { @($aiDast.findings).Count } else { 0 })",
    "  Trivy backend (H/C)   : $($trivyBackend.high)/$($trivyBackend.critical)",
    "  Trivy frontend (H/C)  : $($trivyFrontend.high)/$($trivyFrontend.critical)",
    "",
    "ARTIFACTS",
    "  - reports/devsecops-security-report.html",
    "  - reports/devsecops-security-report.json",
    "  - ai_sast_output.json / ai_sast_report.pdf",
    "  - ai_dast_output.json / ai_dast_report.pdf",
    "  - sonar-report.json / nuclei-report.json",
    "  - quality-gate-result.json"
)
$summaryLines | Out-File -Encoding utf8 "$reportDir\devsecops-executive-summary.txt"

$qgClass = if ($qgStatus -eq "OK") { "pass" } else { "fail" }
$riskClass = $riskScore.ToLower()

$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>DevSecOps Security Report</title>
<style>
  :root { --bg:#0f172a; --card:#1e293b; --text:#e2e8f0; --muted:#94a3b8; --accent:#22c55e; --warn:#f59e0b; --bad:#ef4444; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:Segoe UI,system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.5; }
  .wrap { max-width:1100px; margin:0 auto; padding:32px 20px 60px; }
  h1 { font-size:1.8rem; margin:0 0 8px; }
  .meta { color:var(--muted); margin-bottom:28px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin-bottom:28px; }
  .card { background:var(--card); border:1px solid #334155; border-radius:12px; padding:18px; }
  .card .label { font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }
  .card .value { font-size:1.6rem; font-weight:700; margin-top:6px; }
  .badge { display:inline-block; padding:4px 10px; border-radius:999px; font-size:.75rem; font-weight:700; }
  .badge.pass { background:#14532d; color:#86efac; }
  .badge.fail { background:#450a0a; color:#fca5a5; }
  .badge.low { background:#14532d; color:#86efac; }
  .badge.medium { background:#713f12; color:#fcd34d; }
  .badge.high { background:#450a0a; color:#fca5a5; }
  section { margin-top:32px; }
  section h2 { font-size:1.15rem; border-bottom:1px solid #334155; padding-bottom:8px; margin-bottom:16px; }
  table { width:100%; border-collapse:collapse; font-size:.9rem; }
  th, td { text-align:left; padding:10px 12px; border-bottom:1px solid #334155; vertical-align:top; }
  th { color:var(--muted); font-weight:600; }
  .summary-box { background:#111827; border-left:4px solid var(--accent); padding:16px 18px; border-radius:8px; white-space:pre-wrap; }
  footer { margin-top:40px; color:var(--muted); font-size:.8rem; }
</style>
</head>
<body>
<div class="wrap">
  <h1>DevSecOps Pipeline Security Report</h1>
  <div class="meta">Generated $timestamp &mdash; $JobName build #$BuildNumber</div>

  <div class="grid">
    <div class="card"><div class="label">Quality Gate</div><div class="value"><span class="badge $qgClass">$qgStatus</span></div></div>
    <div class="card"><div class="label">Overall Risk</div><div class="value"><span class="badge $riskClass">$riskScore</span></div></div>
    <div class="card"><div class="label">SonarQube Issues</div><div class="value">$sonarIssueCount</div></div>
    <div class="card"><div class="label">Nuclei Findings</div><div class="value">$($nucleiItems.Count)</div></div>
    <div class="card"><div class="label">AI SAST Items</div><div class="value">$(if ($aiSast -and $aiSast.findings) { @($aiSast.findings).Count } else { 0 })</div></div>
    <div class="card"><div class="label">AI DAST Items</div><div class="value">$(if ($aiDast -and $aiDast.findings) { @($aiDast.findings).Count } else { 0 })</div></div>
  </div>

  <section>
    <h2>Executive Summary</h2>
    <div class="summary-box">$(Escape-Html($(if ($aiSast.summary) { $aiSast.summary } elseif ($aiDast.summary) { $aiDast.summary } else { "Pipeline completed. Review detailed sections below for SAST, DAST, container, and AI-enhanced findings." })))</div>
  </section>

  <section>
    <h2>Static Analysis (SAST)</h2>
    <table>
      <tr><th>Source</th><th>Count</th><th>Notes</th></tr>
      <tr><td>SonarQube</td><td>$sonarIssueCount</td><td>Open vulnerabilities, bugs, and security hotspots</td></tr>
      <tr><td>AI-enhanced SAST</td><td>$(if ($aiSast -and $aiSast.findings) { @($aiSast.findings).Count } else { 0 })</td><td>Groq LLM remediation analysis with RAG context</td></tr>
    </table>
  </section>

  <section>
    <h2>Dynamic Analysis (DAST)</h2>
    <table>
      <tr><th>Scanner</th><th>Findings</th><th>Top items</th></tr>
      <tr>
        <td>Nuclei</td>
        <td>$($nucleiItems.Count)</td>
        <td>$(Escape-Html(($nucleiItems | Select-Object -First 3 | ForEach-Object { if ($_.info) { $_.info.name } elseif ($_.'template-id') { $_.'template-id' } } ) -join "; "))</td>
      </tr>
      <tr>
        <td>AI-enhanced DAST</td>
        <td>$(if ($aiDast -and $aiDast.findings) { @($aiDast.findings).Count } else { 0 })</td>
        <td>Scanner: $(Escape-Html($(if ($aiDast.scanner) { $aiDast.scanner } else { "n/a" })))</td>
      </tr>
    </table>
  </section>

  <section>
    <h2>Container Security (Trivy)</h2>
    <table>
      <tr><th>Image</th><th>Total</th><th>High</th><th>Critical</th></tr>
      <tr><td>devsecops-backend</td><td>$($trivyBackend.total)</td><td>$($trivyBackend.high)</td><td>$($trivyBackend.critical)</td></tr>
      <tr><td>devsecops-frontend</td><td>$($trivyFrontend.total)</td><td>$($trivyFrontend.high)</td><td>$($trivyFrontend.critical)</td></tr>
    </table>
  </section>

  <section>
    <h2>Quality Gate Conditions</h2>
    <table>
      <tr><th>Metric</th><th>Status</th><th>Actual</th><th>Threshold</th></tr>
"@

if ($qualityGate -and $qualityGate.projectStatus.conditions) {
    foreach ($cond in $qualityGate.projectStatus.conditions) {
        $html += "<tr><td>$(Escape-Html($cond.metricKey))</td><td>$(Escape-Html($cond.status))</td><td>$(Escape-Html($cond.actualValue))</td><td>$(Escape-Html($cond.errorThreshold))</td></tr>`n"
    }
} else {
    $html += "<tr><td colspan='4'>No quality gate details captured.</td></tr>`n"
}

$html += @"
    </table>
  </section>

  <footer>
    DevSecOps Application &mdash; Automated pipeline report. Open <code>devsecops-security-report.json</code> for machine-readable output.
  </footer>
</div>
</body>
</html>
"@

$html | Out-File -Encoding utf8 "$reportDir\devsecops-security-report.html"
Write-Host "DONE: Generated reports in $reportDir"
