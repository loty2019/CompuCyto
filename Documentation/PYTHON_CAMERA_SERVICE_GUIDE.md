# Python Camera Service Guide

## Overview

The Python Camera Service is a FastAPI-based microservice that provides HTTP endpoints for controlling the PixeLink camera. It runs on port **8001** and communicates with the NestJS backend (port 3000).

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│  Vue Frontend   │────────▶│  NestJS Backend  │────────▶│   Python    │
│  (Port 5173)    │  HTTP   │   (Port 3000)    │  HTTP   │   Camera    │
│                 │◀────────│                  │◀────────│ (Port 8001) │
└─────────────────┘         └──────────────────┘         └─────────────┘
                                                                 │
                                                                 ▼
                                                          ┌─────────────┐
                                                          │  PixeLink   │
                                                          │   Camera    │
                                                          │  Hardware   │
                                                          └─────────────┘
```

---

## Architecture

### Key Components

1. **main.py** - FastAPI application with HTTP endpoints
2. **pixelink_camera.py** - Camera wrapper class for PixeLink SDK
3. **config.py** - Configuration management with environment variables

### Technology Stack

- **FastAPI** - Modern Python web framework
- **PixeLink SDK** - Native camera control library
- **Pillow (PIL)** - Image processing
- **NumPy** - Array manipulation for image data
- **Uvicorn** - ASGI server

---

## How It Works

### 1. Camera Initialization

When the service starts, it initializes the camera with a workaround for Windows `wmic` deprecation:

```python
# pixelink_camera.py

# Fix for wmic error in pixelinkWrapper on newer Windows versions
try:
    from pixelinkWrapper import PxLApi
    PIXELINK_AVAILABLE = True
except Exception as e:
    # Try alternative import with subprocess workaround
    import subprocess
    original_check_output = subprocess.check_output
    
    def patched_check_output(*args, **kwargs):
        try:
            return original_check_output(*args, **kwargs)
        except FileNotFoundError:
            # Return dummy version if wmic fails
            return b"10.0.0"
    
    subprocess.check_output = patched_check_output
    from pixelinkWrapper import PxLApi
    subprocess.check_output = original_check_output
    PIXELINK_AVAILABLE = True
```

**Why this matters:** Newer Windows versions removed `wmic.exe`, which the PixeLink SDK tries to use. This workaround patches the subprocess call to return a dummy version instead of failing.

### 2. Startup Sequence

```python
# main.py - Application lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    global camera
    
    # 1. Create captures directory
    Path(settings.image_save_path).mkdir(parents=True, exist_ok=True)
    
    # 2. Initialize camera (connects to first available if no serial specified)
    camera = PixelinkCamera(
        serial_number=settings.camera_serial_number if settings.camera_serial_number else None
    )
    
    # 3. Set default camera settings
    camera.update_settings(
        exposure=settings.default_exposure,  # 100,000 µs = 100ms
        gain=settings.default_gain           # 1.0
    )
    
    yield  # Application runs
    
    # Cleanup on shutdown
    if camera:
        camera.disconnect()
```

### 3. Camera Settings

The camera uses **microseconds (µs)** for exposure time, stored as integers for database compatibility.

```python
# Camera state
self.exposure = 100000    # 100ms = 100,000 microseconds (integer)
self.gain = 1.0          # Gain multiplier (float)
self.width = 1280        # Image width in pixels
self.height = 1024       # Image height in pixels
```

**Important:** Exposure is stored in microseconds as an integer to match:
- PixeLink SDK native format
- PostgreSQL integer column type in the database

---

## API Endpoints

### GET /health

Health check endpoint to verify service and camera status.

```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "camera_connected": true,
  "timestamp": "2025-10-17T01:00:00.000000"
}
```

### GET /settings

Get current camera settings.

```bash
curl http://localhost:8001/settings
```

**Response:**
```json
{
  "exposure": 3096,
  "gain": 1.0,
  "resolution": {
    "width": 1280,
    "height": 1024
  },
  "connected": true,
  "streaming": false
}
```

### PUT /settings

Update camera settings.

```bash
curl -X PUT http://localhost:8001/settings \
  -H "Content-Type: application/json" \
  -d '{
    "exposure": 50000,
    "gain": 2.0
  }'
