# CompuCyto System Architecture

## Full Stack Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         END USER                                  │
│                      (Web Browser)                               │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ HTTPS/WSS
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                     FRONTEND LAYER                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Vue 3 + Vite Application                       │ │
│  │                   (Port 5173)                               │ │
│  │                                                             │ │
│  │  Components:                                                │ │
│  │  • CameraControl.vue    - Camera controls & capture        │ │
│  │  • ImageGallery.vue     - Display captured images          │ │
│  │  • StageControl.vue     - Microscope stage control         │ │
│  │  • MicroscopeMap.vue    - Position visualization           │ │
│  │  • UserProfile.vue      - User management                  │ │
│  │                                                             │ │
│  │  State Management:                                          │ │
│  │  • Pinia stores (auth, microscope, websocket)              │ │
│  │                                                             │ │
│  │  Styling:                                                   │ │
│  │  • Tailwind CSS for responsive design                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ HTTP REST + JWT
                            │ WebSocket
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                    BACKEND LAYER (NestJS)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              NestJS Application                             │ │
│  │                 (Port 3000)                                 │ │
│  │                                                             │ │
│  │  Modules:                                                   │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Auth Module                                         │ │ │
│  │  │  • JWT authentication                                │ │ │
│  │  │  • User registration/login                           │ │ │
│  │  │  • Password hashing (bcrypt)                         │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Camera Module (Proxy)                               │ │ │
│  │  │  • Forwards requests to Python service               │ │ │
│  │  │  • Saves image metadata to DB                        │ │ │
│  │  │  • User association                                  │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Stage Module                                        │ │ │
│  │  │  • Stage movement control                            │ │ │
│  │  │  • Position tracking                                 │ │ │
│  │  │  • Homing routines                                   │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Images Module                                       │ │ │
│  │  │  • Image metadata management                         │ │ │
│  │  │  • Gallery queries                                   │ │ │
│  │  │  • User image association                            │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Users Module                                        │ │ │
│  │  │  • User CRUD operations                              │ │ │
│  │  │  • Profile management                                │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  Infrastructure:                                            │ │
│  │  • TypeORM for database operations                         │ │
│  │  • Swagger/OpenAPI documentation                           │ │
│  │  • CORS middleware                                         │ │
│  │  • Validation pipes                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────┬─────────────────────────────┬──────────────────────────┘
          │                             │
          │ TypeORM                     │ HTTP (internal)
          │                             │
          ▼                             ▼
┌──────────────────────┐   ┌────────────────────────────────────────┐
│   DATABASE LAYER     │   │   HARDWARE ABSTRACTION LAYER           │
│                      │   │                                        │
│  ┌────────────────┐  │   │  ┌──────────────────────────────────┐ │
│  │  PostgreSQL    │  │   │  │    FastAPI Python Service        │ │
│  │   (Port 5432)  │  │   │  │         (Port 8001)              │ │
│  │                │  │   │  │                                  │ │
│  │  Tables:       │  │   │  │  Endpoints:                      │ │
│  │  • users       │  │   │  │  • POST /capture                 │ │
│  │  • images      │  │   │  │  • GET  /settings                │ │
│  │  • jobs        │  │   │  │  • PUT  /settings                │ │
│  │  • positions   │  │   │  │  • GET  /video/feed              │ │
│  │  • sensors     │  │   │  │  • POST /stream/start            │ │
│  │                │  │   │  │  • POST /stream/stop             │ │
│  │  Features:     │  │   │  │  • GET  /health                  │ │
│  │  • Migrations  │  │   │  │                                  │ │
│  │  • Relations   │  │   │  │  Features:                       │ │
│  │  • Indexes     │  │   │  │  • Pixelink SDK wrapper          │ │
│  └────────────────┘  │   │  │  • Simulation mode               │ │
│                      │   │  │  • Image capture & save          │ │
│  Stores:             │   │  │  • MJPEG streaming               │ │
│  • User credentials  │   │  │  • Camera settings management    │ │
│  • Image metadata    │   │  │  • Auto-documentation (Swagger)  │ │
│  • System state      │   │  │  • Request validation (Pydantic) │ │
└──────────────────────┘   │  └──────────────────────────────────┘ │
                           │                │                       │
                           │                │ Pixelink SDK          │
                           │                │ (Python bindings)     │
                           │                ▼                       │
                           │   ┌────────────────────────────────┐  │
                           │   │    Hardware Interface          │  │
                           │   │                                │  │
                           │   │  • Camera initialization       │  │
                           │   │  • Exposure control            │  │
                           │   │  • Gain control                │  │
                           │   │  • Frame capture               │  │
                           │   │  • Format conversion           │  │
                           │   │  • Streaming control           │  │
                           │   └────────────────────────────────┘  │
                           └────────────────┬───────────────────────┘
                                            │
                                            │ USB 3.0
                                            │
                           ┌────────────────▼───────────────────────┐
                           │       HARDWARE LAYER                   │
                           │                                        │
                           │  ┌──────────────────────────────────┐ │
                           │  │     Pixelink Camera              │ │
                           │  │                                  │ │
                           │  │  • Image sensor                  │ │
                           │  │  • Optics                        │ │
                           │  │  • USB controller                │ │
                           │  │  • Onboard processing            │ │
                           │  └──────────────────────────────────┘ │
                           └────────────────────────────────────────┘
