# NestJS Backend Specification - Microscope Control System

## Project Overview

Build a NestJS backend that serves as the primary orchestration layer for a microscope control system. The backend handles authentication, communicates with Python camera service and Raspberry Pi motor controller, manages database operations, and provides real-time updates via WebSocket.

---

#### **Core Application** (11 files)
- ✅ `src/main.ts` - Application bootstrap, CORS, validation
- ✅ `src/app.module.ts` - Root module structure
- ✅ `src/config/config.service.ts` - All 30+ environment variables
- ✅ `src/config/config.module.ts` - Global configuration
- ✅ `src/config/database.config.ts` - TypeORM setup with safety warnings

#### **Authentication System** (7 files)
- ✅ `src/auth/auth.service.ts` - Login/register flow
- ✅ `src/auth/auth.controller.ts` - Auth endpoints
- ✅ `src/auth/auth.module.ts` - Auth module setup
- ✅ `src/auth/strategies/jwt.strategy.ts` - Token validation process
- ✅ `src/auth/guards/jwt-auth.guard.ts` - Route protection
- ✅ `src/auth/dto/login.dto.ts` - Login validation
- ✅ `src/auth/dto/register.dto.ts` - Registration validation

#### **Camera Control** (4 files)
- ✅ `src/camera/camera.service.ts` - HTTP proxy to Python service
- ✅ `src/camera/camera.controller.ts` - Camera endpoints
- ✅ `src/camera/camera.module.ts` - Camera module
- ✅ `src/camera/dto/capture.dto.ts` - Capture parameters

#### **Stage Control** (5 files) **[CRITICAL SAFETY]**
- ✅ `src/stage/stage.service.ts` - Motor control with validation
- ✅ `src/stage/stage.controller.ts` - Stage endpoints
- ✅ `src/stage/stage.module.ts` - Stage module
- ✅ `src/stage/validators/position-validator.ts` - **Safety limits**
- ✅ `src/stage/dto/move.dto.ts` - Movement parameters

#### **User Management** (5 files)
- ✅ `src/users/users.service.ts` - User CRUD operations
- ✅ `src/users/users.controller.ts` - User endpoints
- ✅ `src/users/users.module.ts` - Users module
- ✅ `src/users/entities/user.entity.ts` - Password hashing, relationships
- ✅ `src/users/entities/user-profile.entity.ts` - User preferences

#### **Database Entities** (4 files)
- ✅ `src/jobs/entities/job.entity.ts` - Job tracking
- ✅ `src/images/entities/image.entity.ts` - Image metadata
- ✅ `src/positions/entities/position.entity.ts` - Saved positions
- ✅ `src/sensors/entities/sensor-status.entity.ts` - Sensor state
- ✅ `src/database/entities/system-log.entity.ts` - Event logging

#### **Health & Monitoring** (1 file)
- ✅ `src/common/controllers/health.controller.ts` - System health


## System Architecture

```
┌─────────────────────────────────────────┐
│  Vue 3 Frontend                         │
│  Hosting: Windows PC (served by NestJS)│
│  OR Vercel (remote access)              │
└──────────────┬──────────────────────────┘
               │ HTTPS + JWT Auth + WebSocket
               │
┌──────────────▼──────────────────────────┐
│  NestJS Backend (Primary Logic Layer)  │
│  Location: Windows PC                   │
│  Port: 3000                             │
│  ┌────────────────────────────────────┐ │
│  │ • JWT Authentication (Passport)    │ │
│  │ • REST API Endpoints               │ │
│  │ • WebSocket Gateway (Socket.IO)    │ │
│  │ • TypeORM (PostgreSQL)             │ │
│  │ • Bull Queue (Redis)               │ │
│  │ • HTTP clients to services         │ │
│  └────────────────────────────────────┘ │
└────────┬──────────────┬─────────────────┘
         │              │
    ┌────▼─────┐   ┌────▼──────┐
    │ Python   │   │ Raspberry │
    │ Camera   │   │ Pi Motor  │
    │ Service  │   │ Controller│
    │ Port:8001│   │ Port:5000 │
    └──────────┘   └───────────┘
         │              │
    ┌────▼─────┐   ┌────▼──────┐
    │  Camera  │   │  Motors   │
    │ Hardware │   │  Sensors  │
    └──────────┘   └───────────┘

┌─────────────────────────────────────────┐
│  Infrastructure (Windows PC)            │
│  • PostgreSQL (port 5432)               │
│  • Redis (port 6379)                    │
└─────────────────────────────────────────┘
```

---

## Technology Stack

### Core Framework
- **NestJS** (latest stable version)
- **TypeScript** (strict mode)
- **Node.js** 20+

### Database & ORM
- **PostgreSQL** 16
- **TypeORM** (with decorators)
- **Migrations** (TypeORM migrations)