```

**Parameters:**
- `exposure` - Exposure time in microseconds (µs)
- `gain` - Gain multiplier

### POST /capture

Capture an image from the camera.

```bash
curl -X POST http://localhost:8001/capture \
  -H "Content-Type: application/json" \
  -d '{
    "exposure": 10000,
    "gain": 1.5
  }'
```

**Parameters (optional):**
- `exposure` - Override exposure for this capture only
- `gain` - Override gain for this capture only

**Response:**
```json
{
  "success": true,
  "filename": "capture_20251017_010844_829.jpg",
  "filepath": "C:\\Users\\loren\\Desktop\\CompuCyto\\backend-python\\captures\\capture_20251017_010844_829.jpg",
  "capturedAt": "2025-10-17T01:08:44.829935",
  "exposureTime": 3096,
  "gain": 1.0,
  "fileSize": 183711,
  "width": 1280,
  "height": 1024,
  "metadata": {
    "format": "JPG",
    "quality": 95,
    "cameraConnected": true,
    "simulatedMode": false
  }
}
```

### GET /captures/list

List all captured images.

```bash
curl http://localhost:8001/captures/list
```

**Response:**
```json
{
  "files": [
    {
      "filename": "capture_20251017_010844_829.jpg",
      "size": 183711,
      "modified": "2025-10-17T01:08:44.829935"
    }
  ],
  "count": 1,
  "path": "C:\\Users\\loren\\Desktop\\CompuCyto\\backend-python\\captures"
}
```

---

## Image Capture Flow

### Step-by-Step Process

```python
def capture_image(self, save_path: Path, exposure: Optional[float] = None, 
                  gain: Optional[float] = None) -> Dict:
    """
    Complete image capture workflow
    """
    
    # 1. Update settings if provided
    if exposure is not None or gain is not None:
        self.update_settings(exposure, gain)
    
    # 2. Capture image (real or simulated)
    if PIXELINK_AVAILABLE and self.is_connected:
        image_data = self._capture_real_image()  # NumPy array
    else:
        image_data = self._capture_simulated_image()  # Fallback
    
    # 3. Convert to PIL Image and save
    image = Image.fromarray(image_data)
    image.save(save_path, quality=95)
    
    # 4. Return metadata matching NestJS Image entity
    return {
        "success": True,
        "filename": save_path.name,
        "filepath": str(save_path.absolute()),
        "capturedAt": timestamp.isoformat(),
        "exposureTime": self.exposure,  # Integer in microseconds
        "gain": self.gain,
        "fileSize": save_path.stat().st_size,
        "width": width,
        "height": height,
        "metadata": {
            "format": "JPG",
            "quality": 95,
            "cameraConnected": self.is_connected,
            "simulatedMode": not (PIXELINK_AVAILABLE and self.is_connected)
        }
    }
