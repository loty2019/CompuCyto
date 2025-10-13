# CompuCyto Advanced Maintenance System

## 🎯 Overview

The enhanced `maintenance.bat` script provides comprehensive system management, monitoring, and automation capabilities for CompuCyto.

## 🚀 Features

### 📱 Application Control
- **Start Application** - Launch both backend and frontend
- **Stop Application** - Gracefully stop all services
- **Restart Application** - Quick restart without manual intervention
- **Background Health Monitor** - Automatic service recovery

### 🔄 Repository Management
- **Update Repository** - Pull latest changes from GitHub
- **Check for Updates** - See what's new before updating
- **View Git Status** - Check current branch and changes
- **Commit and Push** - Easy version control

### 📦 Dependency Management
- **Update Dependencies** - npm update for both projects
- **Install Missing Dependencies** - Fix broken installations
- **Clean Install** - Fresh dependency installation
- **Audit Security** - Check for vulnerabilities

### 💾 Database Operations
- **Run Migrations** - Apply schema changes
- **Create Backup** - Save database snapshots
- **Reset Database** - Start fresh (development)
- **Restore from Backup** - Recover previous state

### 🔍 System Diagnostics
- **Full Health Check** - Comprehensive system test
- **Check Processes** - View running services
- **View Logs** - Access application logs
- **Test Database** - Verify connectivity
- **Test API** - Endpoint health checks

### 🛠️ Utilities
- **Clear Cache** - Clean npm and build caches
- **Fix Permissions** - Reset file attributes
- **Generate Report** - Detailed system report
- **Open in VS Code** - Quick IDE launch

---

## 🔥 Key Feature: Background Health Monitor

### What It Does
Automatically monitors your application and **restarts crashed services**.

### How to Use
1. Run `maintenance.bat`
2. Select option **4** (Start Background Health Monitor)
3. Monitor window opens in background

### Monitoring Features
- ✅ Checks backend health every 30 seconds
- ✅ Checks frontend health every 30 seconds
- ✅ Checks database connectivity
- ✅ Auto-restarts if service crashes
- ✅ Runs in dedicated window
- ✅ Displays realtime status

### Example Output
```
============================================================
CompuCyto Health Monitor - Running
============================================================
Time: 10/13/2025 14:30:45

[Checking Backend...]
Backend: ✓ HEALTHY

[Checking Frontend...]
Frontend: ✓ HEALTHY

[Checking Database...]
Database: ✓ HEALTHY

Next check in 30 seconds... (Press Ctrl+C to stop)
============================================================
```

### Auto-Recovery
If a service crashes:
```
[WARNING] Backend is DOWN
[INFO] Attempting to restart backend...
[Starting] CompuCyto Backend Recovery window opened
```

---

## 🔄 Repository Auto-Update

### Update Repository (Option 5)
```batch
Current branch: master
Fetching latest changes...
Pulling latest changes...
[OK] Repository updated successfully!

Install updated dependencies? (y/n): y
Installing backend dependencies...
Installing frontend dependencies...
[OK] Dependencies updated

Run database migrations? (y/n): y
[OK] Migrations complete
```

### Check for Updates (Option 6)
```batch
Fetching from remote...
Current branch: master

Commits behind remote: 3

Latest remote commits:
a1b2c3d Fix database connection issue
d4e5f6g Add new microscope features
g7h8i9j Update documentation
```

### Workflow
1. **Check for updates** (Option 6) - See what's new
2. **Review changes** - Read commit messages
3. **Update repository** (Option 5) - Pull changes
4. **Auto-install deps** - Script handles dependencies
5. **Auto-run migrations** - Database stays in sync

---

## 💾 Database Management

### Create Backup (Option 14)
```batch
Creating database backup...
[OK] Backup created: backups\backup_microscope_db_20251013_143045.sql
```

Backups saved in `CompuCyto/backups/` folder with timestamp.

### Restore from Backup (Option 16)
```batch
Available backups:
backup_microscope_db_20251013_143045.sql
backup_microscope_db_20251012_090000.sql

Enter backup filename: backup_microscope_db_20251013_143045.sql
Restoring from: backups\backup_microscope_db_20251013_143045.sql
[OK] Database restored successfully!
```

### Reset Database (Option 15)
```batch
WARNING: This will DELETE ALL DATA!
Are you sure? Type YES to continue: YES

Dropping database...
Creating database...
Running migrations...
[OK] Database reset complete
```

---

## 🔍 Diagnostics

