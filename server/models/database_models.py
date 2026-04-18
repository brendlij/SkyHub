"""SQLAlchemy ORM models for database."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text
from server.database import Base


class CaptureModel(Base):
    """Database model for captured images."""
    
    __tablename__ = "captures"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False)
    node_id = Column(String(50), index=True, nullable=False)
    camera_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    date_folder = Column(String(10), index=True, nullable=False)  # "2026-04-18"
    period = Column(String(5), index=True, nullable=False)  # "day" or "night"
    file_path = Column(String(500), nullable=False)  # Relative path: captures/2026-04-18/day/node-1_camera-1_uuid.png
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Capture {self.uuid} ({self.node_id}/{self.camera_id}) {self.date_folder}/{self.period}>"
