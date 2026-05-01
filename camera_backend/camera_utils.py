"""
Camera Utility Functions

Shared utilities for PixeLink camera operations.
Used by both pixelink_camera.py and camera_streamer.py to avoid code duplication.
"""
import logging
import numpy as np
from typing import Optional, Tuple

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


def determine_raw_image_size(camera_handle) -> Tuple[int, int, int]:
    """
    Determine raw image dimensions from camera ROI and pixel format.
    
    Args:
        camera_handle: PixeLink camera handle
        
    Returns:
        Tuple of (width, height, bytes_per_pixel)
    """
    try:
        # Get ROI (Region of Interest)
        ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.ROI)
        if not PxLApi.apiSuccess(ret[0]):
            return (0, 0, 0)
        
        params = ret[2]
        roi_width = params[PxLApi.RoiParams.WIDTH]
        roi_height = params[PxLApi.RoiParams.HEIGHT]
        
        # Get pixel addressing (decimation/binning)
        pixel_addressing_x = 1
        pixel_addressing_y = 1
        
        ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.PIXEL_ADDRESSING)
        if PxLApi.apiSuccess(ret[0]):
            params = ret[2]
            if params[PxLApi.PixelAddressingParams.MODE] != PxLApi.PixelAddressingModes.DECIMATE:
                pixel_addressing_x = max(1, int(params[PxLApi.PixelAddressingParams.X_VALUE]))
                pixel_addressing_y = max(1, int(params[PxLApi.PixelAddressingParams.Y_VALUE]))
        
        # Calculate actual image dimensions
        width = int(roi_width / pixel_addressing_x)
        height = int(roi_height / pixel_addressing_y)
        
        # Get pixel format to determine bytes per pixel
        ret = PxLApi.getFeature(camera_handle, PxLApi.FeatureId.PIXEL_FORMAT)
        if not PxLApi.apiSuccess(ret[0]):
            return (0, 0, 0)
        
        pixel_format = int(ret[2][0])
        bytes_per_pixel = PxLApi.getBytesPerPixel(pixel_format)
        
        return (width, height, bytes_per_pixel)
        
    except Exception as e:
        logger.error(f"Error determining image size: {e}")
        return (0, 0, 0)


def capture_frame(camera_handle, max_retries: int = 3) -> Optional[np.ndarray]:
    """
    Capture a single frame from the PixeLink camera.
    
    Args:
        camera_handle: PixeLink camera handle
        max_retries: Number of retry attempts for frame capture
        
    Returns:
        RGB numpy array (height, width, 3) or None if failed
    """
    try:
        # Determine image dimensions
        width, height, bytes_per_pixel = determine_raw_image_size(camera_handle)
        if width == 0 or height == 0:
            logger.error("Failed to determine image size")
            return None
        
        # Create NumPy buffer for raw image
        np_image = np.zeros([height, width * bytes_per_pixel], dtype=np.uint8)
        
        # Get frame with retries
        ret = None
        for attempt in range(max_retries):
            ret = PxLApi.getNextNumPyFrame(camera_handle, np_image)
            if PxLApi.apiSuccess(ret[0]):
                break
                
            # Check for fatal errors
            # -2147483630 (ApiStreamStopped) is expected when stream is stopped - don't log as error
            if ret[0] == -2147483630:  # ApiStreamStopped
                logger.debug("Stream stopped (expected when closing)")
                return None
            elif ret[0] == PxLApi.ReturnCode.ApiNoCameraAvailableError:
                logger.error(f"Camera not available: {ret[0]}")
                return None
                
            if attempt < max_retries - 1:
                logger.debug(f"Frame grab attempt {attempt + 1} failed, retrying...")
        
        if not ret or not PxLApi.apiSuccess(ret[0]):
            return None
        
        frame_descriptor = ret[1]
        
        # Format as RGB24
        format_ret = PxLApi.formatNumPyImage(np_image, frame_descriptor, PxLApi.ImageFormat.RAW_RGB24)
        if not PxLApi.apiSuccess(format_ret[0]):
            return None
        
        # Convert to RGB array
        rgb_data = format_ret[1]
        image_array = np.frombuffer(rgb_data, dtype=np.uint8)
        image_array = image_array.reshape((height, width, 3))
        
        return image_array
        
    except Exception as e:
        logger.error(f"Frame capture error: {e}")
        return None


def generate_simulated_frame(width: int = 1280, height: int = 1024) -> np.ndarray:
    """
    Generate a simulated test pattern frame.
    
    Args:
        width: Frame width in pixels
        height: Frame height in pixels
        
    Returns:
        RGB numpy array (height, width, 3)
    """
    import time
    
    # Create a gradient pattern for testing
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create animated gradient
    phase = int(time.time() * 50) % 256
    
    for i in range(height):
        for j in range(width):
            image[i, j] = [
                (i + phase) % 256,
                (j + phase) % 256,
                ((i + j + phase) // 2) % 256
            ]
    
    return image
