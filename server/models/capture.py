"""Server data models and schemas."""

from pydantic import BaseModel
from datetime import datetime


class CaptureUploadRequest(BaseModel):
    """Request body for capture upload."""
    
    node_id: str
    camera_id: str
    timestamp: datetime
    exposure: float = None
    gain: float = None
    resolution: str = None
    frame_rate: int = None
    white_balance: str = None
    iso: int = None


class CaptureUploadResponse(BaseModel):
    """Response after successful capture upload."""
    
    node_id: str
    camera_id: str
    filename: str
    path: str
    size_bytes: int
    timestamp: datetime


class CaptureDetailResponse(BaseModel):
    """Detailed capture info from database."""
    
    id: int
    uuid: str
    node_id: str
    camera_id: str
    filename: str | None = None
    timestamp: datetime
    date_folder: str
    period: str
    file_path: str
    size_bytes: int
    
    # Camera metadata
    exposure: float | None = None
    gain: float | None = None
    resolution: str | None = None
    frame_rate: int | None = None
    white_balance: str | None = None
    iso: int | None = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class CaptureListResponse(BaseModel):
    """List of captures with pagination."""
    
    total: int
    captures: list[CaptureDetailResponse]


class CaptureDeleteResponse(BaseModel):
    """Response after delete."""
    
    success: bool
    message: str
    uuid: str


class StatsByPeriod(BaseModel):
    """Statistics for a specific period."""
    
    period: str  # "day" or "night"
    count: int
    total_size_bytes: int


class StatsByDate(BaseModel):
    """Statistics for a specific date."""
    
    date_folder: str
    count: int
    total_size_bytes: int
    by_period: list[StatsByPeriod]


class StatsByNode(BaseModel):
    """Statistics for a specific node."""
    
    node_id: str
    count: int
    total_size_bytes: int
    cameras: list[str]


class OverallStats(BaseModel):
    """Overall system statistics."""
    
    total_captures: int
    total_size_bytes: int
    total_size_gb: float
    date_count: int
    node_count: int
    camera_count: int
    day_captures: int
    night_captures: int
    by_date: list[StatsByDate]
    by_node: list[StatsByNode]


class StorageHealth(BaseModel):
    """Storage system health information."""
    
    status: str  # "ok" or "warning" or "error"
    storage_root: str
    total_size_bytes: int
    total_size_gb: float
    capture_count: int
    captures_dir_exists: bool
    db_file_exists: bool


class DatabaseHealth(BaseModel):
    """Database health information."""
    
    status: str  # "ok" or "error"
    database_type: str
    connection_ok: bool
    table_count: int
    record_count: int
    error: str | None = None


class HealthResponse(BaseModel):
    """Overall health status."""
    
    status: str  # "ok" or "degraded" or "error"
    timestamp: datetime
    server_uptime_seconds: float | None = None
    storage: StorageHealth
    database: DatabaseHealth
