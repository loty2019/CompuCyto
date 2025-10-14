""""""

Pixelink Camera Wrapper - Minimal Essential ImplementationPixelink Camera Wrapper

Provides camera control interface for the PixeLink SDKProvides a high-level interface to the Pixelink SDK for camera control

""""""

import loggingimport logging

from typing import Optional, Dictfrom typing import Optional, Dict, Tuple, List

from datetime import datetimefrom datetime import datetime

from pathlib import Pathfrom pathlib import Path

from ctypes import create_string_bufferimport numpy as np

from PIL import Image

# Import Pixelink SDK - handles the wmic Windows compatibility issue

try:# Import Pixelink SDK

    import subprocess# Note: You'll need to install the Pixelink SDK and ensure the Python bindings are available

    original_check_output = subprocess.check_outputtry:

        from pixelinkWrapper import PxLApi

    def patched_check_output(*args, **kwargs):    PIXELINK_AVAILABLE = True

        try:except ImportError:

            return original_check_output(*args, **kwargs)    PIXELINK_AVAILABLE = False

        except FileNotFoundError:    logging.warning("Pixelink SDK not available. Running in simulation mode.")

            return b"10.0.0"  # Dummy version if wmic fails

    

    subprocess.check_output = patched_check_outputlogger = logging.getLogger(__name__)

    from pixelinkWrapper import PxLApi

    subprocess.check_output = original_check_output

    PIXELINK_AVAILABLE = Trueclass PixelinkCamera:

except ImportError:    """

    PIXELINK_AVAILABLE = False    High-level wrapper for Pixelink camera operations

    logging.warning("Pixelink SDK not available. Running in simulation mode.")    Manages camera initialization, settings, and image capture

    """

