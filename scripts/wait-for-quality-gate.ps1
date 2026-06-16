param(
    [string]$SonarUrl = "http://localhost:9500",
    [string]$ProjectKey = "devsecops-app",
    [string]$SonarToken = $env:SONAR_TOKEN,
    [int]$MaxWaitMinutes = 15
)

$ErrorActionPreference = "Stop"

if (-not $SonarToken) {
    throw "SONAR_TOKEN is not set."
}

$deadline = (Get-Date).AddMinutes($MaxWaitMinutes)
$ceTaskId = $null
$reportTaskFile = ".scannerwork\report-task.txt"

if (Test-Path $reportTaskFile) {
    $lines = Get-Content $reportTaskFile
    foreach ($line in $lines) {
        if ($line -match '^ceTaskId=(.+)$') {
            $ceTaskId = $Matches[1].Trim()
            break
        }
    }
}

Write-Host "INFO: Waiting for SonarQube analysis (max ${MaxWaitMinutes} min)..."
if ($ceTaskId) {
    Write-Host "INFO: CE task id: $ceTaskId"
}

$headers = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${SonarToken}:")))" }

while ((Get-Date) -lt $deadline) {
    if ($ceTaskId) {
        $task = Invoke-RestMethod -Uri "$SonarUrl/api/ce/task?id=$ceTaskId" -Headers $headers -TimeoutSec 30
        $status = $task.task.status
        Write-Host "WAIT: CE task status: $status"
        if ($status -eq "FAILED") {
            throw "SonarQube analysis task failed."
        }
        if ($status -ne "SUCCESS") {
            Start-Sleep -Seconds 10
            continue
        }
    }

    try {
        $qg = Invoke-RestMethod -Uri "$SonarUrl/api/qualitygates/project_status?projectKey=$ProjectKey" -Headers $headers -TimeoutSec 30
        $gateStatus = $qg.projectStatus.status
        Write-Host "INFO: Quality gate status: $gateStatus"

        $qg | ConvertTo-Json -Depth 10 | Out-File -Encoding utf8 "quality-gate-result.json"

        if ($gateStatus -eq "OK") {
            Write-Host "OK: Quality gate passed."
            exit 0
        }
        if ($gateStatus -in @("ERROR", "WARN")) {
            Write-Host "WARN: Quality gate returned $gateStatus (see quality-gate-result.json)."
            exit 1
        }
    } catch {
        Write-Host "WAIT: Quality gate not ready yet: $($_.Exception.Message)"
    }

    Start-Sleep -Seconds 10
}

throw "Quality gate did not complete within ${MaxWaitMinutes} minutes."
