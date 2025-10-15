"""
Pixelink Camera Wrapper

Provides interface to Pixelink SDK for camera control
"""

import logging
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image

try:
    from pixelinkWrapper import PxLApi
    PIXELINK_AVAILABLE = True
except ImportError:
    PIXELINK_AVAILABLE = False

logger = logging.getLogger(__name__)


class PixelinkCamera:
    """Wrapper for PixeLink camera operations"""
    
    def __init__(self, serial_number: Optional[str] = None):
        self.serial_number = serial_number
        self.camera_handle = None
        self.is_connected = False
        self.is_streaming = False
        self.exposure = 100.0
        self.gain = 1.0
        self.width = 1280
        self.height = 1024
        
        if PIXELINK_AVAILABLE:
            self._initialize_camera()
    
    def _initialize_camera(self) -> bool:
        try:
            camera_id = int(self.serial_number) if self.serial_number else 0
            ret = PxLApi.initialize(camera_id)
            
            if PxLApi.apiSuccess(ret[0]):
                self.camera_handle = ret[1]
                self.is_connected = True
                logger.info("Camera initialized")
                self._load_current_settings()
                return True
            else:
                logger.error(f"Failed to initialize camera: {ret[0]}")
                return False
        except Exception as e:
            logger.error(f"Camera init error: {e}")
            return False
    
    def _load_current_settings(self):
        if not PIXELINK_AVAILABLE or not self.is_connected:
            return
        try:
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)
            if PxLApi.apiSuccess(ret[0]):
                self.exposure = ret[2][0] / 1000.0
            
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.GAIN)
            if PxLApi.apiSuccess(ret[0]):
                self.gain = ret[2][0]
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def get_settings(self) -> Dict:
        return {
            "exposure": self.exposure,
            "gain": self.gain,
            "resolution": {"width": self.width, "height": self.height},
            "connected": self.is_connected,
            "streaming": self.is_streaming
        }
    
    def update_settings(self, exposure: Optional[float] = None, gain: Optional[float] = None) -> Dict:
        if exposure is not None:
            self._set_exposure(exposure)
        if gain is not None:
            self._set_gain(gain)
        return self.get_settings()
    
    def _set_exposure(self, exposure_ms: float):
        if PIXELINK_AVAILABLE and self.is_connected:
            try:
                exposure_us = exposure_ms * 1000.0
                ret = PxLApi.setFeature(
                    self.camera_handle,
                    PxLApi.FeatureId.EXPOSURE,
                    PxLApi.FeatureFlags.MANUAL,
                    [exposure_us]
                )
                if PxLApi.apiSuccess(ret[0]):
                    self.exposure = exposure_ms
            except Exception as e:
                logger.error(f"Error setting exposure: {e}")
        else:
            self.exposure = exposure_ms
    
    def _set_gain(self, gain: float):
        if PIXELINK_AVAILABLE and self.is_connected:
            try:
                ret = PxLApi.setFeature(
                    self.camera_handle,
                    PxLApi.FeatureId.GAIN,
                    PxLApi.FeatureFlags.MANUAL,
                    [gain]
                )
                if PxLApi.apiSuccess(ret[0]):
                    self.gain = gain
            except Exception as e:
                logger.error(f"Error setting gain: {e}")
        else:
            self.gain = gain
    
    def capture_image(self, save_path: Path, exposure: Optional[float] = None, gain: Optional[float] = None) -> Dict:
        if exposure is not None or gain is not None:
            self.update_settings(exposure, gain)
        
        timestamp = datetime.now()
        
        if PIXELINK_AVAILABLE and self.is_connected:
            image_data = self._capture_real_image()
        else:
            image_data = self._capture_simulated_image()
        
        if image_data is None:
            raise RuntimeError("Failed to capture image")
        
        image = Image.fromarray(image_data)
        image.save(save_path, quality=95)
        
        return {
            "success": True,
            "filename": save_path.name,
            "filepath": str(save_path),
            "timestamp": timestamp.isoformat(),
            "settings": {
                "exposure": self.exposure,
                "gain": self.gain
            }
        }
    
    def _capture_real_image(self) -> Optional[np.ndarray]:
        try:
            ret = PxLApi.getNextFrame(self.camera_handle)
            if not PxLApi.apiSuccess(ret[0]):
                return None
            
            frame_descriptor = ret[1]
            frame_data = ret[2]
            
            ret = PxLApi.formatImage(frame_data, frame_descriptor, PxLApi.ImageFormat.RGB24)
            if not PxLApi.apiSuccess(ret[0]):
                return None
            
            rgb_data = ret[1]
            image_array = np.frombuffer(rgb_data, dtype=np.uint8)
            image_array = image_array.reshape((self.height, self.width, 3))
            return image_array
        except Exception as e:
            logger.error(f"Error capturing: {e}")
            return None
    
    def _capture_simulated_image(self) -> np.ndarray:
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for i in range(self.height):
            for j in range(self.width):
                image[i, j] = [
                    int(255 * i / self.height),
                    int(255 * j / self.width),
                    128
                ]
        return image
    
    def disconnect(self):
        if PIXELINK_AVAILABLE and self.is_connected:
            try:
                PxLApi.uninitialize(self.camera_handle)
                self.is_connected = False
                logger.info("Camera disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    def __del__(self):
        self.disconnect()
