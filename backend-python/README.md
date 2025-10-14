# Camera Backend - Python Service for PixeLink SDK

This is a minimal FastAPI service that provides HTTP API access to a PixeLink camera. The NestJS backend calls this service to interact with camera hardware.

---

## Architecture Overview

```
┌─────────────────┐
│   Vue Frontend  │
│  (Port 5173)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  NestJS Backend │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ Python FastAPI  │  ◄─── Talks to PixeLink SDK
│   (Port 8001)   │
└─────────────────┘
```

**Why this architecture?**
- PixeLink SDK only has Python/C++ bindings
- FastAPI is lightweight and perfect for camera microservices
- NestJS handles authentication, database, business logic
- Clean separation of concerns

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure (Optional)
```bash
# Copy and edit .env if needed
cp .env.example .env
```

### 3. Run Service
```bash
python main.py
```

Service starts on **http://localhost:8001**

API docs available at: **http://localhost:8001/docs**

---

## API Endpoints

### Health Check
```http
GET /health
```
Returns service status and camera connectivity.

### Capture Image
```http
POST /capture
Content-Type: application/json

{
  "exposure": 100.0,  // optional, in milliseconds
  "gain": 1.0         // optional
}
```
Returns image metadata including filename, path, and settings.

### Get Camera Settings
```http
GET /settings
```
Returns current exposure, gain, resolution, and connection status.

### Update Camera Settings
```http
PUT /settings
Content-Type: application/json

{
  "exposure": 150.0,  // optional
  "gain": 2.0         // optional
}
```
Returns updated settings.

---

## How NestJS Calls This Service

The NestJS backend (`Nest/src/camera/camera.service.ts`) makes HTTP requests to this Python service:

```typescript
// NestJS camera.service.ts
@Injectable()
export class CameraService {
  private readonly baseUrl = 'http://localhost:8001';

  async capture(exposure?: number, gain?: number) {
    const { data } = await this.httpService.post(
      `${this.baseUrl}/capture`,
      { exposure, gain }
    );
    return data;
  }

  async getSettings() {
    const { data } = await this.httpService.get(`${this.baseUrl}/settings`);
    return data;
  }

  async updateSettings(settings: { exposure?: number; gain?: number }) {
    const { data } = await this.httpService.put(
      `${this.baseUrl}/settings`,
      settings
    );
    return data;
  }
}
```

The NestJS backend never talks to the camera directly - it always proxies through this Python service.

---

## How PixeLink SDK Works

### Key Concepts

1. **Initialize Camera**: Get a handle to control the camera
2. **Set Features**: Configure exposure, gain, etc.
3. **Start Streaming**: Put camera in capture mode
4. **Get Frame**: Retrieve raw image data
5. **Format Image**: Convert raw data to JPEG/BMP
6. **Stop Streaming**: Release camera
7. **Uninitialize**: Disconnect

### Code Examples

#### 1. Initialize Camera
```python
from pixelinkWrapper import PxLApi

# Initialize first available camera
ret = PxLApi.initialize(0)
if PxLApi.apiSuccess(ret[0]):
    camera_handle = ret[1]
    print(f"Camera connected: {camera_handle}")
```

#### 2. Set Exposure
```python
# Exposure in microseconds (100ms = 100,000µs)
exposure_us = 100.0 * 1000.0

ret = PxLApi.setFeature(
    camera_handle,
    PxLApi.FeatureId.EXPOSURE,
    PxLApi.FeatureFlags.MANUAL,
    [exposure_us]
)
```

#### 3. Set Gain
```python
ret = PxLApi.setFeature(
    camera_handle,
    PxLApi.FeatureId.GAIN,
    PxLApi.FeatureFlags.MANUAL,
    [1.5]  # Gain value
)
```

#### 4. Get Camera Settings
```python
# Get current exposure
ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.EXPOSURE)
if PxLApi.apiSuccess(ret[0]):
    exposure_us = ret[2][0]
    exposure_ms = exposure_us / 1000.0

# Get current gain
ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.GAIN)
if PxLApi.apiSuccess(ret[0]):
    gain = ret[2][0]

# Get resolution (ROI = Region of Interest)
ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.ROI)
if PxLApi.apiSuccess(ret[0]):
    width = int(ret[2][PxLApi.RoiParams.WIDTH])
    height = int(ret[2][PxLApi.RoiParams.HEIGHT])
```

