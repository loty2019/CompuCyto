param(
    [string]$RepoPath = "C:\cytocore\CompuCyto",
    [string]$RuntimeRoot = "C:\cytocore\runtime"
)

$ErrorActionPreference = "Stop"

$mdnsRoot = Join-Path $RuntimeRoot "mdns"
$venv = Join-Path $mdnsRoot ".venv"
$python = Join-Path $venv "Scripts\python.exe"
$advertiser = Join-Path $PSScriptRoot "mdns-advertise.py"

New-Item -ItemType Directory -Force $mdnsRoot | Out-Null

if (-not (Test-Path -LiteralPath $python)) {
    & py -3 -m venv $venv
}

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$importOutput = & $python -c "import zeroconf" 2>&1
$importExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

if ($importExitCode -ne 0) {
    & $python -m pip install --upgrade pip
    & $python -m pip install zeroconf
}

$addresses = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object {
        $_.InterfaceAlias -in @("Wi-Fi", "Ethernet") -and
        $_.IPAddress -notlike "169.254*" -and
        $_.IPAddress -ne "127.0.0.1"
    } |
    Sort-Object InterfaceAlias |
    Select-Object -ExpandProperty IPAddress

if (-not $addresses) {
    throw "No Wi-Fi or Ethernet IPv4 address found for mDNS advertisement."
}

$args = @(
    $advertiser,
    "--hostname", "cytocore.local.",
    "--service-name", "CytoCore._http._tcp.local.",
    "--port", "80"
)

foreach ($address in $addresses) {
    $args += @("--address", $address)
}

& $python @args
