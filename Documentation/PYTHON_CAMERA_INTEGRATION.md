# Python Camera Service Integration Guide

This document explains how the Python FastAPI camera service integrates with the NestJS backend.

## Overview

The Python camera service acts as a **hardware abstraction layer** between the NestJS backend and the Pixelink camera hardware. This architecture provides:

1. **Language Specialization**: Python for hardware SDK, TypeScript for business logic
2. **Service Isolation**: Camera crashes don't affect main backend
3. **Independent Scaling**: Camera service can be deployed on different hardware
4. **Easy Testing**: Simulation mode for development without camera

## Architecture Flow

```
┌─────────────┐
│   Vue.js    │  HTTP Request (with JWT)
│  Frontend   │  POST /api/v1/camera/capture
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│              NestJS Backend                     │
│  ┌───────────────────────────────────────────┐  │
│  │  CameraController                         │  │
│  │  - Receives request                       │  │
│  │  - Validates JWT                          │  │
│  │  - Extracts user ID                       │  │
│  └────────────────┬──────────────────────────┘  │
│                   ▼                              │
│  ┌───────────────────────────────────────────┐  │
│  │  CameraService                            │  │
│  │  - Proxies to Python service              │  │
│  │  - Saves metadata to PostgreSQL           │  │
│  │  - Handles errors                         │  │
│  └────────────────┬──────────────────────────┘  │
└───────────────────┼──────────────────────────────┘
                    │ HTTP Request
                    │ POST http://localhost:8001/capture
                    ▼
┌─────────────────────────────────────────────────┐
│         Python FastAPI Service                  │
│  ┌───────────────────────────────────────────┐  │
│  │  main.py (FastAPI App)                    │  │
│  │  - Receives capture request               │  │
│  │  - Validates parameters                   │  │
│  └────────────────┬──────────────────────────┘  │
│                   ▼                              │
│  ┌───────────────────────────────────────────┐  │
│  │  PixelinkCamera                           │  │
│  │  - Calls Pixelink SDK                     │  │
│  │  - Captures image                         │  │
│  │  - Saves to disk                          │  │
│  │  - Returns metadata                       │  │
│  └────────────────┬──────────────────────────┘  │
└───────────────────┼──────────────────────────────┘
                    │ SDK Calls
                    ▼
              ┌──────────┐
              │ Pixelink │
              │  Camera  │
              └──────────┘
```

## Communication Protocol

### 1. Capture Image

**NestJS → Python**
```typescript
POST http://localhost:8001/capture
Content-Type: application/json

{
  "exposure": 100,  // optional, milliseconds
  "gain": 1.5       // optional
}
```

**Python → NestJS Response**
```json
{
  "success": true,
  "filename": "capture_20250113_103045_123.jpg",
  "filepath": "./captures/capture_20250113_103045_123.jpg",
  "timestamp": "2025-01-13T10:30:45.123Z",
  "settings": {
    "exposure": 100,
    "gain": 1.5,
    "resolution": {
      "width": 1280,
      "height": 1024
    }
  },
  "image_info": {
    "size_bytes": 245678,
    "format": "JPG"
  }
}
```

### 2. Get Settings

**NestJS → Python**
```typescript
GET http://localhost:8001/settings
```

**Python → NestJS Response**
```json
{
  "exposure": 100,
  "gain": 1.0,
  "resolution": {
    "width": 1280,
    "height": 1024
  },
  "available_resolutions": [
    {"width": 640, "height": 480},
    {"width": 1280, "height": 1024},
    {"width": 1920, "height": 1080}
  ],
  "connected": true,
  "streaming": false
}
```

### 3. Update Settings

**NestJS → Python**
```typescript
PUT http://localhost:8001/settings
Content-Type: application/json

{
  "exposure": 150,  // optional
  "gain": 2.0       // optional
}
```

**Python → NestJS Response**
```json
{
  "exposure": 150,
  "gain": 2.0,
  "resolution": {
    "width": 1280,
    "height": 1024
  },
  // ... rest of settings
}
```

### 4. Video Stream

**Direct Frontend → Python**
```
GET http://localhost:8001/video/feed
```

Returns MJPEG stream (multipart/x-mixed-replace)

## NestJS Implementation

### Configuration (Nest/src/config/config.service.ts)

```typescript
@Injectable()
export class ConfigService {
  get pythonCameraUrl(): string {
    return process.env.PYTHON_CAMERA_URL || 'http://localhost:8001';
  }
  
  get serviceTimeout(): number {
    return parseInt(process.env.SERVICE_TIMEOUT || '30000', 10);
  }
}
```

### Camera Service (Nest/src/camera/camera.service.ts)

```typescript
@Injectable()
export class CameraService {
  constructor(
    private httpService: HttpService,
    private configService: ConfigService,
    @InjectRepository(Image)
    private imageRepository: Repository<Image>,
  ) {
    this.baseUrl = this.configService.pythonCameraUrl;
  }

  async capture(exposure?: number, gain?: number, userId?: number): Promise<any> {
    // Forward to Python service
    const { data } = await firstValueFrom(
      this.httpService.post(
        `${this.baseUrl}/capture`,
        { exposure, gain },
        { timeout: this.timeout }
      )
    );
    
    // Save metadata to database
    if (data && userId) {
      const image = this.imageRepository.create({
        userId,
        filename: data.filename,
        capturedAt: new Date(),
        exposureTime: exposure,
        gain: gain,
        metadata: data,
      });
      await this.imageRepository.save(image);
    }
    
    return data;
  }
}
```

