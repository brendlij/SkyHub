"""Orchestrates capture and upload operations on the node."""

import time
import logging
from node.cameras.base import Camera
from node.network.server_client import ServerClient
from node.network.event_client import EventClient


logger = logging.getLogger(__name__)


class CaptureService:
    """Coordinates camera capture and server upload."""
    
    def __init__(self, camera: Camera, server_client: ServerClient, event_client: EventClient = None):
        self.camera = camera
        self.server_client = server_client
        self.event_client = event_client
        self.camera_config = {}
    
    def capture_and_upload(self) -> bool:
        """
        Capture image and upload to server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Capture
            logger.info(f"Capturing from {self.camera.camera_id}...")
            capture = self.camera.capture_image()
            logger.info(f"Captured {capture.size_mb():.2f}MB")
            
            # Upload with camera config
            logger.info(f"Uploading to server...")
            response = self.server_client.upload_capture(capture, self.camera_config)
            logger.info(f"Upload successful: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Capture/upload failed: {e}")
            return False
    
    def capture_loop(self, interval_seconds: float = 10, camera_config: dict = None, config_refresh_interval: int = 60) -> None:
        """
        Run continuous capture loop with event-based config updates.
        
        Args:
            interval_seconds: Time between captures
            camera_config: Optional camera configuration dict (with exposure, gain, etc.)
            config_refresh_interval: Check for config events every N seconds
        """
        logger.info(f"Starting capture loop (interval: {interval_seconds}s)")
        self.camera_config = camera_config or {}
        self.camera.connect()
        
        last_config_check = 0
        
        try:
            while True:
                # Check for config change events
                import time as time_module
                current_time = time_module.time()
                if self.event_client and (current_time - last_config_check) > config_refresh_interval:
                    event = self.event_client.get_latest_config_event()
                    if event and event.get("data"):
                        new_config = event.get("data")
                        logger.info(f"🔄 Config update received via event: {new_config}")
                        
                        # Update camera config
                        self.camera_config.update(new_config)
                        
                        # Update camera object
                        if hasattr(self.camera, 'exposure'):
                            self.camera.exposure = new_config.get('exposure', self.camera.exposure)
                        if hasattr(self.camera, 'gain'):
                            self.camera.gain = new_config.get('gain', self.camera.gain)
                        
                        # Update interval
                        interval_seconds = new_config.get('capture_interval', interval_seconds)
                        logger.info(f"✅ Config updated: interval={interval_seconds}s, exposure={self.camera.exposure}s, gain={self.camera.gain}%")
                    
                    last_config_check = current_time
                
                self.capture_and_upload()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Capture loop interrupted by user")
        finally:
            self.camera.disconnect()