```

### Real Camera Capture

The real camera capture uses the PixeLink SDK's NumPy integration:

```python
def _capture_real_image(self) -> Optional[np.ndarray]:
    """
    Capture from real PixeLink camera
    Based on PixeLink SDK sample: getNumPySnapshot.py
    """
    
    # 1. Determine image dimensions from camera ROI
    width, height, bytes_per_pixel = self._determine_raw_image_size()
    
    # 2. Create NumPy buffer for raw image
    np_image = np.zeros([height, width * bytes_per_pixel], dtype=np.uint8)
    
    # 3. Start streaming
    PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
    
    # 4. Get frame (with retries for hardware triggering)
    for attempt in range(MAX_RETRIES):
        ret = PxLApi.getNextNumPyFrame(self.camera_handle, np_image)
        if PxLApi.apiSuccess(ret[0]):
            break
    
    # 5. Stop streaming
    PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)
    
    # 6. Format as RGB
    frame_descriptor = ret[1]
    format_ret = PxLApi.formatNumPyImage(np_image, frame_descriptor, 
                                         PxLApi.ImageFormat.RAW_RGB24)
    
    # 7. Reshape to proper dimensions
    rgb_data = format_ret[1]
    image_array = np.frombuffer(rgb_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, 3))
    
    return image_array
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend-python` directory:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=True

# Camera Configuration
CAMERA_SERIAL_NUMBER=        # Empty = use first available camera
DEFAULT_EXPOSURE=100000.0    # Microseconds (100ms)
DEFAULT_GAIN=1.0
IMAGE_SAVE_PATH=./captures
IMAGE_FORMAT=jpg
IMAGE_QUALITY=95

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Settings Class

```python
# config.py

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    # Camera Configuration
    camera_serial_number: str = ""
    default_exposure: float = 100000.0  # microseconds
    default_gain: float = 1.0
    image_save_path: str = "./captures"
    image_format: str = "jpg"
    image_quality: int = 95
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

## Exposure Time Units

### Understanding Microseconds

The camera uses **microseconds (µs)** for precise exposure control:

| Microseconds | Milliseconds | Seconds | Description |
|--------------|--------------|---------|-------------|
| 1,000 µs | 1 ms | 0.001 s | Very fast exposure |
| 10,000 µs | 10 ms | 0.01 s | Fast exposure |
| 100,000 µs | 100 ms | 0.1 s | Moderate exposure (default) |
| 1,000,000 µs | 1,000 ms | 1 s | Long exposure |

### Conversion Examples

```python
# Convert milliseconds to microseconds
exposure_ms = 100  # 100 milliseconds
exposure_us = exposure_ms * 1000  # 100,000 microseconds

# Convert seconds to microseconds
exposure_s = 0.1  # 0.1 seconds
exposure_us = exposure_s * 1000000  # 100,000 microseconds

# Format for display
exposure_us = 3096
print(f"{exposure_us}µs = {exposure_us/1000}ms = {exposure_us/1000000}s")
# Output: 3096µs = 3.096ms = 0.003096s
```

---

## Error Handling

### Common Issues and Solutions

#### 1. PixeLink SDK Not Found

**Error:**
```
WARNING: PixeLink SDK not available: [WinError 2] The system cannot find the file specified
```

**Solution:**
The wmic workaround handles this automatically. Ensure:
- PixeLink SDK is installed
- DLLs are in system PATH or `C:\Program Files (x86)\PixeLINK\bin\x86\`

#### 2. Camera Not Connected

**Error:**
```
ERROR: Could not initialize camera. Error code: [error_code]
```

**Solution:**
- Check camera USB connection
- Verify camera power
- Ensure no other application is using the camera
- Check camera serial number in config

#### 3. Exposure Out of Range

**Warning:**
```
WARNING: Camera rejected exposure 100000µs (error -2147483645), keeping current: 3096µs
```

**Solution:**
The camera has valid exposure ranges. The code automatically keeps the camera's current valid exposure. Check your camera's specifications for supported ranges.

#### 4. Database Integer Error

**Error:**
```
ERROR: invalid input syntax for type integer: "0.0000030968005303293465"
```

**Solution:**
This was fixed by storing exposure as integer microseconds instead of float milliseconds:
```python
# Before (caused error)
self.exposure = ret[2][0] / 1000.0  # Float in milliseconds

# After (works correctly)
self.exposure = int(ret[2][0])  # Integer in microseconds
```

---

## NestJS Integration

### How NestJS Calls the Python Service

```typescript
// Nest/src/camera/camera.service.ts

