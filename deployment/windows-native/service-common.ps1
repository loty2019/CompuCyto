$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $OutputEncoding
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "Process")
[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "Process")
[Environment]::SetEnvironmentVariable("NO_COLOR", "1", "Process")

function Read-CytoCoreEnv {
    param(
        [string]$RepoPath
    )

    $envFile = Join-Path $RepoPath ".env.native"
    if (-not (Test-Path -LiteralPath $envFile)) {
        $envFile = Join-Path $RepoPath ".env"
    }

    if (-not (Test-Path -LiteralPath $envFile)) {
        throw "Missing runtime env file. Copy .env.native.example to .env.native and edit it."
    }

    $values = @{}
    Get-Content -LiteralPath $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }

        $parts = $line -split "=", 2
        $values[$parts[0].Trim()] = $parts[1]
    }

    return $values
}

function Set-CytoCoreProcessEnv {
    param(
        [hashtable]$Values
    )

    foreach ($key in $Values.Keys) {
        [Environment]::SetEnvironmentVariable($key, [string]$Values[$key], "Process")
    }
}

function Get-CytoCoreValue {
    param(
        [hashtable]$Values,
        [string]$Name,
        [string]$Default = ""
    )

    if ($Values.ContainsKey($Name) -and $Values[$Name] -ne "") {
        return [string]$Values[$Name]
    }

    return $Default
}