#### 5. Capture Image
```python
from ctypes import create_string_buffer

# Calculate buffer size needed
def determine_raw_image_size(camera_handle):
    # Get ROI
    ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.ROI)
    roi_width = ret[2][PxLApi.RoiParams.WIDTH]
    roi_height = ret[2][PxLApi.RoiParams.HEIGHT]
    
    # Get pixel addressing (decimation/binning)
    ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.PIXEL_ADDRESSING)
    pixel_addr = ret[2][PxLApi.PixelAddressingParams.VALUE] if PxLApi.apiSuccess(ret[0]) else 1
    
    # Calculate pixel count
    num_pixels = (roi_width / pixel_addr) * (roi_height / pixel_addr)
    
    # Get bytes per pixel
    ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.PIXEL_FORMAT)
    pixel_format = int(ret[2][0])
    pixel_size = PxLApi.getBytesPerPixel(pixel_format)
    
    return int(num_pixels * pixel_size)

# Create buffer
raw_image_size = determine_raw_image_size(camera_handle)
raw_image = create_string_buffer(raw_image_size)

# Start streaming
PxLApi.setStreamState(camera_handle, PxLApi.StreamState.START)

# Get frame (blocking call - waits for camera)
ret = PxLApi.getNextFrame(camera_handle, raw_image)
if PxLApi.apiSuccess(ret[0]):
    frame_descriptor = ret[1]
    
    # Format to JPEG
    ret = PxLApi.formatImage(raw_image, frame_descriptor, PxLApi.ImageFormat.JPEG)
    if PxLApi.apiSuccess(ret[0]):
        jpeg_data = ret[1]
        
        # Save to file
        with open("capture.jpg", "wb") as f:
            f.write(jpeg_data)

# Stop streaming
PxLApi.setStreamState(camera_handle, PxLApi.StreamState.STOP)
```

#### 6. Disconnect Camera
```python
PxLApi.uninitialize(camera_handle)
```

---

## Project Structure

```
backend-python/
├── main.py                 # FastAPI app with HTTP endpoints
├── pixelink_camera.py      # PixeLink SDK wrapper class
├── config.py               # Configuration from .env
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── .env.example            # Configuration template
└── captures/               # Saved images directory
```

### File Responsibilities

**`main.py`**
- Defines FastAPI HTTP endpoints
- Handles requests from NestJS
- Validates input with Pydantic models
- Calls PixelinkCamera methods
- Returns JSON responses

**`pixelink_camera.py`**
- Wraps PixeLink SDK C API
- Manages camera lifecycle (init, uninit)
- Handles settings (exposure, gain)
- Captures images and saves to disk
- Falls back to simulation mode without SDK

**`config.py`**
- Loads configuration from `.env`
- Provides settings throughout app
- Handles CORS origins parsing

---

## Configuration

Edit `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=8001
DEBUG=True

# Camera
CAMERA_SERIAL_NUMBER=        # Empty = first camera
DEFAULT_EXPOSURE=100         # milliseconds
DEFAULT_GAIN=1.0
IMAGE_SAVE_PATH=./captures
IMAGE_FORMAT=jpg
IMAGE_QUALITY=95

# CORS (frontend URLs)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Simulation Mode

Without the PixeLink SDK installed, the service runs in **simulation mode**:

- All endpoints work normally
- Returns mock camera data
- Generates gradient test images
- Perfect for development/testing without hardware

To use real camera:
1. Install [PixeLink SDK](https://www.pixelink.com/)
2. Install Python bindings
3. Restart service - it will auto-detect camera

---

## Dependencies

```txt
fastapi>=0.109.0          # Web framework
uvicorn[standard]>=0.27.0 # ASGI server
pydantic>=2.5.0           # Data validation
pydantic-settings>=2.1.0  # Settings management
opencv-python>=4.8.0      # Image processing (for simulation)
numpy>=1.24.0             # Array operations (for simulation)
Pillow>=10.0.0            # Image handling (for simulation)
python-dotenv>=1.0.0      # .env file support
```

Install with: `pip install -r requirements.txt`

---

## Troubleshooting

**"Camera not connected"**
- Check PixeLink SDK is installed
- Verify camera is plugged into USB
- Check `CAMERA_SERIAL_NUMBER` in `.env`
- Service works in simulation mode without camera

**"Port 8001 already in use"**
- Change `PORT` in `.env`
- Or kill process using port 8001

**"CORS error" from frontend**
- Add frontend URL to `ALLOWED_ORIGINS` in `.env`
- Format: `http://localhost:5173,http://localhost:3000`

**"Module not found"**
```bash
pip install -r requirements.txt
```

---

## Testing

Start the service and test endpoints:

```bash
# Health check
curl http://localhost:8001/health

# Get settings
curl http://localhost:8001/settings

# Capture image
curl -X POST http://localhost:8001/capture \
  -H "Content-Type: application/json" \
  -d '{"exposure": 100.0, "gain": 1.0}'

# Update settings
curl -X PUT http://localhost:8001/settings \
  -H "Content-Type: application/json" \
  -d '{"exposure": 150.0, "gain": 2.0}'
```

Or use the interactive API docs: **http://localhost:8001/docs**

---

## Summary

This service provides a clean HTTP API layer over the PixeLink SDK, allowing your NestJS backend to control the camera without needing Python/SDK integration in TypeScript. It's minimal, focused, and does one thing well: camera control.
