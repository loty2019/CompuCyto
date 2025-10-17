# Camera Live Streaming Setup

## Overview

The live camera feed uses **WebSocket** for real-time streaming from the Python backend to the Vue frontend.

## Architecture

```
┌─────────────────┐         WebSocket          ┌──────────────────┐
│  Vue Frontend   │ ←─────────────────────────→ │  Python Backend  │
│ CameraControl   │   ws://localhost:8001/ws    │  camera_streamer │
└─────────────────┘                             └──────────────────┘
                                                         ↓
                                                 ┌──────────────┐
                                                 │ PixeLink SDK │
                                                 │   Camera     │
                                                 └──────────────┘
```

## Components

### Backend (Python FastAPI)

#### 1. **camera_streamer.py** - Core Streaming Logic

- `CameraStreamer` class manages continuous frame capture
- Uses `PxLApi.getNextFrame` in async loop
- Supports multiple WebSocket clients simultaneously
- Auto-starts/stops streaming based on connected clients
- Frame rate: ~30 FPS

**Key Methods:**

- `start_streaming()` - Begins frame capture loop
- `stop_streaming()` - Stops frame capture
- `add_client(websocket)` - Registers new WebSocket connection
- `remove_client(websocket)` - Unregisters client
- `_capture_real_frame()` - Gets frame from PixeLink camera
- `_encode_jpeg()` - Encodes frame as JPEG
- `_broadcast_frame()` - Sends frame to all clients

#### 2. **main.py** - WebSocket Endpoint

```python
@app.websocket("/ws/camera/stream")
async def websocket_camera_stream(websocket: WebSocket):
    # Handles WebSocket connections
    # Registers client with streamer
    # Keeps connection alive
```

**WebSocket Message Format:**

```json
{
  "type": "frame",
  "data": "base64_encoded_jpeg_data",
  "timestamp": 1234567890.123
}
```

### Frontend (Vue 3)

#### **CameraControl.vue** - Live Feed Display

- Connects to WebSocket on mount
- Displays base64 JPEG frames in `<img>` tag
- Auto-reconnects on disconnect (3 second delay)
- Shows loading/error states

**Key Features:**

- Auto-connect on component mount
- Connection status indicators
- Manual reconnect button
- Graceful cleanup on unmount

## Setup Instructions

### 1. Backend Setup

**Install Dependencies:**

```bash
cd backend-python
pip install -r requirements.txt
```

**Start Python Service:**

```bash
python main.py
```

Service runs on: `http://localhost:8001`
WebSocket endpoint: `ws://localhost:8001/ws/camera/stream`

### 2. Frontend Setup

**Environment Configuration:**
Create/update `.env` in `frontend-vue/`:

```env
VITE_API_BASE_URL=http://localhost:3000
```

The frontend automatically converts this to WebSocket URL and adjusts port to 8001.

**Start Vue Dev Server:**

```bash
cd frontend-vue
npm run dev
```

## How It Works

### Streaming Flow

1. **Frontend connects** to WebSocket
2. **Backend accepts** connection and registers client
3. **Streamer starts** (if first client)
4. **Camera begins** continuous frame capture:
   - Calls `PxLApi.setStreamState(START)`
   - Loops: `getNextFrame()` → Encode JPEG → Broadcast
5. **Frontend receives** base64 JPEG frames
6. **Updates** `<img src="data:image/jpeg;base64,...">`
7. **Display updates** at ~30 FPS

### Multiple Clients

- Streamer maintains a set of active WebSocket connections
- Each frame is broadcast to all connected clients
- Streaming stops automatically when last client disconnects
- Efficient: Camera captures once, sends to many clients

## Troubleshooting

### Issue: "Connection error - check if Python camera service is running"

**Solution:** Ensure Python backend is running on port 8001

```bash
cd backend-python
python main.py
```

### Issue: Simulated/Test Pattern Instead of Camera

**Causes:**

- PixeLink SDK not installed
- Camera not connected
- Camera in use by another application

**Check logs:**

```
⚠️ PixeLink SDK not available - running in SIMULATED mode
```

### Issue: WebSocket Keeps Reconnecting

**Causes:**

- Python service crashed
- Network/CORS issues
- Port 8001 blocked

**Debug:**

1. Check Python service logs
2. Test WebSocket manually: `wscat -c ws://localhost:8001/ws/camera/stream`
3. Check browser DevTools → Network → WS

### Issue: Low Frame Rate / Laggy

**Solutions:**

- Reduce JPEG quality in `camera_streamer.py` (line ~273):
  ```python
  jpeg_data = await asyncio.to_thread(self._encode_jpeg, frame_data, quality=70)
  ```
- Increase frame delay (line ~333):
  ```python
  await asyncio.sleep(0.050)  # 20 FPS instead of 30
  ```
- Reduce camera resolution

## Configuration

### Adjust Frame Rate

**File:** `backend-python/camera_streamer.py`

```python
# Line ~333 in _stream_loop()
await asyncio.sleep(0.033)  # 30 FPS (1/30 = 0.033)
await asyncio.sleep(0.050)  # 20 FPS
await asyncio.sleep(0.100)  # 10 FPS
```

### Adjust JPEG Quality

**File:** `backend-python/camera_streamer.py`

```python
# Line ~273 in _encode_jpeg()
image.save(buffer, format='JPEG', quality=85)  # 1-95, higher = better quality
```

### Adjust Reconnection Delay

**File:** `frontend-vue/src/components/CameraControl.vue`

```javascript
// Line ~192
reconnectTimeout = setTimeout(() => {
  startFeed();
}, 3000); // 3 seconds
```

## API Endpoints

### WebSocket

- **URL:** `ws://localhost:8001/ws/camera/stream`
- **Protocol:** WebSocket
- **Message Format:** JSON with base64 JPEG data
- **Auto-reconnect:** Yes (3 second delay)

### HTTP (Existing)

- `POST /capture` - Capture still image
- `GET /settings` - Get camera settings
- `PUT /settings` - Update camera settings
- `GET /health` - Health check

## Performance

- **Frame Rate:** ~30 FPS
- **Resolution:** 1280x1024 (configurable)
- **Latency:** <100ms (local network)
- **Bandwidth:** ~2-5 Mbps per client (depends on JPEG quality)
- **Max Clients:** Limited by server resources (tested up to 10)

## Future Enhancements

Potential improvements:

- [ ] H.264 video encoding for lower bandwidth
- [ ] Adaptive quality based on network conditions
- [ ] Client-side buffering for smoother playback
- [ ] Frame rate synchronization across clients
- [ ] Streaming statistics (FPS, bandwidth, latency)
- [ ] WebRTC for peer-to-peer streaming