### Authentication
- **Passport.js** (JWT strategy)
- **@nestjs/jwt**
- **bcrypt** (password hashing)

### Real-Time Communication
- **Socket.IO** (@nestjs/websockets)
- **WebSocket Gateway**

### Job Queue
- **Bull** (@nestjs/bull)
- **Redis** (Bull backend)

### HTTP Communication
- **@nestjs/axios** (HTTP client)
- **axios**

### Validation
- **class-validator**
- **class-transformer**

---

## Project Structure

```
microscope-backend/
├── src/
│   ├── main.ts                          # Application entry point
│   ├── app.module.ts                    # Root module
│   │
│   ├── config/
│   │   ├── config.module.ts
│   │   ├── config.service.ts            # Environment variables
│   │   └── database.config.ts           # TypeORM configuration
│   │
│   ├── common/
│   │   ├── decorators/                  # Custom decorators
│   │   ├── guards/                      # Auth guards
│   │   ├── interceptors/                # Response interceptors
│   │   └── filters/                     # Exception filters
│   │
│   ├── auth/
│   │   ├── auth.module.ts
│   │   ├── auth.service.ts              # Login, register, JWT
│   │   ├── auth.controller.ts
│   │   ├── strategies/
│   │   │   └── jwt.strategy.ts
│   │   ├── guards/
│   │   │   └── jwt-auth.guard.ts
│   │   └── dto/
│   │       ├── login.dto.ts
│   │       └── register.dto.ts
│   │
│   ├── users/
│   │   ├── users.module.ts
│   │   ├── users.service.ts
│   │   ├── users.controller.ts
│   │   ├── entities/
│   │   │   ├── user.entity.ts           # One-to-One with UserProfile
│   │   │   └── user-profile.entity.ts   # One-to-One with User
│   │   └── dto/
│   │
│   ├── camera/
│   │   ├── camera.module.ts
│   │   ├── camera.service.ts            # HTTP client to Python service
│   │   ├── camera.controller.ts
│   │   └── dto/
│   │       └── capture.dto.ts
│   │
│   ├── stage/
│   │   ├── stage.module.ts
│   │   ├── stage.service.ts             # HTTP client to Raspberry Pi
│   │   ├── stage.controller.ts
│   │   ├── validators/
│   │   │   └── position-validator.ts    # Safety limits validation
│   │   └── dto/
│   │       └── move.dto.ts
│   │
│   ├── images/
│   │   ├── images.module.ts
│   │   ├── images.service.ts            # CRUD operations
│   │   ├── images.controller.ts
│   │   ├── entities/
│   │   │   └── image.entity.ts          # Many-to-One with Job
│   │   └── dto/
│   │
│   ├── jobs/
│   │   ├── jobs.module.ts
│   │   ├── jobs.service.ts
│   │   ├── jobs.controller.ts
│   │   ├── jobs.processor.ts            # Bull queue processor
│   │   ├── entities/
│   │   │   └── job.entity.ts            # One-to-Many with Images, Many-to-One with User
│   │   └── dto/
│   │       ├── create-job.dto.ts
│   │       └── update-job.dto.ts
│   │
│   ├── positions/
│   │   ├── positions.module.ts
│   │   ├── positions.service.ts
│   │   ├── positions.controller.ts
│   │   ├── entities/
│   │   │   └── position.entity.ts       # Many-to-One with User
│   │   └── dto/
│   │
│   ├── sensors/
│   │   ├── sensors.module.ts
│   │   ├── sensors.service.ts           # Poll RPi, event-based updates
│   │   ├── sensors.controller.ts
│   │   ├── entities/
│   │   │   └── sensor-status.entity.ts  # Current status only
│   │   └── dto/
│   │
│   ├── websocket/
│   │   ├── websocket.module.ts
│   │   └── websocket.gateway.ts         # Socket.IO gateway
│   │
│   └── database/
│       ├── database.module.ts
│       ├── migrations/                  # TypeORM migrations
│       └── seeds/                       # Database seeds
│
├── .env                                 # Environment variables (not in git)
├── .env.example                         # Template
├── package.json
├── tsconfig.json
├── nest-cli.json
└── README.md
```

---

## Database Schema (TypeORM Entities)

### 1. User Entity (Authentication)

**Relationships:**
- **One-to-One:** User ↔ UserProfile
- **One-to-Many:** User → Jobs
- **One-to-Many:** User → Positions

**Fields:**
- `id` (PrimaryGeneratedColumn)
- `email` (unique, indexed)
- `username` (unique)
- `password` (hashed with bcrypt, excluded from responses)
- `role` (enum: 'admin', 'user')
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

**Relations:**
- `profile` (OneToOne → UserProfile)
- `jobs` (OneToMany → Job)
- `positions` (OneToMany → Position)

