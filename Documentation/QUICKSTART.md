# Quick Start Guide - CompuCyto NestJS Backend

## Step 1: Install Dependencies

### Option A: Using the install script (CMD)
```cmd
install.bat
```

### Option B: Using PowerShell
```powershell
.\install.ps1
```

### Option C: Manual installation
```bash
npm install
```

If you encounter PowerShell execution policy errors, use the batch file or run in CMD.

---

## Step 2: Configure Environment

The `.env` file has been created from `.env.example`. Edit it with your settings:

```bash
# Open .env in notepad
notepad .env
```

**Important settings to update:**
- `DATABASE_PASSWORD` - Your PostgreSQL password
- `JWT_SECRET` - A strong random string (minimum 32 characters)
- `PYTHON_CAMERA_URL` - URL of your Python camera service
- `RASPBERRY_PI_URL` - URL of your Raspberry Pi controller

---

## Step 3: Setup PostgreSQL Database

### Install PostgreSQL (if not installed)
Download from: https://www.postgresql.org/download/windows/

### Create Database

Option 1 - Using psql:
```bash
psql -U postgres
```

Then in psql:
```sql
CREATE DATABASE microscope_db;
\q
```

Option 2 - Using pgAdmin:
1. Open pgAdmin
2. Right-click "Databases" → Create → Database
3. Name: `microscope_db`
4. Click Save

---

## Step 4: Start the Backend

### Development Mode (with auto-reload)
```bash
npm run start:dev
```

### Production Mode
```bash
npm run build
npm run start:prod
```

The server will start on `http://localhost:3000`

---

## Step 5: Verify Installation

### Check Health Endpoint

Open your browser or use curl:
```bash
curl http://localhost:3000/api/v1/health
```

You should see:
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "pythonCamera": false,
    "raspberryPi": false,
    "redis": true
  },
  "timestamp": "2025-10-09T..."
}
```

**Note:** `pythonCamera` and `raspberryPi` will be `false` until those services are running.

---

## Step 6: Test Authentication

### Register a User

Using curl:
```bash
curl -X POST http://localhost:3000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@test.com\",\"username\":\"testuser\",\"password\":\"password123\"}"
```

Using PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/register" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email":"test@test.com","username":"testuser","password":"password123"}'
```

You should receive a JWT token in the response.

### Login

```bash
curl -X POST http://localhost:3000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@test.com\",\"password\":\"password123\"}"
```

Save the `access_token` from the response for authenticated requests.

---

## Step 7: Connect Frontend

### Update Frontend .env

In your Vue frontend (`frontend-vue/.env` or `.env.local`):
```env
VITE_API_URL=http://localhost:3000/api/v1
```

### Start Frontend

```bash
cd ../frontend-vue
npm install
npm run dev
```

The frontend will connect to the backend at `http://localhost:3000/api/v1`

---

## Common Issues

### Issue: "Cannot connect to database"

**Solution:**
1. Check PostgreSQL is running:
   ```bash
   pg_isready
   ```
2. Verify database credentials in `.env`
3. Ensure database `microscope_db` exists

---

### Issue: "PowerShell script execution disabled"

**Solution:**
Use the batch file instead:
```cmd
install.bat
```

Or enable scripts (run PowerShell as Administrator):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue: "Camera service unavailable (503)"

**Solution:**
This is normal if Python camera service isn't running yet. The backend will still work for authentication and other features.

To start camera service (when ready):
```bash
cd backend-python
python camera_service.py
```

---

### Issue: "Stage controller unavailable (503)"

**Solution:**
This is normal if Raspberry Pi isn't connected or not running the motor controller service.

Verify Raspberry Pi is accessible:
```bash
ping raspberrypi.local
```

---

### Issue: Port 3000 already in use

**Solution:**
Change the port in `.env`:
```env
PORT=3001
```

Then restart the backend.

---

## Next Steps

1. **Read API Documentation**: See `API_DOCUMENTATION.md` for all available endpoints
2. **Setup External Services**: 
   - Python camera service (port 8001)
   - Raspberry Pi motor controller (port 5000)
3. **Test with Frontend**: Open `http://localhost:5173` (frontend dev server)
4. **Review Specification**: See `NESTJS_BACKEND_SPECIFICATION.md` for full details

---

## Development Commands

```bash
# Start development server (auto-reload)
npm run start:dev

# Build for production
npm run build

# Run production build
npm run start:prod

# Run tests
npm run test

# Format code
npm run format

# Lint code
npm run lint
```

---

## Project Status

### ✅ Phase 1 - Complete
- ✅ Configuration module
- ✅ Database setup (TypeORM + PostgreSQL)
- ✅ User authentication (JWT)
- ✅ Camera control (proxy to Python service)
- ✅ Stage control (proxy to Raspberry Pi)
- ✅ Position validation
- ✅ Health checks

### 🚧 Phase 2 - Coming Soon
- Images module (database + file management)
- Jobs module (timelapse, grid scan, z-stack)
- Positions module (saved positions)
- WebSocket gateway (real-time updates)
- Bull queue (job processing)

### 📅 Phase 3 - Future
- Sensors module
- System logging
- Advanced features

---

## Support

- **API Docs**: `API_DOCUMENTATION.md`
- **Setup Guide**: `SETUP.md`
- **Full Spec**: `NESTJS_BACKEND_SPECIFICATION.md`

For issues, check the troubleshooting sections in these documents.
