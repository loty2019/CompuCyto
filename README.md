# CompuCyto - Microscopy Control System

Full-stack microscopy automation platform with Vue.js frontend, NestJS backend, and Python camera service.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Vue 3 Frontend                         │
│              (Vite + TypeScript + Tailwind)             │
│                   Port: 5173                            │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                  NestJS Backend                         │
│            (TypeScript + TypeORM + JWT)                 │
│                   Port: 3000                            │
└──────────┬──────────────────────────────┬───────────────┘
           │                              │
           │ PostgreSQL                   │ HTTP
           ▼                              ▼
┌──────────────────────┐    ┌────────────────────────────┐
│   PostgreSQL DB      │    │  Python Camera Service     │
│   (User data, jobs,  │    │  (FastAPI + Pixelink SDK)  │
│    images metadata)  │    │        Port: 8001          │
└──────────────────────┘    └────────────┬───────────────┘
                                         │ USB/SDK
                                         ▼
                            ┌────────────────────────────┐
                            │   Pixelink Camera          │
                            │   (Hardware Control)       │
                            └────────────────────────────┘
```

## 📦 Project Structure

```
CompuCyto/
├── frontend-vue/          # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── composables/   # Vue composables
│   │   ├── stores/        # Pinia state management
│   │   ├── views/         # Page views
│   │   └── api/           # API client
│   └── package.json
│
├── Nest/                  # NestJS backend
│   ├── src/
│   │   ├── auth/          # Authentication module
│   │   ├── camera/        # Camera proxy service
│   │   ├── stage/         # Stage control
│   │   ├── images/        # Image management
│   │   ├── users/         # User management
│   │   └── config/        # Configuration
│   └── package.json
│
├── backend-python/        # Python camera service
│   ├── main.py           # FastAPI application
│   ├── pixelink_camera.py # Camera SDK wrapper
│   ├── config.py         # Configuration
│   └── requirements.txt
│
├── Documentation/         # Project documentation
└── package.json          # Root workspace config
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **PostgreSQL** 14+
- **Pixelink SDK** (for camera control)
- **Git**

### One-Command Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd CompuCyto

# Install all dependencies (Node.js workspaces)
npm install

# Setup Python environment
npm run setup:python

# Configure environment variables (see Configuration section below)
# Edit Nest/.env and backend-python/.env

# Run all services in development mode
npm run dev
```

This will start:
- 🎨 Frontend at http://localhost:5173
- 🔧 Backend at http://localhost:3000
- 📷 Camera service at http://localhost:8001

## 📋 Detailed Setup

### 1. Install Node.js Dependencies

```bash
npm install
```

This installs dependencies for both frontend and backend using npm workspaces.

### 2. Setup Python Environment

```bash
cd backend-python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database

```bash
# Install PostgreSQL if not already installed
# Create database
createdb compucyto

# Or using psql:
psql -U postgres
CREATE DATABASE compucyto;
\q
```

### 4. Configure Environment Variables

#### Backend (Nest/.env)
```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_NAME=compucyto

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRATION=24h

# Server
PORT=3000
NODE_ENV=development

# Python Camera Service
PYTHON_CAMERA_URL=http://localhost:8001
SERVICE_TIMEOUT=30000
```

#### Python Camera Service (backend-python/.env)
```env
# Server
HOST=0.0.0.0
PORT=8001
DEBUG=True

# Camera
CAMERA_SERIAL_NUMBER=
DEFAULT_EXPOSURE=100
DEFAULT_GAIN=1.0
IMAGE_SAVE_PATH=./captures
IMAGE_FORMAT=jpg
IMAGE_QUALITY=95

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Run Database Migrations

```bash
cd Nest
npm run typeorm:run-migrations
```

## 🎮 Running the Application

### Development Mode

Run all services together:
```bash
npm run dev
```

Or run individually:
```bash
# Frontend only
npm run dev:frontend

# Backend only
npm run dev:backend

# Python camera service only
npm run dev:python
```

### Production Mode

```bash
# Build all
npm run build

# Start all services
npm run start
```

## 🔧 Available Scripts

From root directory:

| Command | Description |
|---------|-------------|
| `npm install` | Install all dependencies |
| `npm run setup:python` | Setup Python virtual environment |
| `npm run dev` | Run all services in development mode |
| `npm run dev:frontend` | Run Vue frontend only |
| `npm run dev:backend` | Run NestJS backend only |
| `npm run dev:python` | Run Python camera service only |
| `npm run build` | Build all services |
| `npm run start` | Start all services in production mode |

## 📚 Service-Specific Documentation

- **Frontend**: See `frontend-vue/README.md`
- **Backend**: See `Documentation/NESTJS_BACKEND_SPECIFICATION.md`
- **Camera Service**: See `backend-python/README.md`
- **API Documentation**: 
  - NestJS: http://localhost:3000/api (Swagger)
  - Python: http://localhost:8001/docs (FastAPI)

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/profile` - Get user profile

### Camera Control
- `POST /api/v1/camera/capture` - Capture image
- `GET /api/v1/camera/settings` - Get camera settings
- `PUT /api/v1/camera/settings` - Update settings
- `GET /api/v1/camera/preview` - Get video stream URL

### Stage Control
- `POST /api/v1/stage/move` - Move stage
- `GET /api/v1/stage/position` - Get current position
- `POST /api/v1/stage/home` - Home stage

### Images
- `GET /api/v1/images` - List images
- `GET /api/v1/images/:id` - Get image details
- `DELETE /api/v1/images/:id` - Delete image

## 🧪 Testing

### Backend Tests
```bash
cd Nest
npm run test
npm run test:e2e
```

### Frontend Tests
```bash
cd frontend-vue
npm run test
```

## 🐛 Troubleshooting

### Camera Not Detected
1. Verify Pixelink SDK is installed
2. Check USB connection
3. Try specifying `CAMERA_SERIAL_NUMBER` in `backend-python/.env`
4. Check camera works with Pixelink Capture software

### Database Connection Issues
1. Verify PostgreSQL is running
2. Check credentials in `Nest/.env`
3. Ensure database exists: `createdb compucyto`

### Port Already in Use
Change ports in respective `.env` files:
- Frontend: `vite.config.ts` → `server.port`
- Backend: `Nest/.env` → `PORT`
- Python: `backend-python/.env` → `PORT`

### CORS Issues
Add your frontend URL to:
- `Nest/src/main.ts` → CORS configuration
- `backend-python/.env` → `ALLOWED_ORIGINS`

## 🔐 Security Notes

- Change `JWT_SECRET` in production
- Use strong database passwords
- Don't commit `.env` files
- Enable HTTPS in production
- Restrict CORS origins

## 📦 Deployment

### Docker (Recommended)
```bash
# Coming soon - Docker Compose configuration
docker-compose up
```

### Manual Deployment
1. Build all services: `npm run build`
2. Setup PostgreSQL on server
3. Configure environment variables
4. Run migrations: `cd Nest && npm run typeorm:run-migrations`
5. Start services:
   - Frontend: Serve `frontend-vue/dist` with Nginx
   - Backend: `cd Nest && npm run start:prod`
   - Python: `cd backend-python && uvicorn main:app`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT

## 👥 Authors

- Lorenzo

## 🙏 Acknowledgments

- Pixelink for camera SDK
- NestJS team
- Vue.js team
- FastAPI team
