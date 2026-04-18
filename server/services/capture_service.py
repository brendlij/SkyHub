"""Server-side capture orchestration."""

from datetime import datetime
from server.services.storage_service import StorageService
from server.repositories.capture_repository import CaptureRepository
from server.models.capture import CaptureUploadResponse


class CaptureService:
    """Orchestrates capture storage and metadata tracking."""
    
    def __init__(self, storage_service: StorageService, repository: CaptureRepository):
        self.storage = storage_service
        self.repository = repository
    
    def store_capture(
        self,
        image_bytes: bytes,
        node_id: str,
        camera_id: str,
        timestamp: datetime,
        exposure: float,
        gain: float,
    ) -> CaptureUploadResponse:
        """
        Store capture file and metadata.
        
        Args:
            image_bytes: Raw image data
            node_id: Source node
            camera_id: Source camera
            timestamp: Capture timestamp
            exposure: Exposure setting
            gain: Gain setting
            
        Returns:
            CaptureUploadResponse with saved file info
        """
        # Save file
        file_info = self.storage.save_capture(
            image_bytes=image_bytes,
            node_id=node_id,
            camera_id=camera_id,
            timestamp=timestamp,
        )
        
        # Save metadata to database
        self.repository.create_capture(
            uuid=file_info["uuid"],
            node_id=node_id,
            camera_id=camera_id,
            timestamp=timestamp,
            date_folder=file_info["date_folder"],
            period=file_info["period"],
            file_path=file_info["path"],
            size_bytes=file_info["size_bytes"],
        )
        
        return CaptureUploadResponse(
            node_id=node_id,
            camera_id=camera_id,
            filename=file_info["filename"],
            path=file_info["path"],
            size_bytes=file_info["size_bytes"],
            timestamp=timestamp,
        )