async captureImage(exposure?: number, gain?: number): Promise<Image> {
  // 1. Call Python service
  const response = await axios.post('http://localhost:8001/capture', {
    exposure,  // Optional: microseconds
    gain       // Optional: gain value
  });
  
  // 2. Create database record
  const image = this.imageRepository.create({
    userId: 1,  // Current user
    jobId: null,
    filename: response.data.filename,
    capturedAt: new Date(response.data.capturedAt),
    exposureTime: response.data.exposureTime,  // Integer in µs
    gain: response.data.gain,
    fileSize: response.data.fileSize,
    width: response.data.width,
    height: response.data.height,
    metadata: response.data.metadata
  });
  
  // 3. Save to database
  return await this.imageRepository.save(image);
}
```

### Database Schema

```typescript
// Image entity fields
@Column({ name: 'exposure_time', nullable: true })
exposureTime: number;  // Integer in microseconds

@Column({ type: 'float', nullable: true })
gain: number;

@Column({ name: 'file_size', nullable: true })
fileSize: number;
```

---

## Running the Service

### Development Mode

```bash
cd backend-python
python main.py
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [67890]
INFO:     Application startup complete.
```

### Production Mode

```bash
cd backend-python
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1
```

**Note:** Use `--workers 1` because the camera hardware can only be accessed by one process.

---

## Testing

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8001/health

# Get settings
curl http://localhost:8001/settings

# Capture image with default settings
curl -X POST http://localhost:8001/capture \
  -H "Content-Type: application/json" \
  -d '{}'

# Capture with custom exposure
curl -X POST http://localhost:8001/capture \
  -H "Content-Type: application/json" \
  -d '{"exposure": 50000, "gain": 1.5}'

# List captured images
curl http://localhost:8001/captures/list
```

### Testing from Python

```python
import requests

# Capture image
response = requests.post('http://localhost:8001/capture', json={
    'exposure': 50000,  # 50ms
    'gain': 1.5
})

data = response.json()
print(f"Captured: {data['filename']}")
print(f"Size: {data['fileSize']} bytes")
print(f"Exposure: {data['exposureTime']}µs")
```

---

## Troubleshooting

### Check Camera Connection

```python
import requests
response = requests.get('http://localhost:8001/health')
print(response.json())
# {'status': 'healthy', 'camera_connected': true, ...}
```

### View Service Logs

Look for these key log messages:

```
✓ Good signs:
INFO:     Application startup complete.
WARNING:pixelink_camera:Camera rejected exposure 100000µs, keeping current: 3096µs
INFO:pixelink_camera:✓ Exposure set to 3096µs

✗ Problem signs:
ERROR:pixelink_camera:Failed to initialize camera
WARNING:pixelink_camera:⚠️ PixeLink SDK not available - running in SIMULATED mode
```

### Verify Image Files

```bash
# Check captures directory
ls -lh backend-python/captures/

# Verify image is valid
file backend-python/captures/capture_*.jpg
# Should output: JPEG image data...
```

---

## Key Takeaways

1. **Exposure units:** Always use **microseconds as integers** (e.g., `100000` = 100ms)
2. **wmic workaround:** Required for Windows 11+ compatibility
3. **Single worker:** Camera hardware can only be accessed by one process
4. **Real vs Simulated:** Check `simulatedMode` in response metadata
5. **Error handling:** Camera automatically keeps valid exposure if requested value is out of range

---

## Quick Reference

| Feature | Value | Notes |
|---------|-------|-------|
| Service Port | 8001 | HTTP API |
| Default Exposure | 100,000 µs | 100 milliseconds |
| Default Gain | 1.0 | No amplification |
| Image Format | JPEG | 95% quality |
| Image Resolution | 1280×1024 | Camera dependent |
| Captures Path | `./captures/` | Configurable |

---

## Additional Resources

- [PixeLink SDK Documentation](https://pixelink.com/support/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Project Documentation](../Documentation/)
  - `SYSTEM_ARCHITECTURE.md` - Overall system design
  - `IMAGE_CAPTURE_FLOW.md` - Detailed capture workflow
  - `QUICK_COMMUNICATION_GUIDE.md` - Service communication patterns
