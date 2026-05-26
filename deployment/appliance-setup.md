# CytoCore Native Windows Appliance Setup

This setup runs CytoCore before user login. It does not depend on Docker Desktop.

Runtime layout:

```text
Windows services
  CytoCoreMdns   -> advertises cytocore.local on the LAN
  CytoCoreCamera -> Python FastAPI camera service on 8001
  CytoCoreApi    -> NestJS API on 3000
  CytoCoreNginx  -> Nginx public web server on 80

Windows Scheduled Task
  CytoCore Native Update -> git pull, rebuild, publish frontend, restart services
  CytoCore Console       -> visible status/log console after user login
```

## 1. Install prerequisites

Install these on the Windows appliance:

- Git for Windows
- Node.js LTS
- Python 3.11
- PostgreSQL for Windows
- Nginx for Windows extracted to `C:\nginx`
- NSSM extracted to `C:\nssm\nssm.exe`
- Pixelink SDK/driver for Windows
- Bonjour Print Services for Windows on client PCs, if `cytocore.local` does not resolve there

Rename the Windows PC:

```powershell
Rename-Computer -NewName "cytocore" -Restart
```

After reboot, confirm the Pixelink camera works in Pixelink's own software.

## 2. Clone the repo

```powershell
New-Item -ItemType Directory -Force C:\cytocore
git clone <your-github-repo-url> C:\cytocore\CompuCyto
Set-Location C:\cytocore\CompuCyto
```

## 3. Create the runtime env

```powershell
Copy-Item .env.native.example .env.native
notepad .env.native
```

Set real values for:

```text
DATABASE_USER
DATABASE_PASSWORD
DATABASE_NAME
JWT_SECRET
RASPBERRY_PI_URL
PI_API_UPSTREAM
```

The camera service should stay local:

```text
PYTHON_CAMERA_URL=http://127.0.0.1:8001
```

## 4. Prepare PostgreSQL

Create a PostgreSQL database/user matching `.env.native`.

Example from an elevated PowerShell or psql shell:

```sql
CREATE USER cytocore WITH PASSWORD 'replace-with-a-strong-password';
CREATE DATABASE cytocore OWNER cytocore;
```

PostgreSQL should be installed as a Windows service and set to automatic start.

## 5. Install CytoCore services

Run PowerShell as Administrator:

```powershell
Set-Location C:\cytocore\CompuCyto
powershell -ExecutionPolicy Bypass -File .\deployment\windows-native\install-services.ps1
```

The installer:

- installs frontend/backend/Python dependencies
- builds Vue and NestJS
- publishes Vue to `C:\cytocore\runtime\www`
- renders Nginx config to `C:\cytocore\runtime\nginx\cytocore.conf`
- opens Windows Firewall and discovery for LAN access
- installs Windows services with NSSM
- installs the startup update scheduled task
- installs the logon console scheduled task
- starts all CytoCore services

## 6. Verify

```powershell
Get-Service CytoCoreMdns,CytoCoreCamera,CytoCoreApi,CytoCoreNginx
Invoke-RestMethod http://localhost:8001/health
Invoke-RestMethod http://localhost:3000/api/v1/health
```

Then open:

```text
http://localhost
http://cytocore
http://cytocore.local
http://<machine-ip>
```

If hostname access does not resolve from another computer, test the appliance
IP first. If the IP works but `cytocore` or `cytocore.local` does not, the
remaining issue is LAN name resolution rather than CytoCore.

## Updating

Updates run automatically at Windows startup via `CytoCore Native Update`.

Run an update manually:

```powershell
powershell -ExecutionPolicy Bypass -File C:\cytocore\CompuCyto\deployment\windows-native\update-native.ps1
```

That command:

- pulls latest GitHub changes
- runs `npm ci`
- rebuilds frontend and backend
- updates Python dependencies
- republishes frontend
- restarts `CytoCoreCamera`, `CytoCoreApi`, and `CytoCoreNginx`

## Logs

Logs are written to:

```text
C:\cytocore\runtime\logs
```

Service names:

```text
CytoCoreCamera
CytoCoreApi
CytoCoreNginx
```

When a user logs in, the `CytoCore Console` scheduled task opens a visible
PowerShell window with service status, health checks, and recent logs.

Open it manually:

```powershell
powershell -ExecutionPolicy Bypass -File C:\cytocore\CompuCyto\deployment\windows-native\operator-console.ps1
```

## Uninstall

Run PowerShell as Administrator:

```powershell
powershell -ExecutionPolicy Bypass -File C:\cytocore\CompuCyto\deployment\windows-native\uninstall-services.ps1
```
