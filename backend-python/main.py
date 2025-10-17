"""
FastAPI Camera Service - Minimal Essential API
Provides HTTP endpoints for NestJS backend to control Pixelink camera
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import settings
from pixelink_camera import PixelinkCamera
from camera_streamer import streamer

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO instead of DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Silence noisy loggers BEFORE they start
logging.getLogger('websockets.client').setLevel(logging.WARNING)
logging.getLogger('websockets.server').setLevel(logging.WARNING)
logging.getLogger('websockets.protocol').setLevel(logging.WARNING)
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
logging.getLogger('uvicorn.error').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# Global camera instance
camera: Optional[PixelinkCamera] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    global camera
    
    # Startup
    logger.info("Starting Camera Service on port 8001...")
    Path(settings.image_save_path).mkdir(parents=True, exist_ok=True)
    
    camera = PixelinkCamera(
        serial_number=settings.camera_serial_number if settings.camera_serial_number else None
    )
    
    logger.info(f"Setting default exposure: {settings.default_exposure}ms")
    camera.update_settings(
        exposure=settings.default_exposure,
        gain=settings.default_gain
    )
    
    current_settings = camera.get_settings()
    logger.info(f"Camera initialized - Exposure: {current_settings['exposure']}ms, Gain: {current_settings['gain']}")
    logger.info(f"   Exposure range: {current_settings['exposureMin']:.3f}ms - {current_settings['exposureMax']:.3f}ms")
    logger.info(f"   Gain range: {current_settings['gainMin']:.2f} - {current_settings['gainMax']:.2f}")
    
    # Initialize streamer with camera
    streamer.set_camera(
        camera.camera_handle,
        camera.width,
        camera.height
    )
    logger.info("Camera streamer initialized")
    logger.info("Camera service ready")
    yield
    
    # Shutdown
    if camera:
        camera.disconnect()
    logger.info("Camera service stopped")


app = FastAPI(
    title="Pixelink Camera Service",
    description="Camera control API for NestJS backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CaptureRequest(BaseModel):
    """Image capture request."""
    exposure: Optional[float] = Field(None, ge=0, description="Exposure in milliseconds (ms)")
    gain: Optional[float] = Field(None, ge=0, description="Gain value")
    gamma: Optional[float] = Field(None, ge=0, description="Gamma value")


class SettingsUpdate(BaseModel):
    """Settings update request."""
    exposure: Optional[float] = Field(None, ge=0, description="Exposure in milliseconds (ms)")
    gain: Optional[float] = Field(None, ge=0, description="Gain value")
    gamma: Optional[float] = Field(None, ge=0, description="Gamma value")
    autoExposure: Optional[bool] = Field(None, description="Enable/disable auto-exposure")


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "camera_connected": camera.is_connected if camera else False,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/captures/list")
async def list_captures():
    """List all captured images in the captures folder."""
    try:
        captures_path = Path(settings.image_save_path)
        if not captures_path.exists():
            return {"files": [], "count": 0, "path": str(captures_path)}
        
        files = []
        for file in sorted(captures_path.glob("*.jpg")):
            stat = file.stat()
            files.append({
                "filename": file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return {
            "files": files,
            "count": len(files),
            "path": str(captures_path.absolute())
        }
    except Exception as e:
        logger.error(f"Error listing captures: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/capture")
async def capture_image(request: CaptureRequest):
    """
    Capture image from camera.
    Called by NestJS camera.service.ts
    Returns metadata matching NestJS Image entity structure.
    """
    if not camera:
        raise HTTPException(status_code=503, detail="Camera not initialized")
    
    try:
        # Pause streaming to prevent conflicts
        streaming_was_active = streamer.is_streaming
        if streaming_was_active:
            await streamer.pause_streaming()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"capture_{timestamp}.{settings.image_format}"
        filepath = Path(settings.image_save_path) / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Capture image - returns metadata matching NestJS Image entity
        result = camera.capture_image(
            save_path=filepath,
            exposure=request.exposure,
            gain=request.gain,
            gamma=request.gamma
        )
        
        # Resume streaming if it was active
        if streaming_was_active:
            await streamer.resume_streaming()
        
        # Verify file was actually saved
        if filepath.exists():
            actual_size = filepath.stat().st_size
            logger.info(f"Image saved to disk: {filepath}")
            logger.info(f"   File size: {actual_size} bytes ({actual_size / 1024:.2f} KB)")
            logger.info(f"   Dimensions: {result.get('width', 'unknown')}x{result.get('height', 'unknown')}")
        else:
            logger.error(f"FILE NOT SAVED! Expected at: {filepath}")
        
        logger.info(f"Image captured: {filename} (size: {result.get('fileSize', 0)} bytes)")
        
        # Return response matching what NestJS camera.service.ts expects
        return {
            "success": result["success"],
            "filename": result["filename"],
            "filepath": result["filepath"],
            "capturedAt": result["capturedAt"],
            "exposureTime": result["exposureTime"],
            "gain": result["gain"],
            "fileSize": result["fileSize"],
            "width": result["width"],
            "height": result["height"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        # Make sure to resume streaming even if capture fails
        if streaming_was_active:
            await streamer.resume_streaming()
        logger.error(f"Capture error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Capture failed: {str(e)}")


@app.get("/settings")
async def get_settings():
    """
    Get current camera settings.
    Called by NestJS camera.service.ts
    """
    if not camera:
        raise HTTPException(status_code=503, detail="Camera not initialized")
    
    return camera.get_settings()


@app.put("/settings")
async def update_settings(settings_update: SettingsUpdate):
    """
    Update camera settings.
    Called by NestJS camera.service.ts or frontend
    """
    if not camera or not camera.is_connected:
        raise HTTPException(status_code=503, detail="Camera not connected")
    
    try:
        updated = camera.update_settings(
            exposure=settings_update.exposure,
            gain=settings_update.gain,
            gamma=settings_update.gamma,
            auto_exposure=settings_update.autoExposure
        )
        logger.info(f"Settings updated: {settings_update}")
        return updated
    except Exception as e:
        logger.error(f"Update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/settings/auto-exposure/once")
async def perform_auto_exposure_once():
    """
    Perform a one-time auto-exposure adjustment.
    Camera will automatically determine optimal exposure, then return to manual control.
    """
    if not camera or not camera.is_connected:
        raise HTTPException(status_code=503, detail="Camera not connected")
    
    try:
        success = camera.perform_one_time_auto_exposure()
        if success:
            settings = camera.get_settings()
            return {
                "success": True,
                "message": "One-time auto-exposure completed",
                "exposure": settings["exposure"],
                "gain": settings["gain"]
            }
        else:
            raise HTTPException(status_code=500, detail="One-time auto-exposure failed or timed out")
    except Exception as e:
        logger.error(f"Auto-exposure error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/camera/stream")
async def websocket_camera_stream(websocket: WebSocket):
    """
    WebSocket endpoint for live camera streaming.
    Streams JPEG frames as base64-encoded JSON messages.
    
    Called by frontend to receive live camera feed.
    Multiple clients can connect simultaneously.
    """
    await websocket.accept()
    client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
    logger.info(f"🔌 WebSocket client connected from {client_info}")
    
    try:
        # Register this client with the streamer
        await streamer.add_client(websocket)
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Camera stream connected",
            "resolution": {"width": camera.width, "height": camera.height}
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client (like settings updates, close, etc.)
            try:
                data = await websocket.receive_text()
                # Handle client messages if needed
                logger.debug(f"Received from client: {data}")
            except WebSocketDisconnect:
                logger.info(f"🔌 WebSocket client {client_info} disconnected (receive)")
                break
            except Exception as e:
                logger.warning(f"Error receiving from client {client_info}: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket client {client_info} disconnected normally")
    except Exception as e:
        logger.error(f"❌ WebSocket error for client {client_info}: {e}", exc_info=True)
    finally:
        # Unregister client
        await streamer.remove_client(websocket)
        logger.info(f"✅ WebSocket client {client_info} removed. Active clients: {len(streamer.active_clients)}")


# Mount static files for captured images
# IMPORTANT: This must come AFTER all API endpoints to avoid conflicts
# Now accessible via http://localhost:8001/captures/filename.jpg
captures_path = Path(settings.image_save_path)
app.mount("/captures", StaticFiles(directory=str(captures_path)), name="captures")
logger.info(f"📁 Static files mounted: /captures -> {captures_path.absolute()}")


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Disable reload to reduce noise
        log_level="info",  # Force INFO level
        access_log=False  # Disable access logs
    )