---

### 2. UserProfile Entity (User Settings)

**Relationships:**
- **One-to-One:** UserProfile ↔ User

**Fields:**
- `id` (PrimaryGeneratedColumn)
- `userId` (foreign key, unique)
- `fullName` (string, nullable)
- `labRole` (string, nullable)
- `preferences` (JSON, default: {})
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

**Relations:**
- `user` (OneToOne → User)

---

### 3. Job Entity

**Relationships:**
- **Many-to-One:** Job → User (creator)
- **One-to-Many:** Job → Images

**Fields:**
- `id` (PrimaryGeneratedColumn)
- `userId` (foreign key, indexed)
- `name` (string)
- `description` (text, nullable)
- `jobType` (enum: 'timelapse', 'grid', 'zstack', 'manual')
- `status` (enum: 'pending', 'running', 'paused', 'completed', 'failed', 'cancelled')
- `progress` (integer, 0-100)
- `totalSteps` (integer)
- `parameters` (JSON)
- `errorMessage` (text, nullable)
- `createdAt` (timestamp)
- `startedAt` (timestamp, nullable)
- `completedAt` (timestamp, nullable)

**Relations:**
- `user` (ManyToOne → User)
- `images` (OneToMany → Image)

**Indexes:**
- `userId`, `status`, `jobType`, `createdAt`

---

### 4. Image Entity

**Relationships:**
- **Many-to-One:** Image → Job (nullable - images can exist without jobs)

**Fields:**
- `id` (PrimaryGeneratedColumn)
- `jobId` (foreign key, nullable, indexed)
- `filename` (string, unique)
- `thumbnailPath` (string, nullable)
- `capturedAt` (timestamp, indexed)
- `xPosition` (float, nullable)
- `yPosition` (float, nullable)
- `zPosition` (float, nullable)
- `exposureTime` (integer, milliseconds)
- `gain` (float)
- `fileSize` (integer, bytes)
- `width` (integer, pixels)
- `height` (integer, pixels)
- `metadata` (JSON, default: {})

**Relations:**
- `job` (ManyToOne → Job, nullable)

**Indexes:**
- `jobId`, `capturedAt` (DESC)

---

### 5. Position Entity (Saved Positions)

**Relationships:**
- **Many-to-One:** Position → User (creator)

**Fields:**
- `id` (PrimaryGeneratedColumn)
- `userId` (foreign key, indexed)
- `name` (string)
- `description` (text, nullable)
- `xPosition` (float)
- `yPosition` (float)
- `zPosition` (float)
- `cameraSettings` (JSON, default: {})
- `createdAt` (timestamp)

**Relations:**
- `user` (ManyToOne → User)

**Indexes:**
- `userId`, `name`

---

### 6. SensorStatus Entity (Current Sensor State)

**No relationships** (standalone status table)

**Fields:**
- `id` (PrimaryGeneratedColumn)
- `sensorType` (string, unique) - e.g., 'temperature', 'limit_x_min', 'limit_x_max'
- `value` (float or boolean, depends on sensor)
- `unit` (string) - e.g., '°C', 'boolean'
- `status` (enum: 'normal', 'warning', 'critical')
- `lastUpdated` (timestamp)

**Note:** This table has a fixed number of rows (one per sensor type). UPDATE operations only, not INSERT.

---

### 7. SystemLog Entity (Event Logging)

**No relationships** (standalone logging)

**Fields:**
- `id` (PrimaryGeneratedColumn)
- `timestamp` (timestamp, indexed)
- `level` (enum: 'debug', 'info', 'warning', 'error', 'critical')
- `component` (string, indexed) - e.g., 'camera', 'stage', 'sensor', 'job'
- `message` (text)
- `details` (JSON, default: {})

**Indexes:**
- `timestamp` (DESC), `level`, `component`

---

## TypeORM Relationship Summary

**Satisfies all requirements:**

✅ **One-to-One:** User ↔ UserProfile
✅ **One-to-Many:** User → Jobs, User → Positions, Job → Images
✅ **Many-to-One:** Job → User, Image → Job, Position → User

---

## API Endpoints

### Authentication

#### `POST /api/v1/auth/register`
Register new user

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "jwt.token.here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "user"
  }
}
```

---

#### `POST /api/v1/auth/login`
Login existing user

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** Same as register

---

#### `GET /api/v1/auth/profile`
Get current user profile (protected)

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "user",
  "profile": {
    "fullName": "John Doe",
    "labRole": "Researcher",
    "preferences": {}
  }
}
```

---

### Camera Control

**All routes protected with JWT guard**

#### `POST /api/v1/camera/capture`
Capture an image

**Flow:**
1. Validate JWT token
2. Call Python service: `POST http://localhost:8001/capture`
3. Save image metadata to database
4. Broadcast via WebSocket
5. Return response

