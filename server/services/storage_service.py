"""Handles file storage operations on the server."""

from pathlib import Path
from uuid import uuid4
from datetime import datetime
from server.astronomy import AstronomyService


class StorageService:
    """Manages capture file storage with day/night organization."""
    
    def __init__(self, storage_root: str, latitude: float = 48.0, longitude: float = 16.0):
        self.storage_root = Path(storage_root)
        self.captures_dir = self.storage_root / "captures"
        self.astronomy = AstronomyService(latitude=latitude, longitude=longitude)
    
    def initialize(self) -> None:
        """Create storage directories."""
        self.captures_dir.mkdir(parents=True, exist_ok=True)
    
    def save_capture(
        self,
        image_bytes: bytes,
        node_id: str,
        camera_id: str,
        timestamp: datetime | None = None,
    ) -> dict:
        """
        Save capture file to disk organized by date and day/night.
        
        Folder structure:
        captures/
        ├── 2026-04-18/
        │   ├── day/
        │   │   └── 2026-04-18_day_001_node-1_camera-1.png
        │   └── night/
        │       └── 2026-04-18_night_001_node-1_camera-1.png
        
        Args:
            image_bytes: Raw image data
            node_id: Source node ID
            camera_id: Source camera ID
            timestamp: Capture timestamp (UTC). If None, uses current time.
            
        Returns:
            Dict with filename, path, size, uuid, date_folder, and period
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Get date folder and day/night period
        date_folder, period = self.astronomy.get_session_date(timestamp)
        
        # Create directory structure
        capture_dir = self.captures_dir / date_folder / period
        capture_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate sequence number by counting existing PNG files
        existing_pngs = list(capture_dir.glob("*.png"))
        sequence_num = len(existing_pngs) + 1
        
        # Generate unique ID and filename with timestamp
        unique_id = uuid4()
        time_str = timestamp.strftime("%H-%M-%S")
        filename = f"{date_folder}_{time_str}_{period}_{sequence_num:03d}_{node_id}_{camera_id}.png"
        file_path = capture_dir / filename
        
        # Write file
        file_path.write_bytes(image_bytes)
        
        return {
            "uuid": str(unique_id),
            "filename": filename,
            "path": str(file_path),
            "size_bytes": len(image_bytes),
            "date_folder": date_folder,
            "period": period,
        }
