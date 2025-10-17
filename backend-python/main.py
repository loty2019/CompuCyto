"""
FastAPI Camera Service - Minimal Essential API
Provides HTTP endpoints for NestJS backend to control Pixelink camera
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from pixelink_camera import PixelinkCamera

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    
    logger.info(f"Setting default exposure: {settings.default_exposure}µs ({settings.default_exposure/1000}ms)")
    camera.update_settings(
        exposure=settings.default_exposure,
        gain=settings.default_gain
    )
    
    current_settings = camera.get_settings()
    logger.info(f"Camera initialized with exposure: {current_settings['exposure']}µs, gain: {current_settings['gain']}")
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
    exposure: Optional[float] = Field(None, ge=0, description="Exposure in microseconds (µs)")
    gain: Optional[float] = Field(None, ge=0, description="Gain value")


class SettingsUpdate(BaseModel):
    """Settings update request."""
    exposure: Optional[float] = Field(None, ge=0, description="Exposure in microseconds (µs)")
    gain: Optional[float] = Field(None, ge=0, description="Gain value")


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
            gain=request.gain
        )
        
        # Verify file was actually saved
        if filepath.exists():
            actual_size = filepath.stat().st_size
            logger.info(f"✅ Image saved to disk: {filepath}")
            logger.info(f"   File size: {actual_size} bytes ({actual_size / 1024:.2f} KB)")
            logger.info(f"   Dimensions: {result.get('width', 'unknown')}x{result.get('height', 'unknown')}")
        else:
            logger.error(f"❌ FILE NOT SAVED! Expected at: {filepath}")
        
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
    Called by NestJS camera.service.ts
    """
    if not camera or not camera.is_connected:
        raise HTTPException(status_code=503, detail="Camera not connected")
    
    try:
        updated = camera.update_settings(
            exposure=settings_update.exposure,
            gain=settings_update.gain
        )
        logger.info(f"Settings updated: {settings_update}")
        return updated
    except Exception as e:
        logger.error(f"Update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
