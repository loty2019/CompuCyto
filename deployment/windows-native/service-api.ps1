param(
    [string]$RepoPath = "C:\cytocore\CompuCyto"
)

. (Join-Path $PSScriptRoot "service-common.ps1")

$envValues = Read-CytoCoreEnv -RepoPath $RepoPath
Set-CytoCoreProcessEnv -Values $envValues

Set-Location -LiteralPath (Join-Path $RepoPath "dashboard_backend")
& node "dist/main"
