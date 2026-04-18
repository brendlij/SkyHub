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
        exposure: float = None,
        gain: float = None,
        resolution: str = None,
        frame_rate: int = None,
        white_balance: str = None,
        iso: int = None,
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
            exposure=exposure,
            gain=gain,
            resolution=resolution,
            frame_rate=frame_rate,
            white_balance=white_balance,
            iso=iso,
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
    
    def get_stats_by_date(self) -> dict:
        """Get statistics grouped by date."""
        from sqlalchemy import func
        
        results = self.db.query(
            CaptureModel.date_folder,
            CaptureModel.period,
            func.count(CaptureModel.id).label('count'),
            func.sum(CaptureModel.size_bytes).label('total_size'),
        ).group_by(CaptureModel.date_folder, CaptureModel.period).all()
        
        stats = {}
        for date_folder, period, count, total_size in results:
            if date_folder not in stats:
                stats[date_folder] = {'day': {}, 'night': {}}
            stats[date_folder][period] = {
                'count': count or 0,
                'total_size_bytes': total_size or 0,
            }
        
        return stats
    
    def get_stats_by_node(self) -> dict:
        """Get statistics grouped by node."""
        from sqlalchemy import func
        
        results = self.db.query(
            CaptureModel.node_id,
            CaptureModel.camera_id,
            func.count(CaptureModel.id).label('count'),
            func.sum(CaptureModel.size_bytes).label('total_size'),
        ).group_by(CaptureModel.node_id, CaptureModel.camera_id).all()
        
        stats = {}
        for node_id, camera_id, count, total_size in results:
            if node_id not in stats:
                stats[node_id] = {'cameras': {}, 'count': 0, 'total_size': 0}
            stats[node_id]['cameras'][camera_id] = {
                'count': count or 0,
                'total_size_bytes': total_size or 0,
            }
            stats[node_id]['count'] += count or 0
            stats[node_id]['total_size'] += total_size or 0
        
        return stats
    
    def get_total_size_bytes(self) -> int:
        """Get total size of all captures."""
        from sqlalchemy import func
        
        result = self.db.query(func.sum(CaptureModel.size_bytes)).scalar()
        return result or 0
    
    def get_period_counts(self) -> dict:
        """Get count of captures by period (day/night)."""
        from sqlalchemy import func
        
        results = self.db.query(
            CaptureModel.period,
            func.count(CaptureModel.id).label('count'),
        ).group_by(CaptureModel.period).all()
        
        stats = {}
        for period, count in results:
            stats[period] = count or 0
        
        return stats
    
    def get_unique_dates(self) -> list[str]:
        """Get list of all unique dates."""
        dates = self.db.query(CaptureModel.date_folder).distinct().order_by(
            CaptureModel.date_folder.desc()
        ).all()
        return [d[0] for d in dates]
    
    def get_unique_nodes(self) -> list[str]:
        """Get list of all unique node IDs."""
        nodes = self.db.query(CaptureModel.node_id).distinct().all()
        return [n[0] for n in nodes]
    
    def get_unique_cameras(self) -> list[str]:
        """Get list of all unique camera IDs."""
        cameras = self.db.query(CaptureModel.camera_id).distinct().all()
        return [c[0] for c in cameras]
