param(
    [string]$RepoPath = "C:\cytocore\CompuCyto",
    [string]$RuntimeRoot = "C:\cytocore\runtime",
    [string]$NginxRoot = "C:\nginx",
    [string]$Branch = "",
    [switch]$SkipGitPull,
    [switch]$SkipRestart
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "service-common.ps1")

Set-Location -LiteralPath $RepoPath

if (-not $SkipGitPull) {
    try {
        git rev-parse --is-inside-work-tree *> $null
        $currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
        $targetBranch = if ($Branch) { $Branch } else { $currentBranch }

        if ($targetBranch -and $targetBranch -ne "HEAD") {
            git fetch --prune origin
            git checkout $targetBranch
            git pull --ff-only origin $targetBranch
        }
    }
    catch {
        Write-Warning "Git update failed; continuing with currently checked-out code. $($_.Exception.Message)"
    }
}

$envValues = Read-CytoCoreEnv -RepoPath $RepoPath

$logsDir = Join-Path $RuntimeRoot "logs"
$wwwDir = Join-Path $RuntimeRoot "www"
$nginxDir = Join-Path $RuntimeRoot "nginx"
$mediaDir = Join-Path $RuntimeRoot "media"
New-Item -ItemType Directory -Force $logsDir, $wwwDir, $nginxDir, $mediaDir | Out-Null
New-Item -ItemType Directory -Force (Join-Path $mediaDir "captures"), (Join-Path $mediaDir "videos"), (Join-Path $mediaDir "thumbnails") | Out-Null

Write-Host "Installing frontend dependencies..."
Push-Location (Join-Path $RepoPath "dashboard_frontend")
npm ci
npm run build
Pop-Location

Write-Host "Installing backend dependencies..."
Push-Location (Join-Path $RepoPath "dashboard_backend")
npm ci
npm run build
Pop-Location

Write-Host "Installing camera dependencies..."
$cameraDir = Join-Path $RepoPath "camera_backend"
$cameraPython = Join-Path $cameraDir ".venv\Scripts\python.exe"
Push-Location $cameraDir
if (-not (Test-Path -LiteralPath $cameraPython)) {
    py -3.11 -m venv .venv
}
& $cameraPython -m pip install --upgrade pip
& $cameraPython -m pip install -r requirements.txt
Pop-Location

Write-Host "Publishing frontend..."
if (Test-Path -LiteralPath $wwwDir) {
    Get-ChildItem -LiteralPath $wwwDir -Force | Remove-Item -Recurse -Force
}
Copy-Item -Path (Join-Path $RepoPath "dashboard_frontend\dist\*") -Destination $wwwDir -Recurse -Force

$cameraUpstream = Get-CytoCoreValue -Values $envValues -Name "PYTHON_CAMERA_URL" -Default "http://127.0.0.1:8001"
$piUpstream = Get-CytoCoreValue -Values $envValues -Name "PI_API_UPSTREAM" -Default (Get-CytoCoreValue -Values $envValues -Name "RASPBERRY_PI_URL" -Default "http://192.168.100.1:8000")
$frontendRoot = ($wwwDir -replace "\\", "/")
$nginxMimeTypes = ((Join-Path $NginxRoot "conf\mime.types") -replace "\\", "/")

$template = Get-Content -LiteralPath (Join-Path $PSScriptRoot "nginx-cytocore.conf.template") -Raw
$rendered = $template `
    -replace "__FRONTEND_ROOT__", $frontendRoot `
    -replace "__NGINX_MIME_TYPES__", $nginxMimeTypes `
    -replace "__CAMERA_API_UPSTREAM__", $cameraUpstream.TrimEnd("/") `
    -replace "__PI_API_UPSTREAM__", $piUpstream.TrimEnd("/")

$nginxConf = Join-Path $nginxDir "cytocore.conf"
Set-Content -LiteralPath $nginxConf -Value $rendered -Encoding ascii

if (-not $SkipRestart) {
    foreach ($service in @("CytoCoreCamera", "CytoCoreApi", "CytoCoreNginx")) {
        $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
        if ($svc) {
            Restart-Service -Name $service -Force
        }
    }
}

Write-Host "Native update complete."
