# CompuCyto Windows Automation Scripts - Summary

## 📦 Created Files

### 1. **setup-windows.bat** - Full Automated Setup
**Purpose**: Complete setup from scratch  
**Use When**: First time installation or fresh Windows install  
**What it does**:
- ✅ Checks for Node.js, Git, PostgreSQL
- ✅ Clones repository from GitHub
- ✅ Creates database
- ✅ Installs all dependencies
- ✅ Creates .env files
- ✅ Runs migrations
- ✅ Creates startup scripts
- ✅ Launches application

**Usage**:
```bash
# Right-click and "Run as Administrator"
setup-windows.bat
```

**Requirements**: Node.js, PostgreSQL, Git already installed

---

### 2. **quick-setup.bat** - Quick Setup
**Purpose**: Fast setup when repo is already cloned  
**Use When**: You already have the code  
**What it does**:
- ✅ Prompts for database credentials
- ✅ Creates database
- ✅ Installs dependencies
- ✅ Creates .env files
- ✅ Runs migrations
- ✅ Creates startup scripts

**Usage**:
```bash
# Double-click to run
quick-setup.bat
```

**Time**: ~3-5 minutes

---

### 3. **start-all.bat** - Launch Application
**Purpose**: Start both backend and frontend  
**Created by**: setup scripts  
**What it does**:
- Opens backend in new terminal
- Opens frontend in new terminal
- Shows URLs for access

**Usage**:
```bash
# Double-click to run
start-all.bat
```

**URLs**:
- Frontend: http://localhost:5173
- Backend: http://localhost:3000

---

### 4. **start-backend.bat** - Launch Backend Only
**Purpose**: Start NestJS backend server  
**Usage**:
```bash
start-backend.bat
```

---

### 5. **start-frontend.bat** - Launch Frontend Only
**Purpose**: Start Vue.js frontend server  
**Usage**:
```bash
start-frontend.bat
```

---

### 6. **maintenance.bat** - System Maintenance Menu
**Purpose**: Common maintenance tasks  
**What it includes**:
1. Start Application
2. Stop Application (kill Node processes)
3. Update Dependencies
4. Reset Database (⚠️ deletes all data)
5. Create Database Backup
6. Run Migrations
7. Clean Install (reinstall node_modules)
8. View Logs
9. Check System Status
0. Exit

**Usage**:
```bash
# Double-click for interactive menu
maintenance.bat
```

**Use for**:
- Killing stuck Node processes
- Updating npm packages
- Resetting development database
- Creating backups before changes
- Troubleshooting installation issues

---

### 7. **WINDOWS_SETUP.md** - Comprehensive Guide
**Purpose**: Complete setup documentation  
**Contents**:
- Prerequisites installation guide
- Setup options comparison
- Troubleshooting section
- Configuration details
- Security notes
- Next steps

---

## 🚀 Quick Start Guide

### For New Users (Fresh Install):

1. **Install Prerequisites**:
   - Node.js: https://nodejs.org/
   - PostgreSQL: https://www.postgresql.org/download/windows/
   - Git: https://git-scm.com/download/win

2. **Download setup-windows.bat** from GitHub

3. **Run as Administrator**:
   - Right-click `setup-windows.bat`
   - Select "Run as Administrator"

4. **Follow prompts** and wait ~10 minutes

5. **Access application** at http://localhost:5173

---

### For Existing Users (Repo Already Cloned):

1. **Run quick setup**:
   ```bash
   quick-setup.bat
   ```

2. **Enter database credentials**

3. **Wait ~5 minutes**

4. **Start application**:
   ```bash
   start-all.bat
   ```

---

## 📋 What Gets Created

After running setup scripts:

```
CompuCyto/
├── Nest/
│   ├── .env                    ← Backend configuration
│   └── node_modules/           ← Dependencies installed
├── frontend-vue/
│   ├── .env                    ← Frontend configuration
│   └── node_modules/           ← Dependencies installed
├── start-all.bat              ← Start both servers
├── start-backend.bat          ← Start backend only
├── start-frontend.bat         ← Start frontend only
└── maintenance.bat            ← Maintenance menu
```

