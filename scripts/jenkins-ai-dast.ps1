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
        Write-Warning "No DAST report found — skipping AI DAST analysis."
        exit 0
    }
}

Write-Host "[*] Checking AI service at $AiUrl/health ..."
$health = Invoke-RestMethod -Uri "$AiUrl/health" -Method Get -TimeoutSec 30
Write-Host "[OK] AI service status: $($health.status) | Groq: $($health.groq)"

Write-Host "[*] Sending DAST report ($ReportFile) to AI service..."
$form = @{
    report = Get-Item -Path $ReportFile
}

$response = Invoke-RestMethod -Uri "$AiUrl/api/v1/analyze/dast?max_issues=$MaxIssues&include_summary=true&include_pdf=true" `
    -Method Post -Form $form -TimeoutSec 600

@{
    summary = $response.summary
    scanner = $response.scanner
    findings = $response.findings
} | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 "ai_dast_output.json"

Write-Host "[+] Saved ai_dast_output.json ($($response.findings.Count) findings)"

if ($response.pdf_base64) {
    [IO.File]::WriteAllBytes("ai_dast_report.pdf", [Convert]::FromBase64String($response.pdf_base64))
    Write-Host "[+] Saved ai_dast_report.pdf"
}
