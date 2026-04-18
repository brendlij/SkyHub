"""Base class for camera implementations."""

from abc import ABC, abstractmethod
from datetime import datetime
from node.capture.models import CaptureResult


class Camera(ABC):
    """Abstract base class for all camera implementations."""
    
    def __init__(self, camera_id: str, node_id: str):
        self.camera_id = camera_id
        self.node_id = node_id
        self.connected = False
    
    @abstractmethod
    def connect(self) -> None:
        """Connect to the camera."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the camera."""
        pass
    
    @abstractmethod
    def capture_image(self) -> CaptureResult:
        """
        Capture an image from the camera.
        
        Returns:
            CaptureResult with image bytes and metadata.
        """
        pass
    
    @abstractmethod
    def get_info(self) -> dict:
        """Return camera metadata (name, resolution, etc.)."""
        pass
