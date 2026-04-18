"""Configuration models and storage."""

from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from server.database import Base


class ConfigOverride(Base):
    """Runtime configuration overrides stored in database."""
    
    __tablename__ = "config_overrides"
    
    key = Column(String(100), primary_key=True, index=True)
    scope = Column(String(50), default="system")  # "system", "node:{id}", "camera:{id}"
    value = Column(Text, nullable=False)  # JSON string
    description = Column(String(500))
    set_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ConfigOverride {self.scope}/{self.key}={self.value}>"


class CameraConfig(Base):
    """Camera-specific configuration."""
    
    __tablename__ = "camera_configs"
    
    id = Column(String(50), primary_key=True)  # "node-1:camera-1"
    camera_id = Column(String(50), index=True)
    node_id = Column(String(50), index=True)
    
    # Camera parameters
    exposure = Column(String(50), default="5.0")
    gain = Column(String(50), default="100")
    resolution = Column(String(20), default="1920x1080")
    frame_rate = Column(String(10), default="30")
    
    # Storage
    enabled = Column(String(5), default="true")  # "true" or "false"
    capture_interval = Column(String(10), default="10.0")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CameraConfig {self.id}>"
