param(
    [string]$AiUrl = "http://localhost:8506",
    [string]$ReportFile = "nuclei-report.json",
    [int]$MaxIssues = 10
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ReportFile)) {
    if (Test-Path "zap-report.json") {
        $ReportFile = "zap-report.json"
    } else {
        Write-Warning "No DAST report found - skipping AI DAST analysis."
        exit 0
    }
}

Write-Host "INFO: Checking AI service at $AiUrl/health ..."
$health = Invoke-RestMethod -Uri "$AiUrl/health" -Method Get -TimeoutSec 30
Write-Host "OK: AI service status: $($health.status) | Groq: $($health.groq)"

$reportPath = (Resolve-Path $ReportFile).Path
$url = ('{0}/api/v1/analyze/dast?max_issues={1}&include_summary=true&include_pdf=true' -f $AiUrl.TrimEnd('/'), $MaxIssues)

Write-Host "INFO: Sending DAST report ($ReportFile) to AI service..."
$raw = & curl.exe -sS -X POST $url -F ("report=@{0};type=application/json" -f $reportPath)
if ($LASTEXITCODE -ne 0) {
    throw "curl failed posting DAST report (exit $LASTEXITCODE)"
}

$response = $raw | ConvertFrom-Json
if (-not $response.findings) {
    throw "AI DAST response missing findings: $raw"
}

@{
    summary = $response.summary
    scanner = $response.scanner
    findings = $response.findings
} | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 "ai_dast_output.json"

$count = @($response.findings).Count
Write-Host "DONE: Saved ai_dast_output.json ($count items)"

if ($response.pdf_base64) {
    [IO.File]::WriteAllBytes("ai_dast_report.pdf", [Convert]::FromBase64String($response.pdf_base64))
    Write-Host "DONE: Saved ai_dast_report.pdf"
}
