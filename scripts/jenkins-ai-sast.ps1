param(
    [string]$AiUrl = "http://localhost:8506",
    [string]$ReportFile = "sonar-report.json",
    [int]$MaxIssues = 10
)

$ErrorActionPreference = "Stop"

Write-Host "INFO: Checking AI service at $AiUrl/health ..."
$health = Invoke-RestMethod -Uri "$AiUrl/health" -Method Get -TimeoutSec 30
Write-Host "OK: AI service status: $($health.status) | Groq: $($health.groq)"

if (-not (Test-Path $ReportFile)) {
    throw "Report file not found: $ReportFile"
}

$reportPath = (Resolve-Path $ReportFile).Path
$url = ('{0}/api/v1/analyze/sast?max_issues={1}&include_summary=true&include_pdf=true' -f $AiUrl.TrimEnd('/'), $MaxIssues)

Write-Host "INFO: Sending SAST report to AI service..."
$raw = & curl.exe -sS -X POST $url -F ("report=@{0};type=application/json" -f $reportPath)
if ($LASTEXITCODE -ne 0) {
    throw "curl failed posting SAST report (exit $LASTEXITCODE)"
}

$response = $raw | ConvertFrom-Json
if (-not $response.findings) {
    throw "AI SAST response missing findings: $raw"
}

@{
    summary = $response.summary
    findings = $response.findings
} | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 "ai_sast_output.json"

$count = @($response.findings).Count
Write-Host "DONE: Saved ai_sast_output.json ($count items)"

if ($response.pdf_base64) {
    [IO.File]::WriteAllBytes("ai_sast_report.pdf", [Convert]::FromBase64String($response.pdf_base64))
    Write-Host "DONE: Saved ai_sast_report.pdf"
}
