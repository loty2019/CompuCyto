# Image Capture Flow Documentation

## Overview
This document describes the complete flow for capturing images from the Pixelink camera, from the frontend Vue component through the NestJS backend to the Python camera service, and finally storing metadata in the PostgreSQL database.

## Architecture

```
Frontend (Vue)
    ↓ HTTP POST
NestJS Backend (Port 3000)
    ↓ HTTP POST  
Python Camera Service (Port 8001)
    ↓ Pixelink SDK
Physical Camera
    ↓
Image File System Storage
    ↓
Database (PostgreSQL)
```

## Detailed Flow

### 1. Frontend Request (Vue)
**Location**: `frontend-vue/src/components/Camera.vue` or similar

```typescript
// Example API call from frontend
const response = await fetch('http://localhost:3000/api/v1/camera/capture', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    exposure: 100,  // Optional: milliseconds
    gain: 1.5       // Optional: gain value
  })
});

const result = await response.json();
```

**Request Format**:
```json
{
  "exposure": 100,
  "gain": 1.5
}
```

### 2. NestJS Backend Processing
**Location**: `Nest/src/camera/camera.controller.ts` → `Nest/src/camera/camera.service.ts`

#### Controller (`camera.controller.ts`)
- **Endpoint**: `POST /api/v1/camera/capture`
- **Authentication**: Requires JWT token (JwtAuthGuard)
- **Extracts**: User ID from JWT token
- **Validates**: Request body using CaptureDto

#### Service (`camera.service.ts`)
1. Forwards request to Python service at `http://localhost:8001/capture`
2. Waits for Python service response
3. Saves image metadata to database (images table)
4. Returns combined response to frontend

**Database Save**:
```typescript
const image = await imageRepository.save({
  userId: userId,           // From JWT token
  filename: 'capture_20250116_103045_123.jpg',
  capturedAt: '2025-01-16T10:30:45.123Z',
  exposureTime: 100,
  gain: 1.5,
  fileSize: 2456789,
  width: 1920,
  height: 1080,
  metadata: {
    format: 'JPG',
    quality: 95,
    cameraConnected: true,
    simulatedMode: false
  }
});
```

### 3. Python Camera Service
**Location**: `backend-python/main.py` → `backend-python/pixelink_camera.py`

#### API Endpoint (`main.py`)
- **Endpoint**: `POST /capture`
- **Port**: 8001
- **Request Body**:
  ```json
  {
    "exposure": 100,
    "gain": 1.5
  }
  ```

#### Camera Operations (`pixelink_camera.py`)

**Based on Sample Code**: `Sample_PixcelinkAPI_python/getNumPySnapshot.py`

##### Step 1: Update Settings (if provided)
```python
if exposure is not None:
    camera.update_settings(exposure=exposure)
if gain is not None:
    camera.update_settings(gain=gain)
```

##### Step 2: Determine Image Dimensions
```python
# Get ROI (Region of Interest)
ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.ROI)
roi_width = params[PxLApi.RoiParams.WIDTH]
roi_height = params[PxLApi.RoiParams.HEIGHT]

# Get pixel addressing (binning/decimation)
ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.PIXEL_ADDRESSING)

# Get pixel format
ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.PIXEL_FORMAT)
bytes_per_pixel = PxLApi.getBytesPerPixel(pixel_format)

# Calculate dimensions
width = int(roi_width / pixel_addressing_x)
height = int(roi_height / pixel_addressing_y)
```

##### Step 3: Create Image Buffer
```python
np_image = np.zeros([height, width * bytes_per_pixel], dtype=np.uint8)
```

##### Step 4: Start Streaming & Capture
```python
# Start streaming
PxLApi.setStreamState(camera_handle, PxLApi.StreamState.START)

# Capture with retries (blocking call)
MAX_RETRIES = 4
for attempt in range(MAX_RETRIES):
    ret = PxLApi.getNextNumPyFrame(camera_handle, np_image)
    if PxLApi.apiSuccess(ret[0]):
        break

# Stop streaming
PxLApi.setStreamState(camera_handle, PxLApi.StreamState.STOP)
```

##### Step 5: Format Image
```python
frame_descriptor = ret[1]
format_ret = PxLApi.formatNumPyImage(
    np_image, 
    frame_descriptor, 
    PxLApi.ImageFormat.RAW_RGB24
)
```

##### Step 6: Save to Disk
```python
# Convert to PIL Image and save
image = Image.fromarray(image_array)
image.save(filepath, quality=95)

# Get file metadata
file_size = filepath.stat().st_size
height, width = image_array.shape[:2]
```