## Python Implementation

### Main Application (backend-python/main.py)

```python
from fastapi import FastAPI
from pixelink_camera import PixelinkCamera

camera: PixelinkCamera = None

@app.post("/capture")
async def capture_image(request: CaptureRequest):
    filepath = Path(settings.image_save_path) / f"capture_{timestamp}.jpg"
    result = camera.capture_image(
        save_path=filepath,
        exposure=request.exposure,
        gain=request.gain
    )
    return result
```

### Camera Wrapper (backend-python/pixelink_camera.py)

```python
class PixelinkCamera:
    def capture_image(self, save_path: Path, exposure=None, gain=None):
        # Update settings if provided
        if exposure is not None:
            self._set_exposure(exposure)
        
        # Call Pixelink SDK
        ret = PxLApi.getNextFrame(self.camera_handle)
        # ... process frame
        
        # Save image
        image = Image.fromarray(image_data)
        image.save(save_path)
        
        return metadata
```

## Error Handling

### Connection Errors

If Python service is unavailable:

```typescript
// NestJS throws ServiceUnavailableException
throw new ServiceUnavailableException('Camera service unavailable');
```

Frontend receives:
```json
{
  "statusCode": 503,
  "message": "Camera service unavailable",
  "error": "Service Unavailable"
}
```

### Hardware Errors

If camera disconnected or fails:

```python
# Python FastAPI
raise HTTPException(
    status_code=503,
    detail="Camera not connected"
)
```

### Timeout Handling

NestJS has configurable timeout (default 30s):

```typescript
this.httpService.post(url, data, { 
  timeout: 30000  // 30 seconds
})
```

## Health Monitoring

### Health Check Endpoint

```typescript
// NestJS
@Get('health')
async checkHealth() {
  const healthy = await this.cameraService.checkHealth();
  return { 
    status: healthy ? 'ok' : 'error',
    service: 'camera',
    timestamp: new Date()
  };
}
```

```python
# Python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "camera_connected": camera.is_connected,
        "timestamp": datetime.now().isoformat()
    }
```

## Development Workflow

### Without Physical Camera

1. Python service runs in **simulation mode**
2. Generates test images (gradients)
3. All endpoints work normally
4. Perfect for frontend/backend development

### With Physical Camera

1. Install Pixelink SDK
2. Connect camera via USB
3. Configure serial number in `.env`
4. Python service auto-detects and initializes

## Testing

### Test Python Service Directly

```bash
# Health check
curl http://localhost:8001/health

# Capture
curl -X POST http://localhost:8001/capture \
  -H "Content-Type: application/json" \
  -d '{"exposure": 100}'

# Settings
curl http://localhost:8001/settings
```

### Test Through NestJS

```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Capture via NestJS
curl -X POST http://localhost:3000/api/v1/camera/capture \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exposure": 100}'
```

## Performance Considerations

### Latency

- NestJS → Python: ~1-5ms (local HTTP)
- Python → Camera: ~50-200ms (hardware dependent)
- **Total capture time**: ~60-210ms

### Optimization

1. **Keep connections alive**: HTTP persistent connections
2. **Pre-warm camera**: Initialize on startup
3. **Async operations**: FastAPI async handlers
4. **Caching**: Cache settings to avoid SDK calls

### Throughput

- **Sequential captures**: ~5-10 images/second
- **Video streaming**: 15-30 FPS
- **Concurrent requests**: FastAPI handles 100+ requests/sec

## Troubleshooting

### Python service not responding

```bash
# Check if service is running
curl http://localhost:8001/health

# Check logs
cd backend-python
python main.py  # See error output
```

### NestJS can't reach Python

1. Check `PYTHON_CAMERA_URL` in `Nest/.env`
2. Ensure Python service is running
3. Check firewall rules
4. Verify port 8001 is not blocked

### Camera not detected

```python
# Check in Python logs
INFO - Camera initialized successfully
# or
WARNING - Pixelink SDK not available. Running in simulation mode.
```

## Security

### No Authentication on Python Service

Python service should **NOT** be exposed to internet. It's designed to be called only by NestJS backend:

1. Run on localhost only (`HOST=0.0.0.0` for Docker)
2. Use firewall to block external access
3. NestJS handles all authentication
4. Python trusts all requests from NestJS

### Production Deployment

For production with Docker:
```yaml
version: '3'
services:
  nestjs:
    ports:
      - "3000:3000"
  
  python-camera:
    # No exposed ports - internal only
    networks:
      - backend
```

## Future Enhancements

1. **WebSocket streaming**: Real-time frame updates
2. **gRPC**: Faster binary protocol
3. **Message queue**: Async job processing
4. **Multiple cameras**: Camera pool management
5. **Image processing**: On-the-fly filters/analysis

## Summary

The Python FastAPI service provides:
- ✅ Clean HTTP API for camera control
- ✅ Hardware abstraction from NestJS
- ✅ Simulation mode for development
- ✅ Comprehensive error handling
- ✅ Real-time video streaming
- ✅ Automatic documentation (FastAPI Swagger)

This architecture allows independent development, testing, and deployment of camera control while maintaining clean separation of concerns.
