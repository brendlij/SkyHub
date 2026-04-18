"""Repository for capture data access."""

from datetime import datetime
from sqlalchemy.orm import Session
from server.models.database_models import CaptureModel


class CaptureRepository:
    """Handles all capture data operations."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def create_capture(
        self,
        uuid: str,
        node_id: str,
        camera_id: str,
        timestamp: datetime,
        date_folder: str,
        period: str,
        file_path: str,
        size_bytes: int,
    ) -> CaptureModel:
        """Create and save a new capture record."""
        capture = CaptureModel(
            uuid=uuid,
            node_id=node_id,
            camera_id=camera_id,
            timestamp=timestamp,
            date_folder=date_folder,
            period=period,
            file_path=file_path,
            size_bytes=size_bytes,
        )
        self.db.add(capture)
        self.db.commit()
        self.db.refresh(capture)
        return capture
    
    def get_capture_by_uuid(self, uuid: str) -> CaptureModel | None:
        """Get a capture by UUID."""
        return self.db.query(CaptureModel).filter(CaptureModel.uuid == uuid).first()
    
    def get_captures_by_date(self, date_folder: str) -> list[CaptureModel]:
        """Get all captures for a specific date."""
        return self.db.query(CaptureModel).filter(CaptureModel.date_folder == date_folder).all()
    
    def get_captures_by_date_and_period(self, date_folder: str, period: str) -> list[CaptureModel]:
        """Get captures for a specific date and period (day/night)."""
        return self.db.query(CaptureModel).filter(
            CaptureModel.date_folder == date_folder,
            CaptureModel.period == period,
        ).all()
    
    def get_captures_by_node(self, node_id: str, limit: int = 100) -> list[CaptureModel]:
        """Get recent captures from a specific node."""
        return self.db.query(CaptureModel).filter(
            CaptureModel.node_id == node_id
        ).order_by(CaptureModel.timestamp.desc()).limit(limit).all()
    
    def get_all_captures(self, limit: int = 1000) -> list[CaptureModel]:
        """Get all captures (most recent first)."""
        return self.db.query(CaptureModel).order_by(
            CaptureModel.timestamp.desc()
        ).limit(limit).all()
    
    def delete_capture(self, uuid: str) -> bool:
        """Delete a capture by UUID."""
        capture = self.get_capture_by_uuid(uuid)
        if capture:
            self.db.delete(capture)
            self.db.commit()
            return True
        return False
    
    def count_captures(self) -> int:
        """Get total number of captures."""
        return self.db.query(CaptureModel).count()
    
    def count_captures_by_date(self, date_folder: str) -> int:
        """Count captures for a specific date."""
        return self.db.query(CaptureModel).filter(
            CaptureModel.date_folder == date_folder
        ).count()
