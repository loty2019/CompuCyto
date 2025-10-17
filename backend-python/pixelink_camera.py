"""
Pixelink Camera Wrapper

Provides interface to Pixelink SDK for camera control
"""

import logging
import os
import sys
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image

# Fix for wmic error in pixelinkWrapper on newer Windows versions
try:
    from pixelinkWrapper import PxLApi
    PIXELINK_AVAILABLE = True
except Exception as e:
    logging.warning(f"Error importing pixelinkWrapper: {e}")
    logging.warning("Trying alternative import method...")
    try:
        # Try to import with subprocess workaround
        import subprocess
        original_check_output = subprocess.check_output
        
        def patched_check_output(*args, **kwargs):
            try:
                return original_check_output(*args, **kwargs)
            except FileNotFoundError:
                # Return a dummy version string if wmic fails
                return b"10.0.0"
        
        subprocess.check_output = patched_check_output
        from pixelinkWrapper import PxLApi
        subprocess.check_output = original_check_output
        PIXELINK_AVAILABLE = True
        logging.info("Successfully imported pixelinkWrapper with workaround")
    except Exception as e2:
        PIXELINK_AVAILABLE = False
        logging.warning(f"Alternative import also failed: {e2}. Running in mock mode.")
        PxLApi = None

logger = logging.getLogger(__name__)


