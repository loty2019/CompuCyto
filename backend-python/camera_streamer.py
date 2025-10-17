"""
Camera Streaming Module

Handles continuous frame capture and encoding for WebSocket streaming.
Uses PixeLink API's getNextFrame for efficient frame grabbing.
"""
import logging
import asyncio
import base64
import io
from typing import Optional, Set
import numpy as np
from PIL import Image

try:
    from pixelinkWrapper import PxLApi
    PIXELINK_AVAILABLE = True
except:
    PIXELINK_AVAILABLE = False
    PxLApi = None

logger = logging.getLogger(__name__)


class CameraStreamer:
    """
    Manages continuous camera streaming for multiple WebSocket clients.
    Captures frames from PixeLink camera and encodes them as JPEG for streaming.
    """
    
    def __init__(self, camera_handle=None, width=1280, height=1024):
        self.camera_handle = camera_handle
        self.width = width
        self.height = height
        self.is_streaming = False
        self.active_clients: Set = set()
        self.stream_task: Optional[asyncio.Task] = None
        self.current_frame: Optional[bytes] = None
        self.frame_lock = asyncio.Lock()
        self.capture_lock = asyncio.Lock()  # Prevent capture conflicts
        self.paused = False  # Pause streaming during captures
        
    def set_camera(self, camera_handle, width, height):
        """Update camera handle and dimensions."""
        self.camera_handle = camera_handle
        self.width = width
        self.height = height
        
    async def start_streaming(self):
        """Start the streaming loop."""
        if self.is_streaming:
            logger.warning("Streaming already active")
            return
            
        if not PIXELINK_AVAILABLE or not self.camera_handle:
            logger.warning("Camera not available, using simulated stream")
        
        self.is_streaming = True
        self.stream_task = asyncio.create_task(self._stream_loop())
        logger.info("Camera streaming started")
        
    async def stop_streaming(self):
        """Stop the streaming loop."""
        if not self.is_streaming:
            return
            
        self.is_streaming = False
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
        logger.info("Camera streaming stopped")
        
    async def add_client(self, websocket):
        """Register a new WebSocket client."""
        self.active_clients.add(websocket)
        logger.info(f"🔌 Client connected. Total clients: {len(self.active_clients)}")
        
        # Start streaming if this is the first client
        if len(self.active_clients) == 1 and not self.is_streaming:
            logger.info("📹 Starting camera stream (first client)")
            await self.start_streaming()
            
    async def remove_client(self, websocket):
        """Unregister a WebSocket client."""
        self.active_clients.discard(websocket)
        logger.info(f"🔌 Client disconnected. Total clients: {len(self.active_clients)}")
        
        # Stop streaming if no more clients
        if len(self.active_clients) == 0 and self.is_streaming:
            logger.info("⏹️  Stopping camera stream (no more clients)")
            await self.stop_streaming()
            
    async def _stream_loop(self):
        """
        Main streaming loop - continuously captures and broadcasts frames.
        Runs in background task while clients are connected.
        """
        logger.info("🎬 Starting stream loop")
        logger.info(f"   Initial state: is_streaming={self.is_streaming}, clients={len(self.active_clients)}")
        
        # Start camera streaming if available
        if PIXELINK_AVAILABLE and self.camera_handle:
            ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
            if not PxLApi.apiSuccess(ret[0]):
                logger.error(f"Failed to start camera stream: {ret[0]}")
                return
        
        frame_count = 0
        last_status_log = 0
        try:
            while self.is_streaming:
                # Check if we still have clients - stop immediately if not
                if len(self.active_clients) == 0:
                    logger.warning("⚠️ No active clients detected in loop!")
                    logger.info("⏹️ No active clients, stopping stream loop")
                    break
                
                # Check if paused (during capture)
                if self.paused:
                    await asyncio.sleep(0.05)  # Wait while paused
                    continue
                
                # Capture frame
                if PIXELINK_AVAILABLE and self.camera_handle:
                    frame_data = await asyncio.to_thread(self._capture_real_frame)
                else:
                    frame_data = await asyncio.to_thread(self._capture_simulated_frame)
                
                if frame_data is None:
                    logger.warning("Frame capture failed, retrying...")
                    await asyncio.sleep(0.1)
                    continue
                
                # Encode frame as JPEG
                jpeg_data = await asyncio.to_thread(self._encode_jpeg, frame_data)
                
                # Store current frame
                async with self.frame_lock:
                    self.current_frame = jpeg_data
                
                # Broadcast to all connected clients
                if self.active_clients:
                    await self._broadcast_frame(jpeg_data)
                else:
                    logger.warning("⚠️ No clients to broadcast to, stopping")
                    break
                
                frame_count += 1
                
                # Log status every 300 frames (~10 seconds at 30fps)
                if frame_count - last_status_log >= 300:
                    logger.info(f"📊 Streaming status: {frame_count} frames sent, {len(self.active_clients)} active client(s)")
                    last_status_log = frame_count
                
                # Small delay to control frame rate (~30 FPS)
                await asyncio.sleep(0.033)
                
        except asyncio.CancelledError:
            logger.info("Stream loop cancelled")
        except Exception as e:
            logger.error(f"Stream loop error: {e}", exc_info=True)
        finally:
            # Mark as not streaming
            self.is_streaming = False
            # Stop camera streaming
            if PIXELINK_AVAILABLE and self.camera_handle:
                PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.STOP)
            logger.info(f"🏁 Stream loop ended. Total frames: {frame_count}, Active clients: {len(self.active_clients)}")
    
    def _capture_real_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the PixeLink camera.
        Uses getNextFrame approach from sample code.
        """
        try:
            # Determine image size
            width, height, bytes_per_pixel = self._determine_raw_image_size()
            if width == 0 or height == 0:
                return None
            
            # Create NumPy buffer
            np_image = np.zeros([height, width * bytes_per_pixel], dtype=np.uint8)
            
            # Get next frame with retry
            MAX_RETRIES = 3
            for attempt in range(MAX_RETRIES):
                ret = PxLApi.getNextNumPyFrame(self.camera_handle, np_image)
                if PxLApi.apiSuccess(ret[0]):
                    break
                    
                # Check for fatal errors
                if ret[0] in [PxLApi.ReturnCode.ApiStreamStopped, 
                             PxLApi.ReturnCode.ApiNoCameraAvailableError]:
                    logger.error(f"Fatal camera error: {ret[0]}")
                    return None
                    
                if attempt < MAX_RETRIES - 1:
                    logger.debug(f"Frame grab attempt {attempt + 1} failed, retrying...")
            
            if not PxLApi.apiSuccess(ret[0]):
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
            logger.error(f"Real frame capture error: {e}")
            return None
    
    def _determine_raw_image_size(self):
        """Get image dimensions from camera ROI."""
        try:
            # Get ROI
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.ROI)
            if not PxLApi.apiSuccess(ret[0]):
                return (0, 0, 0)
            
            params = ret[2]
            roi_width = params[PxLApi.RoiParams.WIDTH]
            roi_height = params[PxLApi.RoiParams.HEIGHT]
            
            # Get pixel addressing
            pixel_addressing_x = 1
            pixel_addressing_y = 1
            
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.PIXEL_ADDRESSING)
            if PxLApi.apiSuccess(ret[0]):
                params = ret[2]
                if params[PxLApi.PixelAddressingParams.MODE] != PxLApi.PixelAddressingModes.DECIMATE:
                    pixel_addressing_x = max(1, int(params[PxLApi.PixelAddressingParams.X_VALUE]))
                    pixel_addressing_y = max(1, int(params[PxLApi.PixelAddressingParams.Y_VALUE]))
            
            width = int(roi_width / pixel_addressing_x)
            height = int(roi_height / pixel_addressing_y)
            
            # Get bytes per pixel
            ret = PxLApi.getFeature(self.camera_handle, PxLApi.FeatureId.PIXEL_FORMAT)
            if not PxLApi.apiSuccess(ret[0]):
                return (0, 0, 0)
            
            pixel_format = int(ret[2][0])
            bytes_per_pixel = PxLApi.getBytesPerPixel(pixel_format)
            
            return (width, height, bytes_per_pixel)
            
        except Exception as e:
            logger.error(f"Error determining image size: {e}")
            return (0, 0, 0)
    
    def _capture_simulated_frame(self) -> np.ndarray:
        """Generate a simulated test pattern frame."""
        # Create a gradient pattern for testing
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Create animated gradient
        import time
        phase = int(time.time() * 50) % 256
        
        for i in range(self.height):
            for j in range(self.width):
                image[i, j] = [
                    (i + phase) % 256,
                    (j + phase) % 256,
                    ((i + j + phase) // 2) % 256
                ]
        
        return image
    
    def _encode_jpeg(self, frame_data: np.ndarray, quality: int = 85) -> bytes:
        """
        Encode numpy array as JPEG bytes.
        
        Args:
            frame_data: RGB numpy array
            quality: JPEG quality (1-95)
        
        Returns:
            JPEG encoded bytes
        """
        image = Image.fromarray(frame_data, mode='RGB')
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality)
        return buffer.getvalue()
    
    async def _broadcast_frame(self, jpeg_data: bytes):
        """
        Send frame to all connected WebSocket clients.
        Encodes as base64 for JSON transmission.
        """
        if not self.active_clients:
            logger.warning("⚠️ Broadcasting but no active clients!")
            return
            
        # Encode as base64 for WebSocket JSON transmission
        base64_data = base64.b64encode(jpeg_data).decode('utf-8')
        
        message = {
            "type": "frame",
            "data": base64_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Send to all clients, remove disconnected ones
        disconnected = set()
        for client in list(self.active_clients):  # Convert to list to avoid modification during iteration
            try:
                await client.send_json(message)
            except Exception as e:
                logger.warning(f"⚠️ Failed to send to client, marking for removal: {e}")
                disconnected.add(client)
        
        # Clean up disconnected clients
        for client in disconnected:
            self.active_clients.discard(client)
            logger.info(f"🧹 Cleaned up stale client. Remaining: {len(self.active_clients)}")
            
        # Stop streaming if no clients left after cleanup
        if len(self.active_clients) == 0 and self.is_streaming:
            logger.info("⏹️ No clients remaining after cleanup, stopping stream")
            await self.stop_streaming()
    
    async def get_current_frame(self) -> Optional[bytes]:
        """Get the most recent frame (JPEG bytes)."""
        async with self.frame_lock:
            return self.current_frame
    
    async def pause_streaming(self):
        """Pause streaming temporarily (for captures)."""
        logger.info("⏸️ Pausing stream for capture")
        self.paused = True
        # Wait a moment for current frame capture to complete
        await asyncio.sleep(0.1)
    
    async def resume_streaming(self):
        """Resume streaming after capture."""
        logger.info("▶️ Resuming stream after capture")
        self.paused = False


# Global streamer instance
streamer = CameraStreamer()