### Backend .env Contents:
```env
NODE_ENV=development
PORT=3000
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=<your-password>
DATABASE_NAME=microscope_db
JWT_SECRET=<generated-secret>
JWT_EXPIRES_IN=7d
```

### Frontend .env Contents:
```env
VITE_API_URL=/api
VITE_WS_URL=ws://localhost:3000/ws
```

---

## 🔧 Common Tasks

### Starting the Application
```bash
start-all.bat
```

### Stopping the Application
```bash
# Option 1: Close terminal windows
# Option 2: Use maintenance menu
maintenance.bat → Option 2
```

### Updating Dependencies
```bash
maintenance.bat → Option 3
```

### Resetting Database (Development)
```bash
maintenance.bat → Option 4
```

### Creating Backup
```bash
maintenance.bat → Option 5
```

### Troubleshooting Installation
```bash
maintenance.bat → Option 9 (Check System Status)
maintenance.bat → Option 7 (Clean Install)
```

---

## 🐛 Troubleshooting

### "Command not found" errors
**Problem**: Node, Git, or PostgreSQL not in PATH  
**Solution**: 
1. Restart Command Prompt after installation
2. Or manually add to PATH in System Environment Variables

### Setup script fails at database creation
**Problem**: Wrong password or PostgreSQL not running  
**Solution**:
1. Check PostgreSQL service is running (Services.msc)
2. Verify password is correct
3. Try connecting with pgAdmin first

### Ports already in use
**Problem**: Another app using 3000 or 5173  
**Solution**:
1. Use `maintenance.bat → Option 2` to kill Node processes
2. Or change ports in .env files

### Dependencies fail to install
**Problem**: Network issues or npm cache  
**Solution**:
```bash
maintenance.bat → Option 7 (Clean Install)
```

---

## 🎯 Workflow Examples

### Daily Development
```bash
1. start-all.bat          # Start servers
2. Code changes...
3. Save files (auto-reload)
4. Close terminals when done
```

### After Git Pull
```bash
cd Nest && npm install
cd ../frontend-vue && npm install
cd ../Nest && npm run migration:run
```

Or use:
```bash
maintenance.bat → Option 3 (Update Dependencies)
maintenance.bat → Option 6 (Run Migrations)
```

### Database Schema Changes
```bash
# Make changes to entities
cd Nest
npm run migration:generate src/database/migrations/YourMigrationName
npm run migration:run
```

### Starting Fresh
```bash
maintenance.bat → Option 4 (Reset Database)
```

---

## 🔒 Security Reminders

### ⚠️ Development Only
These scripts are for **development environments only**.

### For Production:
- ❌ Do NOT use these scripts
- ❌ Do NOT use default secrets
- ✅ Use proper environment variables
- ✅ Use strong, unique passwords
- ✅ Enable HTTPS
- ✅ Configure firewall rules
- ✅ Use environment-specific configs

---

## 📚 Additional Resources

- **Full Setup Guide**: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **Quick Start**: [Documentation/QUICKSTART.md](Documentation/QUICKSTART.md)
- **API Docs**: [Documentation/API_DOCUMENTATION.md](Documentation/API_DOCUMENTATION.md)
- **Architecture**: [Documentation/HOW_VUE_TALKS_TO_NEST.md](Documentation/HOW_VUE_TALKS_TO_NEST.md)

---

## 🎓 Script Details

### Technologies Used:
- **Batch scripting** for Windows automation
- **PostgreSQL CLI** (`psql`, `pg_dump`) for database operations
- **npm** for dependency management
- **Git** for repository cloning

### Design Principles:
- ✅ User-friendly prompts
- ✅ Error checking at each step
- ✅ Colored output for readability
- ✅ Default values for common options
- ✅ Confirmation for destructive operations
- ✅ Helpful error messages

---

## 🤝 Contributing

If you improve these scripts:
1. Test on fresh Windows installation
2. Update this documentation
3. Submit a PR with clear description

---

**Questions?** Check [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed help!