**Request:**
```json
{
  "exposure": 100,
  "gain": 1.5
}
```

**Response:**
```json
{
  "id": 123,
  "filename": "/images/image_123.jpg",
  "thumbnailPath": "/thumbnails/thumb_123.jpg",
  "capturedAt": "2025-10-09T10:30:00Z",
  "exposureTime": 100,
  "gain": 1.5
}
```

---

#### `GET /api/v1/camera/settings`
Get current camera settings

**Flow:**
1. Call Python service: `GET http://localhost:8001/settings`
2. Return settings

**Response:**
```json
{
  "exposure": 100,
  "gain": 1.5,
  "resolution": {
    "width": 1920,
    "height": 1080
  }
}
```

---

#### `PUT /api/v1/camera/settings`
Update camera settings

**Flow:**
1. Call Python service: `PUT http://localhost:8001/settings`
2. Return updated settings

**Request:**
```json
{
  "exposure": 150,
  "gain": 2.0
}
```

---

#### `GET /api/v1/camera/preview`
Get live video feed URL

**Response:**
```json
{
  "streamUrl": "http://localhost:8001/video/feed"
}
```

**Note:** Frontend connects directly to Python for video stream (MJPEG or Socket.IO)

---

### Stage Control

**All routes protected with JWT guard**

#### `POST /api/v1/stage/move`
Move stage to position

**Flow:**
1. Validate position against safety limits (hardcoded or from config)
2. Call Raspberry Pi: `POST http://raspberrypi.local:5000/move`
3. Broadcast position update via WebSocket
4. Return response

**Request:**
```json
{
  "x": 1000,
  "y": 500,
  "z": 100,
  "relative": false
}
```

**Response:**
```json
{
  "status": "moving",
  "targetPosition": {
    "x": 1000,
    "y": 500,
    "z": 100
  }
}
```

---

#### `GET /api/v1/stage/position`
Get current stage position

**Flow:**
1. Call Raspberry Pi: `GET http://raspberrypi.local:5000/position`
2. Return position

**Response:**
```json
{
  "x": 1000,
  "y": 500,
  "z": 100,
  "isMoving": false
}
```

---

#### `POST /api/v1/stage/home`
Home all axes

**Flow:**
1. Call Raspberry Pi: `POST http://raspberrypi.local:5000/home`
2. Broadcast event via WebSocket
3. Return response

---

#### `POST /api/v1/stage/stop`
Emergency stop all movement

**Flow:**
1. Call Raspberry Pi: `POST http://raspberrypi.local:5000/stop`
2. Broadcast alert via WebSocket
3. Return response

---

### Images

**All routes protected with JWT guard**

#### `GET /api/v1/images`
List images with pagination and filters

**Query Parameters:**
- `skip` (default: 0)
- `limit` (default: 50)
- `jobId` (optional filter)
- `startDate` (optional, ISO format)
- `endDate` (optional, ISO format)

**Response:**
```json
{
  "total": 100,
  "skip": 0,
  "limit": 50,
  "images": [
    {
      "id": 1,
      "filename": "/images/image_001.jpg",
      "thumbnailPath": "/thumbnails/thumb_001.jpg",
      "capturedAt": "2025-10-09T10:30:00Z",
      "xPosition": 1000,
      "yPosition": 500,
      "zPosition": 100,
      "jobId": 5
    }
  ]
}
```

---

#### `GET /api/v1/images/:id`
Get specific image details

---

#### `DELETE /api/v1/images/:id`
Delete image and associated files

**Flow:**
1. Delete from database
2. Delete files from filesystem
3. Return success

---

### Jobs

**All routes protected with JWT guard**

#### `GET /api/v1/jobs`
List jobs with filters

**Query Parameters:**
- `skip`, `limit`
- `status` (optional)
- `jobType` (optional)
- `userId` (optional, admin only)

---

#### `POST /api/v1/jobs`
Create new job

**Flow:**
1. Save job to database (status: 'pending')
2. Add job to Bull queue
3. Return job details

**Request (Timelapse):**
```json
{
  "name": "Evening Timelapse",
  "jobType": "timelapse",
  "parameters": {
    "interval": 60,
    "duration": 3600,
    "exposure": 100,
    "gain": 1.5
  }
}
```

**Request (Grid Scan):**
```json
{
  "name": "Sample Grid",
  "jobType": "grid",
  "parameters": {
    "startX": 0,
    "endX": 5000,
    "stepX": 500,
    "startY": 0,
    "endY": 5000,
    "stepY": 500,
    "zPosition": 100,
    "exposure": 100,
    "gain": 1.5
  }
}
```

---

#### `GET /api/v1/jobs/:id`
Get job details with images

---

#### `PATCH /api/v1/jobs/:id`
Update job status (pause/resume/cancel)

