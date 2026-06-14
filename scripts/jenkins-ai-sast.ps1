param(
    [string]$AiUrl = "http://localhost:8506",
    [string]$ReportFile = "sonar-report.json",
    [int]$MaxIssues = 10
)

$ErrorActionPreference = "Stop"

Write-Host "[*] Checking AI service at $AiUrl/health ..."
$health = Invoke-RestMethod -Uri "$AiUrl/health" -Method Get -TimeoutSec 30
Write-Host "[OK] AI service status: $($health.status) | Groq: $($health.groq)"

if (-not (Test-Path $ReportFile)) {
    throw "Report file not found: $ReportFile"
}

Write-Host "[*] Sending SAST report to AI service..."
$form = @{
    report = Get-Item -Path $ReportFile
    max_issues = $MaxIssues
    include_summary = "true"
    include_pdf = "true"
}

$response = Invoke-RestMethod -Uri "$AiUrl/api/v1/analyze/sast?max_issues=$MaxIssues&include_summary=true&include_pdf=true" `
    -Method Post -Form $form -TimeoutSec 600

$output = @{
    summary = $response.summary
    findings = $response.findings
}
$output | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 "ai_sast_output.json"
Write-Host "[+] Saved ai_sast_output.json ($($response.findings.Count) findings)"

if ($response.pdf_base64) {
    [IO.File]::WriteAllBytes("ai_sast_report.pdf", [Convert]::FromBase64String($response.pdf_base64))
    Write-Host "[+] Saved ai_sast_report.pdf"
}