logger = logging.getLogger(__name__)    

    def __init__(self, serial_number: Optional[str] = None):

        """

class PixelinkCamera:        Initialize camera connection

    """        

    High-level wrapper for Pixelink camera operations.        Args:

    Manages initialization, settings, and image capture.            serial_number: Optional camera serial number. If None, uses first available camera.

    """        """

            self.serial_number = serial_number

    def __init__(self, serial_number: Optional[str] = None):        self.camera_handle = None

        """        self.is_connected = False

        Initialize camera connection.        self.is_streaming = False

                

        Args:        # Camera settings

            serial_number: Optional camera serial number (None = first available)        self.exposure = 100.0  # milliseconds

        """        self.gain = 1.0

        self.serial_number = serial_number        self.width = 1280

        self.camera_handle = None        self.height = 1024

        self.is_connected = False        self.available_resolutions = [

        self.is_streaming = False            (640, 480),

                    (800, 600),

        # Default settings            (1024, 768),

        self.exposure = 100.0  # milliseconds            (1280, 1024),

        self.gain = 1.0            (1920, 1080),

        self.width = 1280            (2048, 1536)

        self.height = 1024        ]

                

        if PIXELINK_AVAILABLE:        # Initialize camera

            self._initialize_camera()        if PIXELINK_AVAILABLE:

                self._initialize_camera()

    def _initialize_camera(self) -> bool:        else:

        """Initialize connection to Pixelink camera."""            logger.warning("Pixelink SDK not available. Camera operations will be simulated.")

        try:    

            # Initialize first available camera or specific serial number    def _initialize_camera(self) -> bool:

            camera_id = int(self.serial_number) if self.serial_number else 0        """

            ret = PxLApi.initialize(camera_id)        Initialize connection to Pixelink camera

                    

            if PxLApi.apiSuccess(ret[0]):        Returns:

                self.camera_handle = ret[1]            True if successful, False otherwise

                self.is_connected = True        """

                self._load_current_settings()        try:

                logger.info(f"Camera initialized. Handle: {self.camera_handle}")            # Initialize the camera

                return True            if self.serial_number:

            else:                ret = PxLApi.initialize(int(self.serial_number))

                logger.error(f"Camera init failed: {ret[0]}")            else:

                return False                ret = PxLApi.initialize(0)  # Use first available camera

        except Exception as e:            

            logger.error(f"Camera init error: {e}")            if PxLApi.apiSuccess(ret[0]):

            return False                self.camera_handle = ret[1]

                    self.is_connected = True

    def _load_current_settings(self):                logger.info(f"Camera initialized successfully. Handle: {self.camera_handle}")

        """Load current settings from camera hardware."""                

        try:                # Load current settings from camera

            # Get exposure (convert microseconds to milliseconds)                self._load_current_settings()

            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)                return True

            if PxLApi.apiSuccess(ret[0]):            else:

                self.exposure = ret[2][0] / 1000.0                logger.error(f"Failed to initialize camera. Error: {ret[0]}")

                            return False

            # Get gain                

            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.GAIN)        except Exception as e:

            if PxLApi.apiSuccess(ret[0]):            logger.error(f"Camera initialization error: {e}")

                self.gain = ret[2][0]            return False

                

            # Get ROI (Region of Interest) for resolution    def _load_current_settings(self):

            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.ROI)        """Load current camera settings from hardware"""

            if PxLApi.apiSuccess(ret[0]):        if not PIXELINK_AVAILABLE or not self.is_connected:

                self.width = int(ret[2][PxLApi.RoiParams.WIDTH])            return

                self.height = int(ret[2][PxLApi.RoiParams.HEIGHT])        

                    try:

            logger.info(f"Settings: {self.exposure}ms exposure, {self.gain} gain, {self.width}x{self.height}")            # Get exposure

        except Exception as e:            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)

            logger.error(f"Error loading settings: {e}")            if PxLApi.apiSuccess(ret[0]):

                    self.exposure = ret[2][0] / 1000.0  # Convert to milliseconds

    def get_settings(self) -> Dict:            

        """Get current camera settings."""            # Get gain

        return {            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.GAIN)

            "exposure": self.exposure,            if PxLApi.apiSuccess(ret[0]):

            "gain": self.gain,                self.gain = ret[2][0]

            "resolution": {"width": self.width, "height": self.height},            

            "connected": self.is_connected,            # Get ROI (Region of Interest) for resolution

            "streaming": self.is_streaming            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.ROI)

        }            if PxLApi.apiSuccess(ret[0]):

                    self.width = int(ret[2][PxLApi.RoiParams.WIDTH])

    def update_settings(self, exposure: Optional[float] = None, gain: Optional[float] = None) -> Dict:                self.height = int(ret[2][PxLApi.RoiParams.HEIGHT])

        """            

        Update camera settings.            logger.info(f"Loaded camera settings: exposure={self.exposure}ms, gain={self.gain}, resolution={self.width}x{self.height}")

                except Exception as e:

        Args:            logger.error(f"Error loading camera settings: {e}")

            exposure: Exposure time in milliseconds    

            gain: Gain value    def get_settings(self) -> Dict:

        """        """

        if exposure is not None:        Get current camera settings

            self._set_exposure(exposure)        

        if gain is not None:        Returns:

            self._set_gain(gain)            Dictionary with current settings

        return self.get_settings()        """

            return {

    def _set_exposure(self, exposure_ms: float):            "exposure": self.exposure,

        """Set camera exposure time."""            "gain": self.gain,

        if PIXELINK_AVAILABLE and self.is_connected:            "resolution": {

            try:                "width": self.width,

                # Convert milliseconds to microseconds                "height": self.height

                exposure_us = exposure_ms * 1000.0            },

                ret = PxLApi.setFeature(            "available_resolutions": [

                    self.camera_handle,                {"width": w, "height": h} for w, h in self.available_resolutions

                    PxLApi.FeatureId.EXPOSURE,            ],

                    PxLApi.FeatureFlags.MANUAL,            "connected": self.is_connected,

                    [exposure_us]            "streaming": self.is_streaming

                )        }

                if PxLApi.apiSuccess(ret[0]):    

                    self.exposure = exposure_ms    def update_settings(self, exposure: Optional[float] = None, gain: Optional[float] = None) -> Dict:

                    logger.info(f"Exposure set to {exposure_ms}ms")        """

            except Exception as e:        Update camera settings

                logger.error(f"Error setting exposure: {e}")        

        else:        Args:

            self.exposure = exposure_ms            exposure: Exposure time in milliseconds

                gain: Gain value

    def _set_gain(self, gain: float):            

        """Set camera gain."""        Returns:

        if PIXELINK_AVAILABLE and self.is_connected:            Updated settings dictionary

            try:        """

                ret = PxLApi.setFeature(        if exposure is not None:

                    self.camera_handle,            self._set_exposure(exposure)

                    PxLApi.FeatureId.GAIN,        

                    PxLApi.FeatureFlags.MANUAL,        if gain is not None:

                    [gain]            self._set_gain(gain)

                )        

                if PxLApi.apiSuccess(ret[0]):        return self.get_settings()

                    self.gain = gain    

                    logger.info(f"Gain set to {gain}")    def _set_exposure(self, exposure_ms: float):

            except Exception as e:        """Set camera exposure time"""

                logger.error(f"Error setting gain: {e}")        if PIXELINK_AVAILABLE and self.is_connected:

        else:            try:

            self.gain = gain                # Convert milliseconds to microseconds for Pixelink API

                    exposure_us = exposure_ms * 1000.0

    def _determine_raw_image_size(self) -> int:                ret = PxLApi.setFeature(

        """Calculate size of raw image buffer needed."""                    self.camera_handle,

        # Get ROI dimensions                    PxLApi.FeatureId.EXPOSURE,

        ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.ROI)                    PxLApi.FeatureFlags.MANUAL,

        params = ret[2]                    [exposure_us]

        roi_width = params[PxLApi.RoiParams.WIDTH]                )

        roi_height = params[PxLApi.RoiParams.HEIGHT]                if PxLApi.apiSuccess(ret[0]):

                            self.exposure = exposure_ms

        # Get pixel addressing (decimation)                    logger.info(f"Exposure set to {exposure_ms}ms")

        pixel_addr_x = 1                else:

        pixel_addr_y = 1                    logger.error(f"Failed to set exposure: {ret[0]}")

        ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.PIXEL_ADDRESSING)            except Exception as e:

        if PxLApi.apiSuccess(ret[0]):                logger.error(f"Error setting exposure: {e}")

            params = ret[2]        else:

            if len(params) == PxLApi.PixelAddressingParams.NUM_PARAMS:            # Simulation mode

                pixel_addr_x = params[PxLApi.PixelAddressingParams.X_VALUE]            self.exposure = exposure_ms

                pixel_addr_y = params[PxLApi.PixelAddressingParams.Y_VALUE]            logger.info(f"[SIMULATED] Exposure set to {exposure_ms}ms")

            else:    

                pixel_addr_x = params[PxLApi.PixelAddressingParams.VALUE]    def _set_gain(self, gain: float):

                pixel_addr_y = params[PxLApi.PixelAddressingParams.VALUE]        """Set camera gain"""

                if PIXELINK_AVAILABLE and self.is_connected:

        # Calculate number of pixels            try:

        num_pixels = (roi_width / pixel_addr_x) * (roi_height / pixel_addr_y)                ret = PxLApi.setFeature(

                            self.camera_handle,

        # Get pixel format to determine bytes per pixel                    PxLApi.FeatureId.GAIN,

        ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.PIXEL_FORMAT)                    PxLApi.FeatureFlags.MANUAL,

        pixel_format = int(ret[2][0])                    [gain]

        pixel_size = PxLApi.getBytesPerPixel(pixel_format)                )

                        if PxLApi.apiSuccess(ret[0]):

        return int(num_pixels * pixel_size)                    self.gain = gain

                        logger.info(f"Gain set to {gain}")

    def capture_image(self, save_path: Path, exposure: Optional[float] = None, gain: Optional[float] = None) -> Dict:                else:

        """                    logger.error(f"Failed to set gain: {ret[0]}")

        Capture image from camera and save to disk.            except Exception as e:

                        logger.error(f"Error setting gain: {e}")

        Args:        else:

            save_path: Path where to save the image            # Simulation mode

            exposure: Optional exposure override            self.gain = gain

            gain: Optional gain override            logger.info(f"[SIMULATED] Gain set to {gain}")

                

        Returns:    def capture_image(self, save_path: Path, exposure: Optional[float] = None, gain: Optional[float] = None) -> Dict:

            Capture metadata dict        """

        """        Capture a single image from the camera

        # Update settings if provided        

        if exposure is not None or gain is not None:        Args:

            self.update_settings(exposure, gain)            save_path: Path where to save the captured image

                    exposure: Optional exposure override

        timestamp = datetime.now()            gain: Optional gain override

                    

        if PIXELINK_AVAILABLE and self.is_connected:        Returns:

            success = self._capture_real_image(save_path)            Dictionary with capture metadata

        else:        """

            success = self._capture_simulated_image(save_path)        # Update settings if provided

                if exposure is not None or gain is not None:

        if not success:            self.update_settings(exposure, gain)

            raise RuntimeError("Failed to capture image")        

                timestamp = datetime.now()

        return {        

            "success": True,        if PIXELINK_AVAILABLE and self.is_connected:

            "filename": save_path.name,            image_data = self._capture_real_image()

            "filepath": str(save_path),        else:

            "timestamp": timestamp.isoformat(),            image_data = self._capture_simulated_image()

            "settings": {        

                "exposure": self.exposure,        if image_data is None:

                "gain": self.gain,            raise RuntimeError("Failed to capture image")

                "resolution": {"width": self.width, "height": self.height}        

            },        # Save image

            "image_info": {        image = Image.fromarray(image_data)

                "size_bytes": save_path.stat().st_size,        image.save(save_path, quality=95)

                "format": save_path.suffix[1:].upper()        

            }        return {

        }            "success": True,

                "filename": save_path.name,

    def _capture_real_image(self, save_path: Path) -> bool:            "filepath": str(save_path),

        """Capture image from real Pixelink camera using SDK."""            "timestamp": timestamp.isoformat(),

        try:            "settings": {

            # Determine buffer size needed                "exposure": self.exposure,

            raw_image_size = self._determine_raw_image_size()                "gain": self.gain,

            if raw_image_size == 0:                "resolution": {

                return False                    "width": self.width,

                                "height": self.height

            # Create buffer for raw image                }

            raw_image = create_string_buffer(raw_image_size)            },

                        "image_info": {

            # Start streaming                "size_bytes": save_path.stat().st_size,

            ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)                "format": save_path.suffix[1:].upper()

            if not PxLApi.apiSuccess(ret[0]):            }

                return False        }

                

            # Get frame (with retries for timeout)    def _capture_real_image(self) -> Optional[np.ndarray]:

            MAX_TRIES = 4        """Capture image from real Pixelink camera"""

            ret = None        try:

            for _ in range(MAX_TRIES):            # Get a single frame

                ret = PxLApi.getNextFrame(self.camera_handle, raw_image)            ret = PxLApi.getNextFrame(self.camera_handle)

                if PxLApi.apiSuccess(ret[0]):            if not PxLApi.apiSuccess(ret[0]):

                    break                logger.error(f"Failed to get frame: {ret[0]}")

                            return None

            # Stop streaming            

            PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)            frame_descriptor = ret[1]

                        frame_data = ret[2]

            if not PxLApi.apiSuccess(ret[0]):            

                return False            # Convert to RGB

                        ret = PxLApi.formatImage(frame_data, frame_descriptor, PxLApi.ImageFormat.RGB24)

            # Format image to JPEG            if not PxLApi.apiSuccess(ret[0]):

            frame_descriptor = ret[1]                logger.error(f"Failed to format image: {ret[0]}")

            image_format = PxLApi.ImageFormat.JPEG if save_path.suffix.lower() in ['.jpg', '.jpeg'] else PxLApi.ImageFormat.BMP                return None

                        

            ret = PxLApi.formatImage(raw_image, frame_descriptor, image_format)            rgb_data = ret[1]

            if not PxLApi.apiSuccess(ret[0]):            

                return False            # Convert to numpy array

                        image_array = np.frombuffer(rgb_data, dtype=np.uint8)

            # Save to file            image_array = image_array.reshape((self.height, self.width, 3))

            formatted_image = ret[1]            

            with open(save_path, "wb") as f:            return image_array

                f.write(formatted_image)            

                    except Exception as e:

            return True            logger.error(f"Error capturing image: {e}")

                        return None

        except Exception as e:    

            logger.error(f"Error capturing image: {e}")    def _capture_simulated_image(self) -> np.ndarray:

            return False        """Generate a simulated image for testing"""

            # Create a gradient image with timestamp

    def _capture_simulated_image(self, save_path: Path) -> bool:        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        """Generate simulated image for testing without camera."""        

        try:        # Create gradient

            import numpy as np        for i in range(self.height):

            from PIL import Image            for j in range(self.width):

                            image[i, j] = [

            # Create gradient test image                    int(255 * i / self.height),

            image = np.zeros((self.height, self.width, 3), dtype=np.uint8)                    int(255 * j / self.width),

            for i in range(self.height):                    128

                for j in range(self.width):                ]

                    image[i, j] = [        

                        int(255 * i / self.height),        return image

                        int(255 * j / self.width),    

                        128    def start_streaming(self) -> bool:

                    ]        """Start video streaming"""

                    if PIXELINK_AVAILABLE and self.is_connected and not self.is_streaming:

            # Save image            try:

            img = Image.fromarray(image)                ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)

            img.save(save_path, quality=95)                if PxLApi.apiSuccess(ret[0]):

            return True                    self.is_streaming = True

        except Exception as e:                    logger.info("Camera streaming started")

            logger.error(f"Error creating simulated image: {e}")                    return True

            return False                else:

                        logger.error(f"Failed to start streaming: {ret[0]}")

    def disconnect(self):                    return False

        """Disconnect from camera."""            except Exception as e:

        if PIXELINK_AVAILABLE and self.is_connected:                logger.error(f"Error starting stream: {e}")

            try:                return False

                if self.is_streaming:        else:

                    PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)            self.is_streaming = True

                PxLApi.uninitialize(self.camera_handle)            logger.info("[SIMULATED] Camera streaming started")

                self.is_connected = False            return True

                logger.info("Camera disconnected")    

            except Exception as e:    def stop_streaming(self) -> bool:

                logger.error(f"Error disconnecting: {e}")        """Stop video streaming"""

            if PIXELINK_AVAILABLE and self.is_connected and self.is_streaming:

    def __del__(self):            try:

        """Cleanup on deletion."""                ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)

        self.disconnect()                if PxLApi.apiSuccess(ret[0]):

                    self.is_streaming = False
                    logger.info("Camera streaming stopped")
                    return True
                else:
                    logger.error(f"Failed to stop streaming: {ret[0]}")
                    return False
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")
                return False
        else:
            self.is_streaming = False
            logger.info("[SIMULATED] Camera streaming stopped")
            return True
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get a single frame for streaming
        
        Returns:
            Numpy array with image data, or None if failed
        """
        if not self.is_streaming:
            return None
        
        if PIXELINK_AVAILABLE and self.is_connected:
            return self._capture_real_image()
        else:
            return self._capture_simulated_image()
    
    def disconnect(self):
        """Disconnect from camera"""
        if PIXELINK_AVAILABLE and self.is_connected:
            try:
                if self.is_streaming:
                    self.stop_streaming()
                PxLApi.uninitialize(self.camera_handle)
                self.is_connected = False
                logger.info("Camera disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting camera: {e}")
        else:
            self.is_connected = False
            logger.info("[SIMULATED] Camera disconnected")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()
