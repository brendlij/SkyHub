"""Server data models and schemas."""

from pydantic import BaseModel
from datetime import datetime


class CaptureUploadRequest(BaseModel):
    """Request body for capture upload."""
    
    node_id: str
    camera_id: str
    timestamp: datetime
    exposure: float = 0.0
    gain: float = 0.0


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
