param(
    [string]$RuntimeRoot = "C:\cytocore\runtime",
    [int]$RefreshSeconds = 5,
    [int]$LogLines = 14
)

$ErrorActionPreference = "SilentlyContinue"

$logsDir = Join-Path $RuntimeRoot "logs"
$services = @("CytoCoreCamera", "CytoCoreApi", "CytoCoreNginx")
$healthChecks = @(
    @{ Name = "Public web"; Url = "http://localhost" },
    @{ Name = "Main API"; Url = "http://localhost/api/v1/health" },
    @{ Name = "Camera"; Url = "http://localhost:8001/health" }
)

function Write-State {
    param(
        [string]$Label,
        [string]$State
    )

    $color = switch -Regex ($State) {
        "Running|OK|healthy" { "Green"; break }
        "Starting|Pending" { "Yellow"; break }
        default { "Red" }
    }

    Write-Host ("{0,-18} {1}" -f $Label, $State) -ForegroundColor $color
}

function Get-HealthState {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            return "OK"
        }
        return "HTTP $($response.StatusCode)"
    } catch {
        return "DOWN"
    }
}

function Write-RecentLog {
    param(
        [string]$Title,
        [string]$Path
    )

    Write-Host ""
    Write-Host $Title -ForegroundColor Cyan
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host "No log file yet: $Path" -ForegroundColor DarkGray
        return
    }

    $lines = Get-Content -LiteralPath $Path -Tail $LogLines
    if (-not $lines) {
        Write-Host "(empty)" -ForegroundColor DarkGray
        return
    }

    foreach ($line in $lines) {
        Write-Host $line
    }
}

while ($true) {
    Clear-Host
    Write-Host "CytoCore Console" -ForegroundColor White
    Write-Host ("Updated: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) -ForegroundColor DarkGray
    Write-Host ""

    Write-Host "Services" -ForegroundColor Cyan
    foreach ($name in $services) {
        $service = Get-Service -Name $name
        if ($service) {
            Write-State $name $service.Status
        } else {
            Write-State $name "Missing"
        }
    }

    Write-Host ""
    Write-Host "Health" -ForegroundColor Cyan
    foreach ($check in $healthChecks) {
        Write-State $check.Name (Get-HealthState -Url $check.Url)
    }

    Write-RecentLog "Camera errors" (Join-Path $logsDir "camera.err.log")
    Write-RecentLog "API errors" (Join-Path $logsDir "api.err.log")
    Write-RecentLog "Nginx errors" (Join-Path $logsDir "nginx.err.log")
    Write-RecentLog "Camera output" (Join-Path $logsDir "camera.out.log")
    Write-RecentLog "API output" (Join-Path $logsDir "api.out.log")

    Write-Host ""
    Write-Host "Press Ctrl+C to close this console. It will reopen at the next user login." -ForegroundColor DarkGray
    Start-Sleep -Seconds $RefreshSeconds
}