##### Step 7: Return Response
```python
return {
    "success": True,
    "filename": "capture_20250116_103045_123.jpg",
    "filepath": "/path/to/captures/capture_20250116_103045_123.jpg",
    "capturedAt": "2025-01-16T10:30:45.123Z",
    "exposureTime": 100,
    "gain": 1.5,
    "fileSize": 2456789,
    "width": 1920,
    "height": 1080,
    "metadata": {
        "format": "JPG",
        "quality": 95,
        "cameraConnected": True,
        "simulatedMode": False
    }
}
```

### 4. Response Flow Back to Frontend

**NestJS Response** (after database save):
```json
{
  "success": true,
  "imageId": 123,
  "filename": "capture_20250116_103045_123.jpg",
  "filepath": "/path/to/captures/capture_20250116_103045_123.jpg",
  "capturedAt": "2025-01-16T10:30:45.123Z",
  "exposureTime": 100,
  "gain": 1.5,
  "fileSize": 2456789,
  "width": 1920,
  "height": 1080,
  "metadata": {
    "format": "JPG",
    "quality": 95,
    "cameraConnected": true,
    "simulatedMode": false
  },
  "databaseSaved": true
}
```

## Database Schema

**Table**: `images`

| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key (auto-increment) |
| job_id | integer | Associated job (nullable) |
| user_id | integer | User who captured the image |
| filename | string | Unique filename |
| thumbnail_path | string | Path to thumbnail (nullable) |
| captured_at | timestamp | When image was captured |
| x_position | float | Stage X position (nullable) |
| y_position | float | Stage Y position (nullable) |
| z_position | float | Stage Z position (nullable) |
| exposure_time | number | Exposure in milliseconds |
| gain | float | Gain/sensitivity value |
| file_size | number | File size in bytes |
| width | number | Image width in pixels |
| height | number | Image height in pixels |
| metadata | jsonb | Additional metadata |

**Indexes**:
- `(job_id, captured_at)`
- `(user_id, captured_at)`
- `captured_at`

## Error Handling

### Frontend
```typescript
try {
  const result = await captureImage();
  // Handle success
} catch (error) {
  if (error.status === 503) {
    console.error('Camera service unavailable');
  } else if (error.status === 500) {
    console.error('Camera error:', error.message);
  }
}
```

### NestJS
- Returns 503 if Python service is unreachable
- Returns 500 if capture fails
- Logs all errors for debugging

### Python Service
- Returns 503 if camera not initialized
- Returns 500 if capture fails
- Retries capture up to 4 times on timeout
- Works in simulated mode if hardware unavailable

## Mock/Simulated Mode

When the Pixelink SDK/hardware is not available, the system automatically operates in simulated mode:

**Python Service**:
```python
if PIXELINK_AVAILABLE and camera.is_connected:
    image_data = _capture_real_image()
else:
    image_data = _capture_simulated_image()  # Generates gradient test image
```

**Response Indicator**:
```json
{
  "metadata": {
    "cameraConnected": false,
    "simulatedMode": true
  }
}
```

## File Storage

**Default Location**: `backend-python/captures/`

**Filename Format**: `capture_YYYYMMDD_HHMMSS_mmm.jpg`
- Example: `capture_20250116_103045_123.jpg`

**Configuration** (`backend-python/.env`):
```env
IMAGE_SAVE_PATH=./captures
IMAGE_FORMAT=jpg
IMAGE_QUALITY=95
```

## Testing

### Test Python Service Directly
```bash
curl -X POST http://localhost:8001/capture \
  -H "Content-Type: application/json" \
  -d '{"exposure": 100, "gain": 1.5}'
```

### Test Through NestJS (requires auth token)
```bash
curl -X POST http://localhost:3000/api/v1/camera/capture \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exposure": 100, "gain": 1.5}'
```

### Health Check
```bash
curl http://localhost:8001/health
```

## Configuration

### Python Service (`backend-python/.env`)
```env
HOST=0.0.0.0
PORT=8001
DEBUG=True
CAMERA_SERIAL_NUMBER=
DEFAULT_EXPOSURE=100.0
DEFAULT_GAIN=1.0
IMAGE_SAVE_PATH=./captures
IMAGE_FORMAT=jpg
IMAGE_QUALITY=95
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### NestJS Backend (`.env`)
```env
PYTHON_CAMERA_URL=http://localhost:8001
SERVICE_TIMEOUT=30000
```

## Starting the Services

### Development Mode (All Services)
```bash
npm run dev
```

This starts:
- Frontend (Vue) on port 5173
- Backend (NestJS) on port 3000
- Python camera service on port 8001

### Individual Services
```bash
# Python camera service only
npm run dev:python

# NestJS backend only
npm run dev:backend

# Vue frontend only
npm run dev:frontend
```

## API Documentation

Once NestJS is running, access Swagger documentation at:
- http://localhost:3000/api/docs

This provides interactive API documentation with all endpoints, request/response schemas, and the ability to test endpoints directly from the browser.