**Request:**
```json
{
  "status": "paused"
}
```

---

#### `DELETE /api/v1/jobs/:id`
Delete job and associated images

---

### Positions

**All routes protected with JWT guard**

#### `GET /api/v1/positions`
List saved positions (for current user)

---

#### `POST /api/v1/positions`
Save current position

**Request:**
```json
{
  "name": "Sample Center",
  "description": "Center of sample",
  "xPosition": 1000,
  "yPosition": 500,
  "zPosition": 100,
  "cameraSettings": {
    "exposure": 100,
    "gain": 1.5
  }
}
```

---

#### `POST /api/v1/positions/:id/goto`
Move to saved position

**Flow:**
1. Get position from database
2. Call stage service to move
3. Optionally apply camera settings
4. Return response

---

#### `DELETE /api/v1/positions/:id`
Delete saved position

---

### Sensors

**All routes protected with JWT guard**

#### `GET /api/v1/sensors/status`
Get current sensor status

**Response:**
```json
{
  "temperature": {
    "value": 25.5,
    "unit": "°C",
    "status": "normal",
    "lastUpdated": "2025-10-09T10:30:00Z"
  },
  "limitSwitches": {
    "xMin": false,
    "xMax": false,
    "yMin": false,
    "yMax": false,
    "zMin": false,
    "zMax": false
  }
}
```

---

#### `GET /api/v1/sensors/logs`
Get recent sensor events (from SystemLog table)

**Query Parameters:**
- `component` (filter: 'sensor')
- `level` (filter: 'warning', 'error', 'critical')
- `skip`, `limit`

---

### System

#### `GET /api/v1/health`
Health check endpoint (no auth required)

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "redis": true,
    "pythonCamera": true,
    "raspberryPi": true
  },
  "timestamp": "2025-10-09T10:30:00Z"
}
```

---

## WebSocket Events

### Connection

```javascript
// Client connects with JWT token
const socket = io('http://localhost:3000', {
  auth: {
    token: 'jwt.token.here'
  }
});
```

### Events from Server → Client

#### `position_update`
Real-time position updates during movement

```json
{
  "x": 1000,
  "y": 500,
  "z": 100,
  "isMoving": true
}
```

**Frequency:** Every 1 second during movement

---

#### `image_captured`
Notification when new image is captured

```json
{
  "id": 123,
  "filename": "/images/image_123.jpg",
  "thumbnailPath": "/thumbnails/thumb_123.jpg",
  "capturedAt": "2025-10-09T10:30:00Z"
}
```

---

#### `job_progress`
Job execution progress

```json
{
  "jobId": 5,
  "status": "running",
  "progress": 45,
  "totalSteps": 100,
  "currentStep": 45
}
```

**Frequency:** Every time a step completes

---

#### `sensor_alert`
Critical sensor alerts

```json
{
  "sensorType": "temperature",
  "value": 48.5,
  "threshold": 45,
  "severity": "critical",
  "message": "Temperature exceeded safe limit"
}
```

---

#### `system_status`
Periodic system health updates

```json
{
  "camera": "connected",
  "stage": "connected",
  "sensors": "normal"
}
```

**Frequency:** Every 5 seconds

---

### Events from Client → Server

#### `subscribe_position`
Request position updates

#### `unsubscribe_position`
Stop position updates

#### `subscribe_job`
Subscribe to specific job updates

```json
{
  "jobId": 5
}
```

---

## Background Jobs (Bull Queue)

### Job Types

#### 1. Timelapse Job

**Processor Logic:**
1. Get job parameters from database
2. For each interval:
   - Call camera service to capture
   - Wait for interval duration
   - Update job progress
   - Broadcast progress via WebSocket
3. Mark job as completed
4. Handle errors and retries

---

#### 2. Grid Scan Job

**Processor Logic:**
1. Calculate grid points from parameters
2. For each grid point:
   - Call stage service to move
   - Wait for movement to complete
   - Call camera service to capture
   - Update progress
   - Broadcast progress
3. Mark completed

---

#### 3. Z-Stack Job

**Processor Logic:**
1. Move to starting position
2. For each Z level:
   - Call camera service to capture
   - Move Z axis by step
   - Update progress
3. Mark completed

---

### Queue Configuration

- **Queue Name:** 'microscope-jobs'
- **Redis Connection:** localhost:6379
- **Concurrency:** 1 (only one job at a time)
- **Retry:** 3 attempts with exponential backoff
- **Timeout:** 24 hours per job

---

## Sensor Polling Service

### Implementation

**SensorsService** runs a background task using NestJS scheduler or interval:

1. **Poll Raspberry Pi** every 5 seconds: `GET http://raspberrypi.local:5000/sensors`
2. **Compare with previous values** (stored in memory)
3. **If significant change detected:**
   - Update `SensorStatus` table (UPDATE operation)
   - Log event to `SystemLog` if threshold exceeded
   - Broadcast via WebSocket if critical
