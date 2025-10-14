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
    camera.update_settings(
        exposure=settings.default_exposure,
        gain=settings.default_gain
    )
    
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
    exposure: Optional[float] = Field(None, ge=0, description="Exposure in ms")
    gain: Optional[float] = Field(None, ge=0, description="Gain value")


class SettingsUpdate(BaseModel):
    """Settings update request."""
    exposure: Optional[float] = Field(None, ge=0, description="Exposure in ms")
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


@app.post("/capture")
async def capture_image(request: CaptureRequest):
    """
    Capture image from camera.
    Called by NestJS camera.service.ts
    """
    if not camera or not camera.is_connected:
        raise HTTPException(status_code=503, detail="Camera not connected")
    
    try:
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"capture_{timestamp}.{settings.image_format}"
        filepath = Path(settings.image_save_path) / filename
        
        # Capture image
        result = camera.capture_image(
            save_path=filepath,
            exposure=request.exposure,
            gain=request.gain
        )
        
        logger.info(f"Image captured: {filename}")
        return result
        
    except Exception as e:
        logger.error(f"Capture error: {e}")
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
