param(
    [string]$RepoPath = "C:\cytocore\CompuCyto",
    [string]$RuntimeRoot = "C:\cytocore\runtime",
    [string]$NssmExe = "C:\nssm\nssm.exe",
    [string]$NginxExe = "C:\nginx\nginx.exe",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell window."
}

if (-not (Test-Path -LiteralPath $NssmExe)) {
    throw "NSSM was not found at $NssmExe. Install NSSM and rerun this script."
}

if (-not (Test-Path -LiteralPath $NginxExe)) {
    throw "Nginx was not found at $NginxExe. Install Nginx for Windows and rerun this script."
}

$envFile = Join-Path $RepoPath ".env.native"
if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath (Join-Path $RepoPath ".env.native.example") -Destination $envFile
    Write-Warning "Created .env.native. Edit it with production credentials, then rerun this script."
    notepad $envFile
    exit 1
}

New-Item -ItemType Directory -Force $RuntimeRoot, (Join-Path $RuntimeRoot "logs") | Out-Null
$nginxRoot = Split-Path -Parent (Split-Path -Parent $NginxExe)

& (Join-Path $PSScriptRoot "update-native.ps1") `
    -RepoPath $RepoPath `
    -RuntimeRoot $RuntimeRoot `
    -NginxRoot $nginxRoot `
    -Branch $Branch `
    -SkipGitPull `
    -SkipRestart

$logsDir = Join-Path $RuntimeRoot "logs"
$powershell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$apiScript = Join-Path $PSScriptRoot "service-api.ps1"
$cameraScript = Join-Path $PSScriptRoot "service-camera.ps1"
$nginxConf = Join-Path $RuntimeRoot "nginx\cytocore.conf"

function Install-NssmService {
    param(
        [string]$Name,
        [string]$Application,
        [string]$Arguments,
        [string]$Directory,
        [string]$Stdout,
        [string]$Stderr
    )

    $existing = Get-Service -Name $Name -ErrorAction SilentlyContinue
    if ($existing) {
        & $NssmExe stop $Name | Out-Null
        & $NssmExe remove $Name confirm | Out-Null
    }

    & $NssmExe install $Name $Application $Arguments | Out-Null
    & $NssmExe set $Name AppDirectory $Directory | Out-Null
    & $NssmExe set $Name AppStdout $Stdout | Out-Null
    & $NssmExe set $Name AppStderr $Stderr | Out-Null
    & $NssmExe set $Name AppRotateFiles 1 | Out-Null
    & $NssmExe set $Name AppRotateOnline 1 | Out-Null
    & $NssmExe set $Name AppRotateBytes 10485760 | Out-Null
    & $NssmExe set $Name Start SERVICE_AUTO_START | Out-Null
}

Install-NssmService `
    -Name "CytoCoreCamera" `
    -Application $powershell `
    -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$cameraScript`" -RepoPath `"$RepoPath`"" `
    -Directory $RepoPath `
    -Stdout (Join-Path $logsDir "camera.out.log") `
    -Stderr (Join-Path $logsDir "camera.err.log")

Install-NssmService `
    -Name "CytoCoreApi" `
    -Application $powershell `
    -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$apiScript`" -RepoPath `"$RepoPath`"" `
    -Directory $RepoPath `
    -Stdout (Join-Path $logsDir "api.out.log") `
    -Stderr (Join-Path $logsDir "api.err.log")

Install-NssmService `
    -Name "CytoCoreNginx" `
    -Application $NginxExe `
    -Arguments "-p `"$nginxRoot`" -c `"$nginxConf`"" `
    -Directory (Split-Path -Parent $NginxExe) `
    -Stdout (Join-Path $logsDir "nginx.out.log") `
    -Stderr (Join-Path $logsDir "nginx.err.log")

$updateAction = New-ScheduledTaskAction `
    -Execute $powershell `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\update-native.ps1`" -RepoPath `"$RepoPath`" -RuntimeRoot `"$RuntimeRoot`" -NginxRoot `"$nginxRoot`" -Branch `"$Branch`""

$updateTrigger = New-ScheduledTaskTrigger -AtStartup
$updateSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName "CytoCore Native Update" `
    -Action $updateAction `
    -Trigger $updateTrigger `
    -Settings $updateSettings `
    -Description "Pull latest CytoCore updates, rebuild, and restart native services" `
    -RunLevel Highest `
    -Force | Out-Null

Start-Service CytoCoreCamera
Start-Service CytoCoreApi
Start-Service CytoCoreNginx

Write-Host "CytoCore native services installed and started."
