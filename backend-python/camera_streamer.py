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

# Import shared camera utilities to avoid code duplication
from camera_utils import (
    PIXELINK_AVAILABLE, 
    PxLApi,
    capture_frame,
    generate_simulated_frame
)

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
        print(f"[STREAMER] start_streaming() called")
        if self.is_streaming:
            print(f"[STREAMER] Already streaming, ignoring")
            logger.warning("Streaming already active")
            return
            
        if not PIXELINK_AVAILABLE or not self.camera_handle:
            print(f"[STREAMER] No camera, using simulated stream")
            logger.warning("Camera not available, using simulated stream")
        
        # Mark as streaming BEFORE starting the loop
        # This prevents multiple streams from being started
        self.is_streaming = True
        print(f"[STREAMER] Marked as streaming, creating background task...")
        logger.info("🚀 Starting camera streaming task...")
        
        # Create and start the stream task in background (fire and forget)
        self.stream_task = asyncio.create_task(self._stream_loop())
        print(f"[STREAMER] Stream task created and running in background")
        logger.info("✅ Camera streaming task created (running in background)")
        
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
        """Register a new WebSocket client - returns IMMEDIATELY."""
        print(f"[STREAMER] Adding client... (current count: {len(self.active_clients)})")
        self.active_clients.add(websocket)
        print(f"[STREAMER] Client registered. Total clients: {len(self.active_clients)}")
        logger.info(f"🔌 Client registered. Total clients: {len(self.active_clients)}")
        
        # Start streaming if this is the first client
        # Fire and forget - completely non-blocking, no waits
        if len(self.active_clients) == 1:
            if not self.is_streaming:
                print(f"[STREAMER] First client - starting stream in background...")
                logger.info("📹 Initiating camera stream in background (first client)...")
                # Fire and forget - don't await, don't wait
                asyncio.create_task(self.start_streaming())
                print(f"[STREAMER] Stream task created, returning immediately")
            else:
                print(f"[STREAMER] Stream already active")
                logger.info("📹 Stream already active")
        # Return immediately - no delays whatsoever
        print(f"[STREAMER] add_client() returning (no blocking)")
            
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
        print(f"[STREAM_LOOP] Starting stream loop")
        logger.info("🎬 Starting stream loop")
        logger.info(f"   Initial state: is_streaming={self.is_streaming}, clients={len(self.active_clients)}")
        
        # Start camera streaming in the background (non-blocking, fire and forget)
        # We'll start capturing frames immediately and let the stream start happen async
        if PIXELINK_AVAILABLE and self.camera_handle:
            print(f"[STREAM_LOOP] Initiating camera hardware stream...")
            async def start_stream_async():
                """Start stream in background without blocking"""
                try:
                    print(f"[CAMERA] Calling PxLApi.setStreamState(START)...")
                    def do_start_stream():
                        try:
                            ret = PxLApi.setStreamState(self.camera_handle, PxLApi.StreamState.START)
                            if PxLApi.apiSuccess(ret[0]):
                                print(f"[CAMERA] Stream started successfully")
                                logger.info("✅ Camera stream started")
                                return True
                            elif ret[0] == -2147483644:  # ApiAlreadyStreamingError
                                print(f"[CAMERA] Already streaming")
                                logger.info("✅ Camera already streaming")
                                return True
                            else:
                                print(f"[CAMERA] Stream start returned: {ret[0]}")
                                logger.warning(f"Stream start returned: {ret[0]}")
                                return False
                        except Exception as e:
                            print(f"[CAMERA] Exception in stream start: {e}")
                            logger.error(f"Exception in stream start: {e}")
                            return False
                    
                    await asyncio.to_thread(do_start_stream)
                    print(f"[CAMERA] Stream start complete")
                except Exception as e:
                    print(f"[CAMERA] Error in async stream start: {e}")
                    logger.error(f"Error in async stream start: {e}")
            
            # Start stream in background, don't wait for it
            asyncio.create_task(start_stream_async())
            logger.info("📹 Camera stream start initiated in background")
            print(f"[STREAM_LOOP] Camera start task created, continuing...")
            # Give it just a tiny moment to potentially start
            await asyncio.sleep(0.05)
        
        print(f"[STREAM_LOOP] Entering main capture loop")
        
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
                    # Don't log every failure - only after multiple failures
                    if frame_count % 10 == 0:  # Log every 10th failure
                        logger.debug("Frame capture failed, retrying...")
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
        Uses shared utility function to avoid code duplication.
        """
        return capture_frame(self.camera_handle, max_retries=3)
    
    def _capture_simulated_frame(self) -> np.ndarray:
        """
        Generate a simulated test pattern frame.
        Uses shared utility function to avoid code duplication.
        """
        return generate_simulated_frame(self.width, self.height)
    
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
