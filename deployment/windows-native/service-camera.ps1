param(
    [string]$RepoPath = "C:\cytocore\CompuCyto"
)

. (Join-Path $PSScriptRoot "service-common.ps1")

$envValues = Read-CytoCoreEnv -RepoPath $RepoPath
Set-CytoCoreProcessEnv -Values $envValues

if ($envValues.ContainsKey("PYTHON_PORT") -and $envValues["PYTHON_PORT"] -ne "") {
    [Environment]::SetEnvironmentVariable("PORT", [string]$envValues["PYTHON_PORT"], "Process")
}

$cameraDir = Join-Path $RepoPath "camera_backend"
$python = Join-Path $cameraDir ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing camera virtual environment. Run deployment\windows-native\update-native.ps1 first."
}

Set-Location -LiteralPath $cameraDir
& $python "main.py"
