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
import threading
import time

# Import shared camera utilities to avoid code duplication
from camera_utils import (
    PIXELINK_AVAILABLE,
    PxLApi,
    determine_raw_image_size,
    capture_frame,
    generate_simulated_frame
)

logger = logging.getLogger(__name__)


class PixelinkCamera:
    """Wrapper for PixeLink camera operations"""
    
    def __init__(self, serial_number: Optional[str] = None):
        self.serial_number = serial_number
        self.camera_handle = None
        self.is_connected = False
        self.is_streaming = False
        # Note: PixeLink API uses SECONDS for exposure internally
        # We'll store as milliseconds for UI/database, convert when needed
        self.exposure = 100.0  # Default 100ms
        self.gain = 1.0
        self.gamma = 1.0  # Default gamma value
        self.width = 1280
        self.height = 1024
        
        # Exposure limits (in milliseconds)
        self.exposure_min = 0.001  # 1 microsecond
        self.exposure_max = 10000.0  # 10 seconds
        
        # Gain limits
        self.gain_min = 1.0
        self.gain_max = 16.0
        
        # Gamma limits
        self.gamma_min = 0.5
        self.gamma_max = 4.0
        self.gamma_supported = False  # Will be set during initialization
        
        # Auto-exposure state
        self.auto_exposure_enabled = False
        self.auto_exposure_supported = False  # Will be set during initialization
        
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
        """Load current settings and feature limits from camera"""
        if not PIXELINK_AVAILABLE or not self.is_connected:
            return
        try:
            # Get exposure limits from camera features
            ret = PxLApi.getCameraFeatures(self.camera_handle, PxLApi.FeatureId.EXPOSURE)
            if PxLApi.apiSuccess(ret[0]):
                features = ret[1]
                if features.uNumberOfFeatures > 0:
                    feature = features.Features[0]
                    if feature.uFlags & PxLApi.FeatureFlags.PRESENCE:
                        # Exposure limits are in SECONDS, convert to milliseconds
                        self.exposure_min = feature.Params[0].fMinValue * 1000.0
                        self.exposure_max = feature.Params[0].fMaxValue * 1000.0
                        logger.info(f"📏 Exposure range: {self.exposure_min:.3f}ms - {self.exposure_max:.3f}ms")
                        
                        # Check if auto-exposure is supported
                        self.auto_exposure_supported = bool(
                            (feature.uFlags & PxLApi.FeatureFlags.AUTO) or
                            (feature.uFlags & PxLApi.FeatureFlags.ONEPUSH)
                        )
                        logger.info(f"🤖 Auto-exposure supported: {self.auto_exposure_supported}")
            
            # Get current exposure value
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)
            if PxLApi.apiSuccess(ret[0]):
                flags = ret[1]
                params = ret[2]
                # PixeLink API returns exposure in SECONDS
                exposure_seconds = params[0]
                self.exposure = exposure_seconds * 1000.0  # Convert to milliseconds
                
                # Check if auto-exposure is enabled
                self.auto_exposure_enabled = bool(flags & PxLApi.FeatureFlags.AUTO)
                
                logger.info(f"📸 Current exposure: {self.exposure:.3f}ms ({exposure_seconds:.6f}s)")
                logger.info(f"🤖 Auto-exposure: {'ENABLED' if self.auto_exposure_enabled else 'DISABLED'}")
            
            # Get gain limits
            ret = PxLApi.getCameraFeatures(self.camera_handle, PxLApi.FeatureId.GAIN)
            if PxLApi.apiSuccess(ret[0]):
                features = ret[1]
                if features.uNumberOfFeatures > 0:
                    feature = features.Features[0]
                    if feature.uFlags & PxLApi.FeatureFlags.PRESENCE:
                        self.gain_min = feature.Params[0].fMinValue
                        self.gain_max = feature.Params[0].fMaxValue
                        logger.info(f"📏 Gain range: {self.gain_min:.2f} - {self.gain_max:.2f}")
            
            # Get current gain
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.GAIN)
            if PxLApi.apiSuccess(ret[0]):
                self.gain = ret[2][0]
                logger.info(f"📸 Current gain: {self.gain:.2f}")
            
            # Get gamma limits
            ret = PxLApi.getCameraFeatures(self.camera_handle, PxLApi.FeatureId.GAMMA)
            if PxLApi.apiSuccess(ret[0]):
                features = ret[1]
                if features.uNumberOfFeatures > 0:
                    feature = features.Features[0]
                    if feature.uFlags & PxLApi.FeatureFlags.PRESENCE:
                        self.gamma_min = feature.Params[0].fMinValue
                        self.gamma_max = feature.Params[0].fMaxValue
                        self.gamma_supported = True
                        logger.info(f"📏 Gamma range: {self.gamma_min:.2f} - {self.gamma_max:.2f}")
                    else:
                        logger.info("⚠️ Gamma feature not supported by this camera")
            
            # Get current gamma if supported
            if self.gamma_supported:
                ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.GAMMA)
                if PxLApi.apiSuccess(ret[0]):
                    self.gamma = ret[2][0]
                    logger.info(f"📸 Current gamma: {self.gamma:.2f}")
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def get_settings(self) -> Dict:
        return {
            "exposure": self.exposure,
            "exposureMin": self.exposure_min,
            "exposureMax": self.exposure_max,
            "gain": self.gain,
            "gainMin": self.gain_min,
            "gainMax": self.gain_max,
            "gamma": self.gamma,
            "gammaMin": self.gamma_min,
            "gammaMax": self.gamma_max,
            "gammaSupported": self.gamma_supported,
            "autoExposure": self.auto_exposure_enabled,
            "autoExposureSupported": self.auto_exposure_supported,
            "resolution": {"width": self.width, "height": self.height},
            "connected": self.is_connected,
            "streaming": self.is_streaming
        }
    
    def update_settings(self, exposure: Optional[float] = None, gain: Optional[float] = None, 
                       gamma: Optional[float] = None, auto_exposure: Optional[bool] = None) -> Dict:
        """
        Update camera settings.
        
        Args:
            exposure: Exposure time in milliseconds (will be ignored if auto_exposure=True)
            gain: Gain value
            gamma: Gamma value for brightness/contrast adjustment
            auto_exposure: Enable/disable auto-exposure
        """
        if auto_exposure is not None:
            self._set_auto_exposure(auto_exposure)
        
        # Only set manual exposure if auto-exposure is disabled
        if exposure is not None and not self.auto_exposure_enabled:
            self._set_exposure(exposure)
            
        if gain is not None:
            self._set_gain(gain)
        
        if gamma is not None:
            self._set_gamma(gamma)
            
        return self.get_settings()
    
    def _set_exposure(self, exposure_ms: float):
        """
        Set exposure time in milliseconds.
        PixeLink API uses SECONDS, so we convert ms -> seconds.
        """
        if PIXELINK_AVAILABLE and self.is_connected:
            try:
                # Clamp exposure to valid range
                exposure_ms = max(self.exposure_min, min(exposure_ms, self.exposure_max))
                
                # Convert milliseconds to seconds for PixeLink API
                exposure_seconds = exposure_ms / 1000.0
                
                logger.info(f"🎯 Setting exposure to {exposure_ms:.3f}ms ({exposure_seconds:.6f}s)")
                
                ret = PxLApi.setFeature(
                    self.camera_handle,
                    PxLApi.FeatureId.EXPOSURE,
                    PxLApi.FeatureFlags.MANUAL,
                    [exposure_seconds]  # PixeLink expects SECONDS
                )
                
                if PxLApi.apiSuccess(ret[0]):
                    self.exposure = exposure_ms
                    self.auto_exposure_enabled = False
                    logger.info(f"✅ Exposure set successfully to {self.exposure:.3f}ms")
                else:
                    error_code = ret[0]
                    logger.error(f"❌ Failed to set exposure. Error code: {error_code}")
                    logger.error(f"   Requested: {exposure_ms:.3f}ms ({exposure_seconds:.6f}s)")
                    logger.error(f"   Valid range: {self.exposure_min:.3f}ms - {self.exposure_max:.3f}ms")
                    
            except Exception as e:
                logger.error(f"Exception setting exposure: {e}")
        else:
            # Simulated mode - just update the value
            self.exposure = exposure_ms
            logger.info(f"🎭 [SIMULATED] Exposure set to {self.exposure:.3f}ms")
    
    def _set_gain(self, gain: float):
        """Set camera gain"""
        if PIXELINK_AVAILABLE and self.is_connected:
            try:
                # Clamp gain to valid range
                gain = max(self.gain_min, min(gain, self.gain_max))
                
                logger.info(f"🎯 Setting gain to {gain:.2f}")
                
                ret = PxLApi.setFeature(
                    self.camera_handle,
                    PxLApi.FeatureId.GAIN,
                    PxLApi.FeatureFlags.MANUAL,
                    [gain]
                )
                
                if PxLApi.apiSuccess(ret[0]):
                    self.gain = gain
                    logger.info(f"✅ Gain set successfully to {self.gain:.2f}")
                else:
                    logger.error(f"❌ Failed to set gain. Error code: {ret[0]}")
                    
            except Exception as e:
                logger.error(f"Exception setting gain: {e}")
        else:
            self.gain = gain
            logger.info(f"🎭 [SIMULATED] Gain set to {self.gain:.2f}")
    
    def _set_gamma(self, gamma: float):
        """Set camera gamma"""
        if PIXELINK_AVAILABLE and self.is_connected:
            if not self.gamma_supported:
                logger.warning("⚠️ Gamma not supported by this camera")
                return
            
            try:
                # Clamp gamma to valid range
                gamma = max(self.gamma_min, min(gamma, self.gamma_max))
                
                logger.info(f"🎯 Setting gamma to {gamma:.2f}")
                
                ret = PxLApi.setFeature(
                    self.camera_handle,
                    PxLApi.FeatureId.GAMMA,
                    PxLApi.FeatureFlags.MANUAL,
                    [gamma]
                )
                
                if PxLApi.apiSuccess(ret[0]):
                    self.gamma = gamma
                    logger.info(f"✅ Gamma set successfully to {self.gamma:.2f}")
                else:
                    logger.error(f"❌ Failed to set gamma. Error code: {ret[0]}")
                    
            except Exception as e:
                logger.error(f"Exception setting gamma: {e}")
        else:
            self.gamma = gamma
            logger.info(f"🎭 [SIMULATED] Gamma set to {self.gamma:.2f}")
    
    def _set_auto_exposure(self, enabled: bool):
        """Enable or disable continuous auto-exposure"""
        if PIXELINK_AVAILABLE and self.is_connected:
            # Check if auto-exposure is supported
            if not self.auto_exposure_supported:
                logger.warning("⚠️ Auto-exposure not supported by this camera")
                logger.info("ℹ️ Camera does not have AUTO or ONEPUSH capability")
                return
            
            try:
                # CRITICAL: Camera must be streaming for auto-exposure to work!
                # Start streaming if not already streaming
                was_streaming = self.is_streaming
                logger.info(f"🔍 Auto-exposure request - Current streaming state: {self.is_streaming}")
                
                if not was_streaming:
                    logger.info("📹 Starting stream for auto-exposure...")
                    ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
                    if PxLApi.apiSuccess(ret[0]):
                        self.is_streaming = True
                        logger.info(f"✅ Stream started successfully for auto-exposure")
                    else:
                        logger.error(f"❌ Failed to start stream. Error: {ret[0]}")
                        return
                else:
                    logger.info("✓ Camera already streaming, proceeding with auto-exposure")
                
                if enabled:
                    # Enable continuous auto-exposure
                    logger.info("🤖 Enabling AUTO exposure...")
                    
                    # NOTE: Even though value is ignored for AUTO, we still need to pass params array
                    # Get current exposure first (sample code does this)
                    ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)
                    if PxLApi.apiSuccess(ret[0]):
                        params = ret[2]  # Use current params
                    else:
                        params = [0.0]  # Fallback to 0
                    
                    ret = PxLApi.setFeature(
                        self.camera_handle,
                        PxLApi.FeatureId.EXPOSURE,
                        PxLApi.FeatureFlags.AUTO,
                        params  # Pass actual params array, not [0.0]
                    )
                else:
                    # Disable auto-exposure (switch to manual)
                    # Read current exposure value first (as set by camera during AUTO)
                    ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)
                    if PxLApi.apiSuccess(ret[0]):
                        params = ret[2]  # Use current params from camera
                        current_exposure_seconds = params[0]
                        self.exposure = current_exposure_seconds * 1000.0
                    else:
                        logger.error("Failed to get current exposure")
                        return
                    
                    logger.info(f"👤 Switching to MANUAL exposure at {self.exposure:.3f}ms...")
                    ret = PxLApi.setFeature(
                        self.camera_handle,
                        PxLApi.FeatureId.EXPOSURE,
                        PxLApi.FeatureFlags.MANUAL,
                        params  # Use the params we just read
                    )
                
                if PxLApi.apiSuccess(ret[0]):
                    self.auto_exposure_enabled = enabled
                    logger.info(f"✅ Auto-exposure {'ENABLED' if enabled else 'DISABLED'}")
                else:
                    logger.error(f"❌ Failed to set auto-exposure. Error code: {ret[0]}")
                    if ret[0] == -2147483645:
                        logger.error("   This error typically means:")
                        logger.error("   - Camera doesn't support this auto-exposure mode")
                        logger.error("   - Camera needs to be streaming for auto-exposure")
                        logger.error("   - Feature is read-only or unavailable")
                
                # Keep streaming active (streamer will manage it)
                # Don't stop streaming here as it may be used by live feed
                    
            except Exception as e:
                logger.error(f"Exception setting auto-exposure: {e}")
        else:
            self.auto_exposure_enabled = enabled
            logger.info(f"🎭 [SIMULATED] Auto-exposure {'ENABLED' if enabled else 'DISABLED'}")
    
    def perform_one_time_auto_exposure(self) -> bool:
        """
        Perform a one-time auto-exposure adjustment.
        Camera will adjust exposure once, then return to manual control.
        Returns True if successful.
        
        IMPORTANT: Camera must be streaming for auto-exposure to work!
        """
        if not PIXELINK_AVAILABLE or not self.is_connected:
            logger.warning("🎭 [SIMULATED] One-time auto-exposure (no real camera)")
            return False
        
        # Check if auto-exposure is supported
        if not self.auto_exposure_supported:
            logger.warning("⚠️ One-time auto-exposure not supported by this camera")
            return False
        
        try:
            # CRITICAL: Camera must be streaming for auto-exposure to work!
            was_streaming = self.is_streaming
            logger.info(f"🔍 One-time auto-exposure - Current streaming state: {self.is_streaming}")
            
            if not was_streaming:
                logger.info("📹 Starting stream for one-time auto-exposure...")
                ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
                if PxLApi.apiSuccess(ret[0]):
                    self.is_streaming = True
                    logger.info(f"✅ Stream started successfully for one-time auto-exposure")
                else:
                    logger.error(f"❌ Failed to start stream. Error: {ret[0]}")
                    return False
            else:
                logger.info("✓ Camera already streaming, proceeding with one-time auto-exposure")
            
            logger.info("🎯 Starting ONE-TIME auto-exposure adjustment...")
            
            # NOTE: Even though value is ignored for ONEPUSH, we still need to pass params array
            # Get current exposure first (sample code does this)
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)
            if PxLApi.apiSuccess(ret[0]):
                params = ret[2]  # Use current params
            else:
                params = [0.0]  # Fallback to 0
            
            # Initiate one-time auto-exposure
            ret = PxLApi.setFeature(
                self.camera_handle,
                PxLApi.FeatureId.EXPOSURE,
                PxLApi.FeatureFlags.ONEPUSH,
                params  # Pass actual params array, not [0.0]
            )
            
            if not PxLApi.apiSuccess(ret[0]):
                logger.error(f"❌ Failed to initiate one-time auto-exposure. Error: {ret[0]}")
                if ret[0] == -2147483645:
                    logger.error("   Camera may not support ONEPUSH auto-exposure")
                    logger.error("   Or camera is not streaming (required for auto-exposure)")
                return False
            
            # Poll until operation completes (with timeout)
            import time
            max_wait = 5.0  # 5 second timeout
            poll_interval = 0.1  # 100ms
            elapsed = 0.0
            
            while elapsed < max_wait:
                ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.EXPOSURE)
                if PxLApi.apiSuccess(ret[0]):
                    flags = ret[1]
                    params = ret[2]
                    
                    # Check if ONEPUSH flag is cleared (operation complete)
                    if not (flags & PxLApi.FeatureFlags.ONEPUSH):
                        # Operation complete - read final exposure value
                        exposure_seconds = params[0]
                        self.exposure = exposure_seconds * 1000.0
                        self.auto_exposure_enabled = False
                        logger.info(f"✅ One-time auto-exposure complete! New exposure: {self.exposure:.3f}ms")
                        
                        # Keep streaming active (streamer will manage it)
                        return True
                
                time.sleep(poll_interval)
                elapsed += poll_interval
            
            logger.warning("⏱️ One-time auto-exposure timed out")
            return False
            
        except Exception as e:
            logger.error(f"Exception during one-time auto-exposure: {e}")
            return False
    
    def capture_image(self, save_path: Path, exposure: Optional[float] = None, gain: Optional[float] = None, 
                     gamma: Optional[float] = None) -> Dict:
        """
        Capture an image and save it to disk.
        
        Args:
            save_path: Path where to save the image
            exposure: Exposure time in milliseconds (optional)
            gain: Gain value (optional)
            gamma: Gamma value (optional)
            
        Returns metadata matching NestJS Image entity structure.
        """
        # Update settings if provided (and auto-exposure is not enabled)
        if (exposure is not None or gain is not None or gamma is not None) and not self.auto_exposure_enabled:
            self.update_settings(exposure, gain, gamma)
        
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
            "exposureTime": self.exposure,  # Now in milliseconds
            "gain": self.gain,
            "gamma": self.gamma,
            "fileSize": file_size,
            "width": width,
            "height": height,
            "metadata": {
                "format": save_path.suffix.upper().replace('.', ''),
                "quality": 95,
                "cameraConnected": self.is_connected,
                "simulatedMode": not (PIXELINK_AVAILABLE and self.is_connected),
                "autoExposure": self.auto_exposure_enabled
            }
        }
    
    def _capture_real_image(self) -> Optional[np.ndarray]:
        """
        Capture image from real Pixelink camera.
        Uses shared utility function to avoid code duplication.
        
        NOTE: Ensures camera stream is active before capturing.
        """
        try:
            # Ensure camera stream is running
            if not self.is_streaming:
                logger.info("📹 Starting camera stream for capture")
                ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
                if PxLApi.apiSuccess(ret[0]):
                    self.is_streaming = True
                    logger.info("✅ Stream started successfully")
                    # Wait a bit for stream to stabilize
                    time.sleep(0.2)
                else:
                    logger.error(f"❌ Failed to start stream. Error: {ret[0]}")
                    return None
            
            # Determine and update cached dimensions
            width, height, _ = determine_raw_image_size(self.camera_handle)
            if width == 0 or height == 0:
                logger.error("Failed to determine image size")
                return None
            
            self.width = width
            self.height = height
            
            # Capture frame using shared utility (with 4 retries for image capture)
            image_array = capture_frame(self.camera_handle, max_retries=4)
            
            if image_array is not None:
                logger.info(f"✅ Image captured successfully")
            else:
                logger.error(f"❌ Failed to capture image after retries")
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error capturing real image: {e}")
            return None
    
    def _capture_simulated_image(self) -> np.ndarray:
        """
        Generate a simulated test pattern image.
        Uses shared utility function to avoid code duplication.
        """
        return generate_simulated_frame(self.width, self.height)
    
    # ==================== Video Recording Methods ====================
    
    def __init_video_recording_vars(self):
        """Initialize video recording variables"""
        self.is_recording = False
        self.recording_thread = None
        self.num_images_streamed = 0
        self.capture_rc = None
        self.capture_finished = False
        self.video_callback = None
        
    def start_video_recording(self, 
                            save_path: Path, 
                            duration: float = 10.0,
                            playback_frame_rate: float = 25.0,
                            decimation: int = 1) -> Dict:
        """
        Start recording video from camera.
        
        Args:
            save_path: Path where to save the video (should end with .mp4)
            duration: Recording duration in seconds
            playback_frame_rate: Frame rate for video playback (fps)
            decimation: Use every N'th frame (1 = all frames, 5 = every 5th frame)
            
        Returns: Metadata dict with recording parameters
        """
        if not PIXELINK_AVAILABLE or not self.is_connected:
            logger.warning("🎭 [SIMULATED] Cannot record video - no real camera")
            raise RuntimeError("Video recording requires real camera hardware")
        
        if self.is_recording:
            raise RuntimeError("Already recording video")
        
        try:
            # Ensure stream is running
            if not self.is_streaming:
                logger.info("📹 Starting stream for video recording")
                ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
                if PxLApi.apiSuccess(ret[0]):
                    self.is_streaming = True
                    # CRITICAL: Give the stream time to stabilize before capturing
                    # The sample code starts the stream well before calling getEncodedClip
                    logger.info("⏳ Waiting for stream to stabilize...")
                    time.sleep(1.0)  # 1 second delay for stream startup
                else:
                    raise RuntimeError(f"Failed to start stream: {ret[0]}")
            
            # Get effective frame rate
            camera_fps = self._get_effective_frame_rate()
            num_images = int(duration * camera_fps / decimation)
            
            logger.info(f"🎬 Starting video recording:")
            logger.info(f"   Duration requested: {duration}s")
            logger.info(f"   Camera FPS: {camera_fps:.2f}")
            logger.info(f"   Playback FPS: {playback_frame_rate}")
            logger.info(f"   Decimation: {decimation}")
            logger.info(f"   Total images to capture: {num_images}")
            logger.info(f"   Expected capture time: {num_images / camera_fps:.2f}s")
            
            # Create H.264 file path (intermediate file)
            h264_path = save_path.with_suffix('.h264')
            logger.info(f"   H.264 file: {h264_path}")
            
            # Configure clip encoding
            clip_info = PxLApi.ClipEncodingInfo()
            clip_info.uStreamEncoding = PxLApi.ClipEncodingFormat.H264
            clip_info.uDecimationFactor = decimation
            clip_info.playbackFrameRate = playback_frame_rate
            clip_info.playbackBitRate = PxLApi.ClipPlaybackDefaults.BITRATE_DEFAULT
            
            # Reset recording state
            self.is_recording = True
            self.capture_finished = False
            self.num_images_streamed = 0
            self.capture_rc = PxLApi.ReturnCode.ApiSuccess
            
            # Create termination callback
            @PxLApi._terminationFunction
            def term_fn(hCamera, numberOfFrameBlocksStreamed, retCode):
                self.num_images_streamed = numberOfFrameBlocksStreamed
                self.capture_rc = retCode
                self.capture_finished = True
                logger.info(f"📹 === CALLBACK FIRED ===")
                logger.info(f"   Frames captured: {numberOfFrameBlocksStreamed}")
                logger.info(f"   Return code: {retCode}")
                logger.info(f"   Success: {PxLApi.apiSuccess(retCode)}")
                return PxLApi.ReturnCode.ApiSuccess
            
            self.video_callback = term_fn
            
            # Start asynchronous video capture
            ret = PxLApi.getEncodedClip(
                self.camera_handle,
                num_images,
                str(h264_path),
                clip_info,
                term_fn
            )
            
            if not PxLApi.apiSuccess(ret[0]):
                self.is_recording = False
                raise RuntimeError(f"Failed to start video recording: {ret[0]}")
            
            logger.info("✅ Video recording started")
            
            return {
                "success": True,
                "recording": True,
                "duration": duration,
                "frameRate": playback_frame_rate,
                "cameraFrameRate": camera_fps,
                "decimation": decimation,
                "expectedImages": num_images,
                "h264Path": str(h264_path),
                "mp4Path": str(save_path)  # Changed from aviPath to mp4Path
            }
            
        except Exception as e:
            self.is_recording = False
            logger.error(f"Error starting video recording: {e}", exc_info=True)
            raise
    
    def stop_video_recording(self, h264_path: Path, mp4_path: Path) -> Dict:
        """
        Stop recording and finalize video file.
        
        This can be called to:
        1. Abort an ongoing recording early (user clicked stop)
        2. Finalize after natural completion (callback fired on its own)
        
        Args:
            h264_path: Path to intermediate H.264 file
            mp4_path: Path to final MP4 file
            
        Returns: Metadata dict with video information
        """
        if not self.is_recording:
            raise RuntimeError("Not currently recording")
        
        try:
            logger.info("🛑 Stopping video recording...")
            logger.info(f"   Capture finished flag: {self.capture_finished}")
            logger.info(f"   Is streaming: {self.is_streaming}")
            
            # If recording is still in progress (not yet finished), abort it by stopping the stream
            # This follows the PixeLink sample code pattern for aborting early
            if not self.capture_finished:
                logger.info("⏹️ Aborting capture by stopping stream (user stopped early)...")
                if self.is_streaming:
                    ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)
                    if PxLApi.apiSuccess(ret[0]):
                        self.is_streaming = False
                        logger.info("   Stream stopped successfully")
                    else:
                        logger.warning(f"⚠️ Failed to stop stream: {ret[0]}")
            else:
                logger.info("✅ Capture already finished naturally (full duration completed)")
            
            # Wait for the callback to complete (it should fire immediately after stream stop)
            logger.info("⏳ Waiting for capture callback to complete...")
            timeout = 10.0  # 10 second timeout
            start_time = time.time()
            poll_count = 0
            
            while not self.capture_finished:
                elapsed = time.time() - start_time
                poll_count += 1
                if poll_count % 20 == 0:  # Log every second
                    logger.info(f"   Still waiting... ({elapsed:.1f}s elapsed)")
                if elapsed > timeout:
                    logger.error(f"⏱️ Callback timeout after {timeout}s!")
                    logger.error(f"   Capture finished: {self.capture_finished}")
                    logger.error(f"   Images streamed: {self.num_images_streamed}")
                    logger.error(f"   Capture RC: {self.capture_rc}")
                    break
                time.sleep(0.05)  # Poll every 50ms
            
            callback_wait_time = time.time() - start_time
            logger.info(f"   Callback completed in {callback_wait_time:.3f}s")
            
            self.is_recording = False
            
            # Check capture result
            if self.capture_rc and not PxLApi.apiSuccess(self.capture_rc):
                if self.capture_rc == -2147483630:  # ApiStreamStopped
                    logger.info(f"📹 Capture was aborted (user stopped early)")
                elif self.capture_rc == PxLApi.ReturnCode.ApiSuccessWithFrameLoss:
                    logger.warning(f"⚠️ Some frames were lost during capture")
                else:
                    logger.warning(f"⚠️ Capture error code: {self.capture_rc}")
            
            num_images_captured = self.num_images_streamed
            logger.info(f"📹 Captured {num_images_captured} frames")
            
            # Check if H.264 file was created
            if not h264_path.exists():
                logger.error(f"❌ H.264 file not found: {h264_path}")
                # Try to look for any .h264 files in the directory
                import os
                parent_dir = h264_path.parent
                h264_files = list(parent_dir.glob("*.h264"))
                if h264_files:
                    h264_path = max(h264_files, key=lambda p: p.stat().st_mtime)
                    logger.info(f"Using most recent H.264 file: {h264_path}")
                else:
                    raise RuntimeError(f"H.264 file not found: {h264_path}")
            
            # Check H.264 file size
            h264_size = h264_path.stat().st_size if h264_path.exists() else 0
            logger.info(f"📄 H.264: {h264_size / 1024:.1f} KB")
            
            logger.info(f"🔄 Converting H.264 to MP4 container...")
            ret = PxLApi.formatClip(
                str(h264_path),
                str(mp4_path),
                PxLApi.ClipEncodingFormat.H264,
                PxLApi.ClipFileContainerFormat.MP4  # Changed from AVI to MP4 for browser compatibility
            )
            
            if not PxLApi.apiSuccess(ret[0]):
                logger.error(f"Failed to convert video to MP4: {ret[0]}")
                try:
                    h264_path.unlink()
                except:
                    pass
                raise RuntimeError(f"Failed to convert video to MP4: {ret[0]}")
            
            # Get file info
            file_size = mp4_path.stat().st_size if mp4_path.exists() else 0
            
            logger.info(f"✅ Video saved: {file_size / 1024 / 1024:.2f} MB")
            
            # Clean up H.264 file
            try:
                h264_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete H.264 file: {e}")
            
            # IMPORTANT: Restart the stream so the camera is ready for live feed and image capture
            # The streamer or next capture will use this stream
            logger.info("📹 Restarting camera stream after video recording...")
            ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
            if PxLApi.apiSuccess(ret[0]):
                self.is_streaming = True
                logger.info("✅ Stream restarted successfully")
            else:
                logger.warning(f"⚠️ Failed to restart stream: {ret[0]}")
            
            return {
                "success": True,
                "filename": mp4_path.name,
                "filepath": str(mp4_path.absolute()),
                "fileSize": file_size,
                "numImages": num_images_captured,
                "exposureTime": self.exposure,
                "gain": self.gain,
                "gamma": self.gamma,
                "width": self.width,
                "height": self.height,
                "metadata": {
                    "format": "MP4",  # Changed from AVI to MP4
                    "encoding": "H264",
                    "cameraConnected": self.is_connected
                }
            }
            
        except Exception as e:
            self.is_recording = False
            logger.error(f"Error stopping video recording: {e}", exc_info=True)
            raise
    
    def cancel_video_recording(self) -> bool:
        """Cancel ongoing video recording"""
        if not self.is_recording:
            return False
        
        try:
            logger.info("❌ Canceling video recording...")
            # Stop the stream to cancel the capture
            if self.is_streaming:
                PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)
                self.is_streaming = False
            
            self.is_recording = False
            self.capture_finished = True
            logger.info("✅ Video recording canceled")
            
            # Restart the stream for live feed and image capture
            logger.info("📹 Restarting camera stream after cancellation...")
            ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
            if PxLApi.apiSuccess(ret[0]):
                self.is_streaming = True
                logger.info("✅ Stream restarted successfully")
            else:
                logger.warning(f"⚠️ Failed to restart stream: {ret[0]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error canceling video recording: {e}")
            return False
    
    def _get_effective_frame_rate(self) -> float:
        """
        Get the effective frame rate being used by the camera.
        Tries ACTUAL_FRAME_RATE first, falls back to FRAME_RATE.
        """
        frame_rate_feature = PxLApi.FeatureId.FRAME_RATE
        
        # Try to use ACTUAL_FRAME_RATE if available
        ret = PxLApi.getCameraFeatures(self.camera_handle, PxLApi.FeatureId.ACTUAL_FRAME_RATE)
        if PxLApi.apiSuccess(ret[0]):
            camera_features = ret[1]
            if camera_features.Features[0].uFlags & PxLApi.FeatureFlags.PRESENCE:
                frame_rate_feature = PxLApi.FeatureId.ACTUAL_FRAME_RATE
        
        # Get the frame rate
        ret = PxLApi.getFeature(self.camera_handle, frame_rate_feature)
        if not PxLApi.apiSuccess(ret[0]):
            logger.warning("Could not get frame rate, using default 30 fps")
            return 30.0
        
        params = ret[2]
        return params[0]
    
    def is_video_recording(self) -> bool:
        """Check if currently recording video"""
        return self.is_recording
    
    def __init__(self, serial_number: Optional[str] = None):
        # Initialize video recording variables first
        self.__init_video_recording_vars()
        
        # Original initialization code
        self.serial_number = serial_number
        self.camera_handle = None
        self.is_connected = False
        self.is_streaming = False
        # Note: PixeLink API uses SECONDS for exposure internally
        # We'll store as milliseconds for UI/database, convert when needed
        self.exposure = 100.0  # Default 100ms
        self.gain = 1.0
        self.gamma = 1.0  # Default gamma value
        self.width = 1280
        self.height = 1024
        
        # Exposure limits (in milliseconds)
        self.exposure_min = 0.001  # 1 microsecond
        self.exposure_max = 10000.0  # 10 seconds
        
        # Gain limits
        self.gain_min = 1.0
        self.gain_max = 16.0
        
        # Gamma limits
        self.gamma_min = 0.5
        self.gamma_max = 4.0
        self.gamma_supported = False  # Will be set during initialization
        
        # Auto-exposure state
        self.auto_exposure_enabled = False
        self.auto_exposure_supported = False  # Will be set during initialization
        
        logger.info(f"PixelinkCamera initializing... PIXELINK_AVAILABLE={PIXELINK_AVAILABLE}")
        
        if PIXELINK_AVAILABLE:
            self._initialize_camera()
        else:
            logger.warning("⚠️ PixeLink SDK not available - running in SIMULATED mode")
            logger.warning("   Install pixelinkWrapper to use real camera")
    
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
