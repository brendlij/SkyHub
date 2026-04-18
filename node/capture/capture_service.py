"""Orchestrates capture and upload operations on the node."""

import time
import logging
from node.cameras.base import Camera
from node.network.server_client import ServerClient


logger = logging.getLogger(__name__)


class CaptureService:
    """Coordinates camera capture and server upload."""
    
    def __init__(self, camera: Camera, server_client: ServerClient):
        self.camera = camera
        self.server_client = server_client
    
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
            
            # Upload
            logger.info(f"Uploading to server...")
            response = self.server_client.upload_capture(capture)
            logger.info(f"Upload successful: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Capture/upload failed: {e}")
            return False
    
    def capture_loop(self, interval_seconds: float = 10) -> None:
        """
        Run continuous capture loop.
        
        Args:
            interval_seconds: Time between captures
        """
        logger.info(f"Starting capture loop (interval: {interval_seconds}s)")
        self.camera.connect()
        
        try:
            while True:
                self.capture_and_upload()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Capture loop interrupted by user")
        finally:
            self.camera.disconnect()