```

## Request Flow Example: Capture Image

```
┌──────┐     1. Click "Capture"      ┌──────────┐
│ User │ ───────────────────────────>│  Vue.js  │
└──────┘                              └────┬─────┘
                                           │
                          2. POST /api/v1/camera/capture
                             + JWT token
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   NestJS    │
                                    │             │
                                    │ • Validate  │
                                    │   JWT       │
                                    │ • Extract   │
                                    │   user ID   │
                                    └──────┬──────┘
                                           │
                          3. POST http://localhost:8001/capture
                             { exposure: 100, gain: 1.5 }
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   FastAPI   │
                                    │             │
                                    │ • Validate  │
                                    │   params    │
                                    └──────┬──────┘
                                           │
                          4. Call Pixelink SDK
                             PxLApi.getNextFrame()
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   Camera    │
                                    │   Hardware  │
                                    │             │
                                    │ • Capture   │
                                    │ • Return    │
                                    │   raw data  │
                                    └──────┬──────┘
                                           │
                          5. Process & save image
                             ./captures/capture_*.jpg
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   FastAPI   │
                                    │             │
                                    │ • Save file │
                                    │ • Return    │
                                    │   metadata  │
                                    └──────┬──────┘
                                           │
                          6. Save metadata to DB
                             + user_id association
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   NestJS    │
                                    │             │
                                    │ • Insert to │
                                    │   images    │
                                    │   table     │
                                    └──────┬──────┘
                                           │
                          7. Return success response
                             { imageId, filename, ... }
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   Vue.js    │
                                    │             │
                                    │ • Update UI │
                                    │ • Show      │
                                    │   image     │
                                    └──────┬──────┘
                                           │
                          8. Display captured image
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │    User     │
                                    │   sees      │
                                    │   result    │
                                    └─────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Pinia
- **HTTP Client**: Axios
- **WebSocket**: Native WebSocket API

### Backend (NestJS)
- **Framework**: NestJS
- **Language**: TypeScript
- **ORM**: TypeORM
- **Database**: PostgreSQL
- **Authentication**: JWT (Passport)
- **Validation**: class-validator
- **Documentation**: Swagger/OpenAPI
- **HTTP Client**: Axios (for Python service)

### Hardware Service (Python)
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Image Processing**: Pillow, NumPy
- **Video**: OpenCV
- **SDK**: Pixelink SDK (proprietary)
- **Documentation**: FastAPI Swagger

### Database
- **System**: PostgreSQL 14+
- **Features**: Relations, migrations, indexes
- **Connection**: TypeORM connection pool

### Infrastructure
- **Package Management**: npm workspaces
- **Process Management**: concurrently
- **Version Control**: Git
- **Environment**: dotenv

## Security Model

```
┌──────────┐
│  Public  │  No authentication required
│  Access  │  • Login, Register
└──────────┘

┌──────────┐
│   JWT    │  Token-based authentication
│Protected │  • All camera operations
│  Routes  │  • User profile
└──────────┘  • Image gallery

┌──────────┐
│ Internal │  No external access
│ Services │  • Python camera service
└──────────┘  • PostgreSQL database
```

## Port Allocation

| Service | Port | Protocol | Access |
|---------|------|----------|--------|
| Vue Frontend | 5173 | HTTP | Public |
| NestJS Backend | 3000 | HTTP | Public |
| Python Camera | 8001 | HTTP | Internal |
| PostgreSQL | 5432 | TCP | Internal |

## Data Flow

### User Data
```
Vue → NestJS → PostgreSQL
```

### Camera Data
```
Vue → NestJS → FastAPI → Pixelink SDK → Camera
```

### Image Metadata
```
Camera → FastAPI → NestJS → PostgreSQL
              ↓
         File System
      (./captures/*.jpg)
```

### Video Stream
```
Camera → FastAPI → Vue (direct MJPEG stream)
```

## Deployment Topology

### Development
```
Single Machine:
├── frontend:5173
├── backend:3000
├── python:8001
└── postgres:5432
```

### Production (Future)
```
Load Balancer
    ├── Frontend Servers (Nginx)
    ├── Backend Cluster (NestJS)
    │   └── Python Camera Service (1:1 with camera hardware)
    └── Database (PostgreSQL + replica)
```

## Scalability Considerations

- **Frontend**: Static files, CDN-ready
- **NestJS**: Stateless, horizontally scalable
- **Python**: 1:1 with camera (hardware bound)
- **Database**: Connection pooling, read replicas
- **WebSocket**: Sticky sessions required

## Monitoring Points

1. **Health Checks**
   - `/health` endpoints on all services
   - Database connectivity
   - Camera hardware status

2. **Metrics**
   - Request latency
   - Capture success rate
   - Database query performance
   - WebSocket connections

3. **Logging**
   - Application logs (Winston/Python logging)
   - Access logs (Nginx)
   - Error tracking
   - Audit logs (user actions)

---

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Independent service scaling
- ✅ Easy testing and development
- ✅ Hardware abstraction
- ✅ Comprehensive monitoring
- ✅ Security at multiple layers