### Full Health Check (Option 17)
```batch
[1/8] Node.js Installation
✓ Node.js OK (v20.10.0)

[2/8] npm Installation  
✓ npm OK (v10.2.3)

[3/8] PostgreSQL Installation
✓ PostgreSQL OK (v16.1)

[4/8] Git Installation
✓ Git OK (v2.42.0)

[5/8] Backend Dependencies
✓ Backend dependencies installed

[6/8] Frontend Dependencies
✓ Frontend dependencies installed

[7/8] Backend Running
✓ Backend is running (port 3000)

[8/8] Frontend Running
✓ Frontend is running (port 5173)

[9/8] Database Connection
✓ Database connection OK
```

### Test API Endpoints (Option 21)
```batch
Testing Backend Health...
{"status":"ok","timestamp":"2025-10-13T14:30:45.123Z"}

Testing Backend API...
{"message":"CompuCyto API v1.0","docs":"/api/docs"}

Testing Frontend...
HTTP/1.1 200 OK
```

### Generate System Report (Option 24)
Creates timestamped report file with:
- System information
- Software versions
- Git status
- Running processes
- Port usage
- Component status
- Configuration status

---

## 📋 Common Workflows

### Daily Development
```
1. Run maintenance.bat
2. Option 4: Start Health Monitor
3. Option 1: Start Application
4. Develop...
5. Health monitor auto-recovers crashes
6. Option 2: Stop when done
```

### Pull Latest Updates
```
1. Option 6: Check for Updates
2. Review commits
3. Option 5: Update Repository
4. Auto-installs dependencies
5. Auto-runs migrations
6. Option 3: Restart Application
```

### After Making Changes
```
1. Option 8: Commit and Push
2. Enter commit message
3. Changes pushed to GitHub
```

### Troubleshooting Issues
```
1. Option 17: Full Health Check
2. Review results
3. If dependencies broken: Option 11 (Clean Install)
4. If database issues: Option 20 (Test DB Connection)
5. If API issues: Option 21 (Test API)
6. Option 24: Generate System Report (for support)
```

### Preparing for Production
```
1. Option 14: Create Database Backup
2. Option 12: Audit Dependencies
3. Fix vulnerabilities
4. Option 8: Commit and Push
5. Option 17: Full Health Check
```

---

## 🎨 Menu Organization

### Application Control (1-4)
Quick access to start/stop/restart services and monitoring

### Repository Management (5-8)
Git operations for keeping code up to date

### Dependency Management (9-12)
npm operations for managing packages

### Database Operations (13-16)
Database maintenance and backups

### System Diagnostics (17-21)
Health checks and testing

### Utilities (22-25)
Misc tools and helpers

---

## 🔧 Configuration

### Database Credentials
Hardcoded to match your `.env`:
```batch
DB_USER=compucyto
DB_PASSWORD=bioreactor  
DB_NAME=microscope_db
```

### Health Monitor
- Check interval: 30 seconds
- Auto-restart: Enabled
- Services monitored: Backend, Frontend, Database

### Backup Location
```
CompuCyto/backups/
```

---

## 🚨 Safety Features

### Confirmations
- Database reset requires typing "YES"
- Clean install asks for confirmation
- Commit and push shows changes first

### Backups
- Timestamped backup files
- Never overwrites existing backups
- Easy to restore any backup

### Error Handling
- Clear error messages
- Graceful failures
- Helpful troubleshooting hints

---

## 💡 Pro Tips

1. **Keep health monitor running** during development
2. **Check for updates** at start of each day
3. **Create backups** before major database changes
4. **Use system report** when asking for help
5. **Clean install** fixes most dependency issues
6. **Audit dependencies** regularly for security

---

## 🤖 Automation Potential

### Current Capabilities
- Auto-restart crashed services
- Auto-install dependencies after git pull
- Auto-run migrations after update
- Auto-detect system issues

### Future Enhancements
Could add:
- Scheduled automatic backups
- Auto-update on schedule
- Email/SMS alerts on crashes
- Performance monitoring
- Auto-scaling
- Log rotation

---

## 📊 System Requirements

- **Windows 10/11**
- **PowerShell** (for health monitor)
- **curl** (for API testing)
- **Git** (for repo management)
- **Admin rights** (for some operations)

---

## 🆘 Troubleshooting

### Health Monitor Won't Start
**Solution**: Ensure curl is installed
```batch
curl --version
```

### Git Commands Fail
**Solution**: Check Git installation
```batch
git --version
```

### Database Operations Fail
**Solution**: Verify PostgreSQL is running
```batch
services.msc → postgresql-x64-16 → Start
```

### Can't Find Backups
**Solution**: Check backups folder
```batch
dir backups
```

---

## 📚 Related Documentation

- `AUTONOMOUS_SETUP_README.md` - Initial setup
- `DATABASE_SETUP.md` - Database configuration
- `WINDOWS_AUTOMATION_GUIDE.md` - All scripts reference

---

**The maintenance.bat script is your one-stop shop for all CompuCyto system management! 🚀**
