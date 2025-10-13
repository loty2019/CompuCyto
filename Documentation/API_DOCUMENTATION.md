# CompuCyto API Documentation

## Base URL
```
http://localhost:3000/api/v1
```

## Authentication

All endpoints except `/auth/register`, `/auth/login`, and `/health` require JWT authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer {your_jwt_token}
```

---

## Auth Endpoints

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "user",
    "profile": {
      "id": 1,
      "userId": 1,
      "fullName": null,
      "labRole": null,
      "preferences": {},
      "createdAt": "2025-10-09T10:30:00Z",
      "updatedAt": "2025-10-09T10:30:00Z"
    }
  }
}
```

---

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** Same as register

---

### Get Profile
```http
GET /api/v1/auth/profile
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "user",
  "createdAt": "2025-10-09T10:30:00Z",
  "updatedAt": "2025-10-09T10:30:00Z",
  "profile": {
    "id": 1,
    "fullName": null,
    "labRole": null,
    "preferences": {}
  }
}
```

---

## Camera Endpoints (Protected)

### Capture Image
```http
POST /api/v1/camera/capture
Authorization: Bearer {token}
Content-Type: application/json

{
  "exposure": 100,
  "gain": 1.5
}
```

Calls Python camera service at `http://localhost:8001/capture`

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

### Get Camera Settings
```http
GET /api/v1/camera/settings
Authorization: Bearer {token}
```

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

### Update Camera Settings
```http
PUT /api/v1/camera/settings
Authorization: Bearer {token}
Content-Type: application/json

{
  "exposure": 150,
  "gain": 2.0
}
```

**Response:** Same as GET settings

---

### Get Video Preview URL
```http
GET /api/v1/camera/preview
Authorization: Bearer {token}
```

**Response:**
```json
{
  "streamUrl": "http://localhost:8001/video/feed"
}
```

Frontend should connect directly to this URL for MJPEG stream.

---

## Stage Endpoints (Protected)

### Move Stage
```http
POST /api/v1/stage/move
Authorization: Bearer {token}
Content-Type: application/json

{
  "x": 1000,
  "y": 500,
  "z": 100,
  "relative": false
}
```

**Parameters:**
- `x`, `y`, `z`: Optional position values (omit to keep current position)
- `relative`: Boolean - `true` for relative movement, `false` for absolute

**Position Validation:**
- X range: 0 - 10000 (configurable via env)
- Y range: 0 - 10000
- Z range: 0 - 5000

Returns 400 Bad Request if position is out of bounds.

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

### Get Current Position
```http
GET /api/v1/stage/position
Authorization: Bearer {token}
```

**Response:**
```json
{
  "x": 1000,
  "y": 500,
  "z": 100,
  "is_moving": false
}
```

---

### Home All Axes
```http
POST /api/v1/stage/home
Authorization: Bearer {token}
```

Homes all axes (X, Y, Z) to origin position.

**Response:**
```json
{
  "status": "success",
  "message": "Homing initiated"
}
```

---

### Emergency Stop
```http
POST /api/v1/stage/stop
Authorization: Bearer {token}
```

Immediately stops all motor movement.

**Response:**
```json
{
  "status": "success",
  "message": "Motors stopped"
}
```

---

## Health Check (Public)

### Check System Health
```http
GET /api/v1/health
```

No authentication required.

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "pythonCamera": true,
    "raspberryPi": true,
    "redis": true
  },
  "timestamp": "2025-10-09T10:30:00.000Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request"
}
```

### 401 Unauthorized
```json
{
  "statusCode": 401,
  "message": "Unauthorized"
}
```

### 503 Service Unavailable
```json
{
  "statusCode": 503,
  "message": "Camera service unavailable"
}
```

Returned when Python camera service or Raspberry Pi controller is not reachable.

---

## Frontend Integration

### Vue 3 API Client Example

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:3000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add JWT token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login example
const login = async (email: string, password: string) => {
  const { data } = await apiClient.post('/auth/login', { email, password });
  localStorage.setItem('token', data.access_token);
  return data.user;
};

// Capture image example
const captureImage = async (exposure?: number, gain?: number) => {
  const { data } = await apiClient.post('/camera/capture', { exposure, gain });
  return data;
};

// Move stage example
const moveStage = async (x?: number, y?: number, z?: number, relative = false) => {
  const { data } = await apiClient.post('/stage/move', { x, y, z, relative });
  return data;
};
```

---

## Phase 2 Features (Coming Soon)

The following endpoints will be added in Phase 2:

- **Images**: `/api/v1/images` - Image management and gallery
- **Jobs**: `/api/v1/jobs` - Automated job management (timelapse, grid scan, z-stack)
- **Positions**: `/api/v1/positions` - Saved position management
- **Sensors**: `/api/v1/sensors` - Sensor status and monitoring
- **WebSocket**: Real-time updates for position, job progress, sensor alerts

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- The backend acts as an orchestration layer - it doesn't control hardware directly
- Camera operations proxy to Python service at port 8001
- Stage operations proxy to Raspberry Pi at port 5000
- The system validates all position requests before forwarding to hardware
