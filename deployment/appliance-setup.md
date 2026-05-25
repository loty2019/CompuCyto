# CytoCore Windows Appliance Setup

Use this on the Windows machine that will host CytoCore.

## 1. Install prerequisites

Install:

- Git for Windows
- Docker Desktop with Linux containers enabled
- Bonjour Print Services for Windows, if `cytocore.local` does not resolve on your LAN

Rename the Windows PC to `cytocore`:

```powershell
Rename-Computer -NewName "cytocore" -Restart
```

After reboot, make sure Docker Desktop is running.

## 2. Clone the repo

Open PowerShell:

```powershell
New-Item -ItemType Directory -Force C:\cytocore
git clone <your-github-repo-url> C:\cytocore\CompuCyto
Set-Location C:\cytocore\CompuCyto
```

## 3. Create the appliance env

```powershell
Copy-Item .env.appliance.example .env
notepad .env
```

Set `PI_API_UPSTREAM` to the separate Pi API device URL. For example:

```text
PI_API_UPSTREAM=http://192.168.100.1:8000
```

## 4. Start the stack

```powershell
docker compose up -d --build
docker compose ps
```

The app is served on one public port:

```text
http://cytocore.local
http://cytocore
http://<machine-ip>
```

If port 80 is blocked, allow Docker Desktop through Windows Firewall and make
sure no other Windows service is already using port 80.

## 5. Auto-start and auto-update on boot/login

This creates a Windows Scheduled Task. It runs the PowerShell startup helper,
pulls the latest GitHub changes, then starts Docker Compose.

Run PowerShell as Administrator:

```powershell
$Action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\cytocore\CompuCyto\deployment\cytocore-start.ps1"

$Trigger = New-ScheduledTaskTrigger -AtLogOn

$Settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable

Register-ScheduledTask `
  -TaskName "CytoCore Appliance" `
  -Action $Action `
  -Trigger $Trigger `
  -Settings $Settings `
  -Description "Pull latest CytoCore and start Docker Compose" `
  -RunLevel Highest `
  -Force
```

To run it manually:

```powershell
Start-ScheduledTask -TaskName "CytoCore Appliance"
```

To see logs:

```powershell
Set-Location C:\cytocore\CompuCyto
docker compose logs -f
```

## Routes

Internal routes:

```text
/api        -> NestJS
/python-api -> camera FastAPI
/pi-api     -> external Pi API device
```

## Linux note

The Linux systemd files are still in `deployment/` for a future Linux appliance,
but they are not used on the Windows host.