4. **If movement detected:** Poll every 1 second instead of 5

### Thresholds

**Temperature:**
- Normal: < 40°C
- Warning: 40-45°C
- Critical: > 45°C

**Limit Switches:**
- Log event when triggered
- Broadcast alert immediately

**Motor Status:**
- Log when starts/stops moving
- Alert if stall detected

---

## Python Camera Service Communication

### Python Service Endpoints (External)

The Python service runs independently on Windows PC at `http://localhost:8001`

**NestJS must call these endpoints:**

#### `POST /capture`
**Request:**
```json
{
  "exposure": 100,
  "gain": 1.5
}
```

**Response:**
```json
{
  "filename": "image_20251009_103045.jpg",
  "filepath": "/images/image_20251009_103045.jpg",
  "thumbnailPath": "/thumbnails/thumb_20251009_103045.jpg",
  "width": 1920,
  "height": 1080,
  "fileSize": 2048576,
  "timestamp": "2025-10-09T10:30:45Z"
}
```

---

#### `GET /settings`
Get current camera settings

**Response:**
```json
{
  "exposure": 100,
  "gain": 1.5,
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "availableResolutions": [
    {"width": 1920, "height": 1080},
    {"width": 1280, "height": 720}
  ]
}
```

---

#### `PUT /settings`
Update camera settings

**Request:**
```json
{
  "exposure": 150,
  "gain": 2.0
}
```

---

#### `GET /video/feed`
MJPEG video stream (frontend connects directly)

---

#### `GET /health`
Health check

---

## Raspberry Pi Communication

### Raspberry Pi Endpoints (External)

The RPi Flask service runs at `http://raspberrypi.local:5000`

**NestJS must call these endpoints:**

#### `POST /move`
**Request:**
```json
{
  "x": 1000,
  "y": 500,
  "z": 100,
  "relative": false
}
```

**Response:**
```json
{
  "status": "success",
  "position": {
    "x": 1000,
    "y": 500,
    "z": 100
  },
  "estimatedTime": 15
}
```

---

#### `GET /position`
**Response:**
```json
{
  "x": 1000,
  "y": 500,
  "z": 100
}
```

---

#### `POST /home`
Home all axes

---

#### `POST /stop`
Emergency stop

---

#### `GET /sensors`
**Response:**
```json
{
  "temperature": 25.5,
  "limitSwitches": {
    "xMin": false,
    "xMax": false,
    "yMin": false,
    "yMax": false,
    "zMin": false,
    "zMax": false
  },
  "motorStatus": {
    "xMoving": false,
    "yMoving": false,
    "zMoving": false
  }
}
```

---

## Position Validation

### Safety Limits

Hardcode or load from configuration:

```typescript
const LIMITS = {
  X_MIN: 0,
  X_MAX: 10000,
  Y_MIN: 0,
  Y_MAX: 10000,
  Z_MIN: 0,
  Z_MAX: 5000,
};
```

### Validation Logic

Before calling Raspberry Pi to move:

1. **Check absolute limits:** Position must be within min/max
2. **Check relative moves:** Calculate target position first, then validate
3. **Throw error** if validation fails
4. **Log validation failures** to SystemLog

---

## Environment Variables

```bash
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_NAME=microscope_db

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=7d

# External Services
PYTHON_CAMERA_URL=http://localhost:8001
RASPBERRY_PI_URL=http://raspberrypi.local:5000
SERVICE_TIMEOUT=30000

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Server
PORT=3000
NODE_ENV=production

# CORS
ALLOWED_ORIGINS=http://localhost:5173,https://microscope-ui.vercel.app

# File Storage
IMAGES_PATH=./images
THUMBNAILS_PATH=./thumbnails

# Safety Limits (steps)
MAX_X_POSITION=10000
MAX_Y_POSITION=10000
MAX_Z_POSITION=5000
MIN_X_POSITION=0
MIN_Y_POSITION=0
MIN_Z_POSITION=0

# Sensor Polling
SENSOR_POLL_INTERVAL=5000
SENSOR_POLL_INTERVAL_MOVING=1000

# Temperature Thresholds
TEMP_WARNING_THRESHOLD=40
TEMP_CRITICAL_THRESHOLD=45
```

---

## Error Handling

### HTTP Exception Handling

Create global exception filter:

