# Database Configuration - Updated for CompuCyto

## ✅ Updated Autonomous Setup

The `autonomous-setup-windows.bat` script now automatically creates the PostgreSQL database with credentials that **exactly match** your `.env` file!

## 🔐 Default Credentials (Out-of-the-Box)

The script now creates:

```properties
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=compucyto
DATABASE_PASSWORD=bioreactor
DATABASE_NAME=microscope_db
```

These match your existing `.env` configuration **perfectly**, so everything works immediately without any manual configuration!

## 🚀 What the Script Does

### Step 1: Creates PostgreSQL User
```sql
CREATE USER compucyto WITH PASSWORD 'bioreactor';
```

### Step 2: Creates Database
```sql
CREATE DATABASE microscope_db OWNER compucyto;
```

### Step 3: Grants Privileges
```sql
GRANT ALL PRIVILEGES ON DATABASE microscope_db TO compucyto;
```

### Step 4: Tests Connection
```bash
psql -U compucyto -d microscope_db -c "SELECT 1;"
```

### Step 5: Creates .env File
Creates `Nest/.env` with all your existing configuration:
- Database credentials (compucyto/bioreactor)
- JWT secret (your exact secret key)
- External service URLs
- Redis configuration
- Server configuration
- CORS settings
- File storage paths
- Safety limits
- Sensor polling
- Temperature thresholds

## 📋 Complete .env File Created

The script now creates this **exact** `.env` file:

```properties
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=compucyto
DATABASE_PASSWORD=bioreactor
DATABASE_NAME=microscope_db

# JWT Configuration
JWT_SECRET=4f8b3c2d1e6a7b8c9d0a1b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5b6
JWT_EXPIRES_IN=15d

# External Services
PYTHON_CAMERA_URL=http://localhost:8001
RASPBERRY_PI_URL=http://raspberrypi.local:5000
SERVICE_TIMEOUT=30000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Server Configuration
PORT=3000
NODE_ENV=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File Storage
IMAGES_PATH=./images
THUMBNAILS_PATH=./thumbnails

# Safety Limits (motor steps)
MAX_X_POSITION=10000
MAX_Y_POSITION=10000
MAX_Z_POSITION=5000
MIN_X_POSITION=0
MIN_Y_POSITION=0
MIN_Z_POSITION=0

# Sensor Polling Configuration
SENSOR_POLL_INTERVAL=5000
SENSOR_POLL_INTERVAL_MOVING=1000

# Temperature Thresholds (Celsius)
TEMP_WARNING_THRESHOLD=40
TEMP_CRITICAL_THRESHOLD=45
```

## ✨ Benefits

1. **Zero Manual Configuration**: Script creates everything automatically
2. **Exact Match**: Credentials match your `.env` perfectly
3. **Works Immediately**: No need to edit any files
4. **Secure Setup**: Proper user with limited privileges (not postgres superuser)
5. **Database Ownership**: `compucyto` user owns the database
6. **Proper Permissions**: All required privileges granted
7. **Complete Configuration**: All settings from your `.env` included

## 🔄 Smart Detection

The script is smart:
- ✅ Detects if user `compucyto` already exists → updates password
- ✅ Detects if database `microscope_db` exists → updates ownership
- ✅ Tests connection before proceeding
- ✅ Shows clear error messages if anything fails

## 🎯 Usage

Just run the script - no input needed for database setup:

```batch
autonomous-setup-windows.bat
```

The script will:
1. Install PostgreSQL (if needed)
2. Create user `compucyto` with password `bioreactor`
3. Create database `microscope_db` owned by `compucyto`
4. Grant all privileges
5. Create `.env` with your exact configuration
6. Run migrations
7. Ready to go!

## 🐛 Troubleshooting

### If database creation fails:

The script requires the `postgres` superuser password. Default is `postgres123`.

**Manual fix if needed:**
```bash
# Connect as postgres superuser
psql -U postgres

# Create user
CREATE USER compucyto WITH PASSWORD 'bioreactor';

# Create database
CREATE DATABASE microscope_db OWNER compucyto;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE microscope_db TO compucyto;

# Test connection
\c microscope_db compucyto
```

### Verify Setup:

```bash
# Check user exists
psql -U postgres -c "\du"

# Check database exists
psql -U postgres -c "\l"

# Test connection
psql -U compucyto -d microscope_db -c "SELECT 1;"
```

## 🎉 Result

After running the script, you have:
- ✅ PostgreSQL user: `compucyto`
- ✅ Database: `microscope_db`
- ✅ Proper ownership and privileges
- ✅ `.env` file with exact configuration
- ✅ Database migrations run
- ✅ Ready to start the application!

**No manual configuration needed!** 🚀
