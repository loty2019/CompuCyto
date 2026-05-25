$ErrorActionPreference = "Stop"

$AppDir = if ($env:APP_DIR) { $env:APP_DIR } else { "C:\cytocore\CompuCyto" }
$Branch = if ($env:CYTOCORE_BRANCH) { $env:CYTOCORE_BRANCH } else { "" }

Set-Location -LiteralPath $AppDir

try {
    git rev-parse --is-inside-work-tree *> $null
    $CurrentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
    $TargetBranch = if ($Branch) { $Branch } else { $CurrentBranch }

    if ($TargetBranch -and $TargetBranch -ne "HEAD") {
        git fetch --prune origin
        git checkout $TargetBranch
        git pull --ff-only origin $TargetBranch
    }
}
catch {
    Write-Warning "Git update failed; starting the currently checked-out code. $($_.Exception.Message)"
}

$DockerReady = $false
for ($Attempt = 1; $Attempt -le 60; $Attempt++) {
    try {
        docker info *> $null
        $DockerReady = $true
        break
    }
    catch {
        Start-Sleep -Seconds 5
    }
}

if (-not $DockerReady) {
    throw "Docker did not become ready after 5 minutes."
}

docker compose up -d --build --remove-orphans