**Error Response Format:**
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request",
  "timestamp": "2025-10-09T10:30:00Z",
  "path": "/api/v1/camera/capture"
}
```

### Service Communication Errors

**Python Camera Service Down:**
- Return HTTP 503 Service Unavailable
- Log error to SystemLog
- Broadcast alert via WebSocket

**Raspberry Pi Down:**
- Return HTTP 503 Service Unavailable
- Log error to SystemLog
- Broadcast alert via WebSocket
- Do NOT attempt stage movement

### Position Validation Errors

- Return HTTP 400 Bad Request
- Include specific error message: "X position 15000 exceeds maximum 10000"
- Do NOT call Raspberry Pi

---

## Logging

### Application Logging

Use NestJS built-in logger:

- **INFO:** API requests, job starts/completions
- **WARNING:** Sensor thresholds exceeded, retries
- **ERROR:** Service communication failures, job failures
- **DEBUG:** Detailed execution flow (development only)

### Database Logging (SystemLog table)

Log significant events:

- Sensor alerts
- Job lifecycle (start, pause, complete, fail)
- Hardware errors
- Authentication failures
- Position validation failures

---

## Authentication & Authorization

### JWT Token

**Payload:**
```json
{
  "sub": 1,
  "email": "user@example.com",
  "role": "user",
  "iat": 1234567890,
  "exp": 1234654890
}
```

### Protected Routes

All routes except:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/health`

Must include: `Authorization: Bearer <token>`

### Role-Based Access (Optional Enhancement)

If implementing roles:
- **Admin:** Full access, can see all users' jobs
- **User:** Can only see own jobs and positions

---

## File Storage

### Images

- Stored on Windows PC filesystem
- Path: `./images/` (relative to NestJS app)
- Naming: `image_<timestamp>_<id>.jpg`
- Served as static files via NestJS

### Thumbnails

- Generated by Python service
- Path: `./thumbnails/`
- Naming: `thumb_<timestamp>_<id>.jpg`

### Static File Serving

Configure NestJS to serve:
- `/images/*` → `./images/`
- `/thumbnails/*` → `./thumbnails/`

---

## Development & Deployment

### Running Locally

```bash
# Install dependencies
npm install

# Setup database
# Create PostgreSQL database
# Run migrations
npm run migration:run

# Start Redis
redis-server

# Start NestJS
npm run start:dev
```

### Running in Production (Windows PC)

**Option 1: PM2**
```bash
npm install -g pm2
npm run build
pm2 start dist/main.js --name microscope-api
pm2 startup
pm2 save
```

**Option 2: Windows Service**
Use node-windows or pm2-windows-service

---

## Frontend Integration

### API Client Configuration

Frontend should use:
- Base URL: `http://localhost:3000/api/v1` (development)
- OR: `https://your-tunnel.com/api/v1` (production with Cloudflare Tunnel)

### WebSocket Connection

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:3000', {
  auth: {
    token: localStorage.getItem('token')
  }
});

