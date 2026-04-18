"""Data models for capture operations."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class CaptureResult:
    """Result of a camera capture operation."""
    
    node_id: str
    camera_id: str
    timestamp: datetime
    image_bytes: bytes
    exposure: float | None = None
    gain: float | None = None
    
    def size_mb(self) -> float:
        """Size of image in megabytes."""
        return len(self.image_bytes) / (1024 * 1024)
