param(
    [string]$AiUrl = "http://localhost:8306",
    [int]$MaxWaitSeconds = 120
)

$ErrorActionPreference = "Stop"
$deadline = (Get-Date).AddSeconds($MaxWaitSeconds)

Write-Host "INFO: Waiting for AI service at $AiUrl/health (max ${MaxWaitSeconds}s)..."

while ((Get-Date) -lt $deadline) {
    try {
        $health = Invoke-RestMethod -Uri "$AiUrl/health" -Method Get -TimeoutSec 10
        if ($health.status -eq "ok") {
            Write-Host "OK: AI service ready. Groq: $($health.groq)"
            exit 0
        }
        Write-Host "WAIT: AI status: $($health.status) - $($health.message)"
    } catch {
        Write-Host "WAIT: AI not ready yet: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 5
}

Write-Host "ERROR: AI service not reachable at $AiUrl"
Write-Host "Start it once with: docker compose -f docker-compose.ai.yml up -d --build"
exit 1