socket.on('position_update', (data) => {
  // Update UI
});
```

### Authentication Flow

1. User logs in → Receive JWT token
2. Store token in localStorage
3. Include token in all API requests: `Authorization: Bearer <token>`
4. On 401 response → Redirect to login

---

## Testing Requirements

### Unit Tests

Test each service method in isolation:
- Mock external HTTP calls (Python, RPi)
- Mock database operations
- Test validation logic
- Test error handling

### Integration Tests

Test complete request flows:
- POST /auth/login → Receive token → Use token for protected route
- POST /camera/capture → Verify database entry created
- POST /jobs → Verify job added to queue

### E2E Tests

Test critical user flows:
- Complete authentication flow
- Capture image workflow
- Create and execute job workflow
- Emergency stop scenario

---

## Performance Considerations

### Database Queries

- Use indexes on frequently queried columns (see entity definitions)
- Use pagination for large result sets
- Use `select` to limit returned columns when needed

### Caching (Optional Enhancement)

Cache frequently accessed data in Redis:
- Current camera settings (5 second TTL)
- Current position (1 second TTL)
- User profiles (5 minute TTL)

### Rate Limiting

Implement rate limiting on endpoints:
- Camera capture: Max 10/minute per user
- Stage movement: Max 60/minute per user
- Prevent abuse and hardware damage

---

## Security Considerations

### Password Hashing

- Use bcrypt with salt rounds: 10
- Never store plain text passwords
- Exclude password from all responses

### JWT Security

- Use strong secret key (256-bit)
- Set reasonable expiration (7 days default)
- Implement token refresh mechanism (optional)

### CORS

- Only allow specific origins (frontend URL)
- Enable credentials for cookies/auth headers
- Don't use wildcard (*) in production

### Input Validation

- Validate all DTOs with class-validator
- Sanitize user inputs
- Validate position bounds before hardware calls

### SQL Injection Protection

- TypeORM uses parameterized queries (safe by default)
- Never concatenate raw SQL with user input

---

## Monitoring & Observability

### Health Checks

Implement `/health` endpoint that checks:
- Database connection (pg_isready)
- Redis connection (PING)
- Python service (HTTP GET /health)
- Raspberry Pi (HTTP GET /health)

### Metrics (Optional)

Track:
- API request count/latency
- Job success/failure rate
- Camera capture count
- Stage movement count
- WebSocket connections

### Alerts

Notify on:
- Service down (Python, RPi)
- Temperature critical
- Job failures
- Database connection lost

---

## Known Limitations & Edge Cases

### Concurrent Jobs

- System only supports 1 active job at a time (hardware limitation)
- Queue ensures sequential execution
- If user tries to start second job, it goes to queue

### Stage Movement During Job

- Block manual stage movement if job is running
- Return error: "Cannot move stage while job is running"

### Camera Busy

- If capture requested while previous capture in progress, queue or reject
- Python service should handle this

### Network Interruptions

- If RPi connection lost mid-movement, status unknown
- Implement retry logic with exponential backoff
- Log error and alert user

---

## Future Enhancements (Out of Scope)

### Phase 2 Features

- Multi-camera support
- Image processing (focus stacking, stitching)
- Advanced analytics dashboard
- Email notifications
- Mobile app

### Phase 3 Features

- Multi-user concurrent access with locking
- Cloud storage (AWS S3)
- AI-powered auto-focus
- Remote collaboration features

---

## Development Priorities

### Phase 1: Core Functionality (Weeks 1-3)

1. Project setup (NestJS, TypeORM, PostgreSQL)
2. Authentication (User, UserProfile, JWT)
3. Camera service integration (capture, settings)
4. Stage service integration (move, position, validation)
5. Basic WebSocket (position updates)

### Phase 2: Job System (Weeks 4-5)

1. Job entities and CRUD
2. Bull queue setup
3. Timelapse job processor
4. Grid scan job processor
5. Z-stack job processor
6. Job progress WebSocket events

### Phase 3: Images & Positions (Week 6)

1. Image CRUD operations
2. Image list with filters
3. Position CRUD operations
4. Position goto functionality

### Phase 4: Sensors & Polish (Week 7)

1. Sensor polling service
2. Sensor status endpoint
3. Event logging (SystemLog)
4. Error handling refinement
5. Testing

### Phase 5: Deployment (Week 8)

1. Production configuration
2. Windows service setup
3. Database migrations
4. Health checks
5. Documentation

---

## Critical Success Factors

### Must Have

✅ JWT authentication working
✅ Camera capture working (via Python service)
✅ Stage movement working (via Raspberry Pi)
✅ Position validation preventing hardware damage
✅ Job queue processing timelapses
✅ WebSocket real-time updates
✅ All TypeORM relationships implemented correctly

### Should Have

✅ Sensor monitoring
✅ System logging
✅ Error recovery
✅ Grid scan and z-stack jobs

### Nice to Have

✅ Advanced caching
✅ Comprehensive testing
✅ Performance optimization
✅ Monitoring dashboard

---

## Questions for Clarification

Before starting development, clarify:

1. **Camera details:** What camera model? SDK available?
2. **Raspberry Pi details:** GPIO pin assignments? Motor drivers?
3. **Image formats:** JPEG only? RAW support needed?
4. **File storage:** Local only? Cloud backup needed?
5. **User management:** Single user? Multi-user? Admin role needed?
6. **Deployment:** Windows version? Administrator access?
7. **Network:** Static IPs? DNS names? VPN?

---

## Contact & Support

For questions during development:
- Architecture questions → Review this document
- API questions → Refer to endpoint specifications
- Database questions → Review entity relationships
- External service questions → Refer to Python/RPi communication sections

---

## Appendix: Quick Reference

### Technology Versions

- NestJS: ^10.0.0
- TypeScript: ^5.0.0
- TypeORM: ^0.3.0
- PostgreSQL: 16
- Redis: 7
- Node.js: 20+

### Port Assignments

- NestJS: 3000
- PostgreSQL: 5432
- Redis: 6379
- Python Camera: 8001
- Raspberry Pi: 5000

### Key Commands

```bash
# Development
npm run start:dev

# Build
npm run build

# Migrations
npm run migration:generate --name=InitialSchema
npm run migration:run

# Testing
npm run test
npm run test:e2e
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-09  
**Target Completion:** 8 weeks from start

---

## Summary

This NestJS backend serves as the orchestration layer for the microscope control system. It handles all authentication, business logic, database operations, and coordinates communication between the Vue frontend, Python camera service, and Raspberry Pi motor controller. The system uses TypeORM with proper one-to-one, one-to-many, and many-to-one relationships, implements JWT authentication, provides real-time updates via WebSocket, and manages automated jobs through a Bull queue system.

**The backend never directly controls hardware** - it always communicates through the Python camera service (localhost:8001) and Raspberry Pi service (raspberrypi.local:5000), ensuring proper separation of concerns and maintainability.
