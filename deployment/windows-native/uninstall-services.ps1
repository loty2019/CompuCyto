param(
    [string]$NssmExe = "C:\nssm\nssm.exe"
)

$ErrorActionPreference = "Stop"

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell window."
}

Unregister-ScheduledTask -TaskName "CytoCore Native Update" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "CytoCore Console" -Confirm:$false -ErrorAction SilentlyContinue

foreach ($service in @("CytoCoreNginx", "CytoCoreApi", "CytoCoreCamera")) {
    if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        if (Test-Path -LiteralPath $NssmExe) {
            & $NssmExe remove $service confirm | Out-Null
        }
    }
}

Write-Host "CytoCore native services removed."