class PixelinkCamera:
    """Wrapper for PixeLink camera operations"""
    
    def __init__(self, serial_number: Optional[str] = None):
        self.serial_number = serial_number
        self.camera_handle = None
        self.is_connected = False
        self.is_streaming = False
        self.exposure = 100000  # Default 100ms (stored as microseconds: 100,000 µs)
        self.gain = 1.0
        self.width = 1280
        self.height = 1024
        
        logger.info(f"PixelinkCamera initializing... PIXELINK_AVAILABLE={PIXELINK_AVAILABLE}")
        
        if PIXELINK_AVAILABLE:
            self._initialize_camera()
        else:
            logger.warning("⚠️ PixeLink SDK not available - running in SIMULATED mode")
            logger.warning("   Install pixelinkWrapper to use real camera")
    
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
                params = ret[2]
                raw_exposure = params[0]
                logger.info(f"Camera raw exposure value: {raw_exposure} (type: {type(raw_exposure).__name__})")
                
                # Store exposure in microseconds (integer) for database compatibility  
                self.exposure = int(raw_exposure) if raw_exposure >= 1 else int(raw_exposure * 1000000)
                
                # Log exposure info
                logger.info(f"Current exposure: {self.exposure}µs ({self.exposure/1000}ms)")
                if len(params) > 2:
                    logger.info(f"Exposure range: min={params[1]}µs, max={params[2]}µs")
            
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
    
    def _set_exposure(self, exposure_us: float):
        """Set exposure time in microseconds"""
        if PIXELINK_AVAILABLE and self.is_connected:
            try:
                # Just use the current exposure if none specified or if the value is invalid
                # The camera will reject invalid values, so we'll just use what it currently has
                logger.info(f"Attempting to set exposure to {exposure_us}µs")
                
                ret = PxLApi.setFeature(
                    self.camera_handle,
                    PxLApi.FeatureId.EXPOSURE,
                    PxLApi.FeatureFlags.MANUAL,
                    [float(exposure_us)]
                )
                
                if PxLApi.apiSuccess(ret[0]):
                    self.exposure = int(exposure_us)
                    logger.info(f"✓ Exposure successfully set to {self.exposure}µs ({self.exposure/1000}ms)")
                else:
                    # If it fails, just keep the current exposure setting
                    logger.warning(f"Camera rejected exposure {exposure_us}µs (error {ret[0]}), keeping current: {self.exposure}µs")
            except Exception as e:
                logger.error(f"Error setting exposure: {e}")
        else:
            self.exposure = int(exposure_us)
    
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
        """
        Capture an image and save it to disk.
        Returns metadata matching NestJS Image entity structure.
        """
        # Update settings if provided
        if exposure is not None or gain is not None:
            self.update_settings(exposure, gain)
        
        timestamp = datetime.now()
        
        # Capture image (real or simulated)
        logger.info(f"🎥 Capture attempt - SDK Available: {PIXELINK_AVAILABLE}, Camera Connected: {self.is_connected}")
        if PIXELINK_AVAILABLE and self.is_connected:
            logger.info("📸 Using REAL camera")
            image_data = self._capture_real_image()
        else:
            logger.warning("⚠️ Using SIMULATED image - check camera connection!")
            if not PIXELINK_AVAILABLE:
                logger.warning("   Reason: PixeLink SDK not available")
            if not self.is_connected:
                logger.warning("   Reason: Camera not connected")
            image_data = self._capture_simulated_image()
        
        if image_data is None:
            raise RuntimeError("Failed to capture image")
        
        # Save image to disk
        image = Image.fromarray(image_data)
        image.save(save_path, quality=95)
        
        # Get file size and dimensions
        file_size = save_path.stat().st_size if save_path.exists() else 0
        height, width = image_data.shape[:2]
        
        # Return metadata matching NestJS Image entity
        return {
            "success": True,
            "filename": save_path.name,
            "filepath": str(save_path.absolute()),
            "capturedAt": timestamp.isoformat(),
            "exposureTime": self.exposure,
            "gain": self.gain,
            "fileSize": file_size,
            "width": width,
            "height": height,
            "metadata": {
                "format": save_path.suffix.upper().replace('.', ''),
                "quality": 95,
                "cameraConnected": self.is_connected,
                "simulatedMode": not (PIXELINK_AVAILABLE and self.is_connected)
            }
        }
    
    def _capture_real_image(self) -> Optional[np.ndarray]:
        """
        Capture image from real Pixelink camera using proper API flow.
        Based on Sample_PixcelinkAPI_python/getNumPySnapshot.py
        """
        try:
            # Determine image dimensions
            width, height, bytes_per_pixel = self._determine_raw_image_size()
            if width == 0 or height == 0:
                logger.error("Failed to determine image size")
                return None
            
            # Update cached dimensions
            self.width = width
            self.height = height
            
            # Create NumPy buffer for raw image
            np_image = np.zeros([height, width * bytes_per_pixel], dtype=np.uint8)
            
            # Capture image with retries (blocking call)
            MAX_RETRIES = 4
            ret = None
            
            # Start streaming
            stream_ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
            if not PxLApi.apiSuccess(stream_ret[0]):
                logger.error("Failed to start streaming")
                return None
            
            # Get frame with retries
            for attempt in range(MAX_RETRIES):
                ret = PxLApi.getNextNumPyFrame(self.camera_handle, np_image)
                if PxLApi.apiSuccess(ret[0]):
                    break
                logger.warning(f"Capture attempt {attempt + 1} failed, retrying...")
            
            # Stop streaming
            PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)
            
            if not ret or not PxLApi.apiSuccess(ret[0]):
                logger.error("Failed to capture image after retries")
                return None
            
            frame_descriptor = ret[1]
            
            # Format image as JPEG/RGB
            format_ret = PxLApi.formatNumPyImage(np_image, frame_descriptor, PxLApi.ImageFormat.RAW_RGB24)
            if not PxLApi.apiSuccess(format_ret[0]):
                logger.error("Failed to format image")
                return None
            
            # Convert to proper RGB array
            rgb_data = format_ret[1]
            image_array = np.frombuffer(rgb_data, dtype=np.uint8)
            image_array = image_array.reshape((height, width, 3))
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error capturing real image: {e}")
            return None
    
    def _determine_raw_image_size(self):
        """
        Determine raw image dimensions from camera ROI and pixel format.
        Returns: (width, height, bytes_per_pixel)
        """
        try:
            # Get ROI (Region of Interest)
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.ROI)
            if not PxLApi.apiSuccess(ret[0]):
                return (0, 0, 0)
            
            params = ret[2]
            roi_width = params[PxLApi.RoiParams.WIDTH]
            roi_height = params[PxLApi.RoiParams.HEIGHT]
            
            # Get pixel addressing (decimation/binning)
            pixel_addressing_x = 1
            pixel_addressing_y = 1
            
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.PIXEL_ADDRESSING)
            if PxLApi.apiSuccess(ret[0]):
                params = ret[2]
                if len(params) == PxLApi.PixelAddressingParams.NUM_PARAMS:
                    # Asymmetric pixel addressing
                    pixel_addressing_x = params[PxLApi.PixelAddressingParams.X_VALUE]
                    pixel_addressing_y = params[PxLApi.PixelAddressingParams.Y_VALUE]
                else:
                    # Symmetric pixel addressing
                    pixel_addressing_x = params[PxLApi.PixelAddressingParams.VALUE]
                    pixel_addressing_y = params[PxLApi.PixelAddressingParams.VALUE]
            
            # Calculate actual image dimensions
            width = int(roi_width / pixel_addressing_x)
            height = int(roi_height / pixel_addressing_y)
            
            # Get pixel format to determine bytes per pixel
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.PIXEL_FORMAT)
            if not PxLApi.apiSuccess(ret[0]):
                return (0, 0, 0)
            
            params = ret[2]
            pixel_format = int(params[0])
            bytes_per_pixel = PxLApi.getBytesPerPixel(pixel_format)
            
            return (width, height, bytes_per_pixel)
            
        except Exception as e:
            logger.error(f"Error determining image size: {e}")
            return (0, 0, 0)
    
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
