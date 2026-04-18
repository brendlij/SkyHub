"""FastAPI routes for the server."""

from fastapi import APIRouter, UploadFile, Form, HTTPException
from datetime import datetime
from server.services.capture_service import CaptureService
from server.models.capture import (
    CaptureUploadResponse, 
    CaptureDetailResponse,
    CaptureListResponse,
    CaptureDeleteResponse,
)


router = APIRouter(prefix="/api", tags=["captures"])


def init_routes(capture_service: CaptureService) -> APIRouter:
    """
    Initialize routes with service dependency.
    
    Args:
        capture_service: CaptureService instance
        
    Returns:
        Configured router
    """
    
    @router.post("/captures", response_model=CaptureUploadResponse)
    async def upload_capture(
        file: UploadFile,
        node_id: str = Form(...),
        camera_id: str = Form(...),
        timestamp: str = Form(...),
        exposure: float = Form(0.0),
        gain: float = Form(0.0),
    ) -> CaptureUploadResponse:
        """
        Upload a capture from a node.
        
        Parameters:
            file: Image file
            node_id: Source node ID
            camera_id: Source camera ID
            timestamp: ISO format timestamp
            exposure: Exposure value
            gain: Gain value
        """
        # Read file
        content = await file.read()
        
        # Parse timestamp
        capture_timestamp = datetime.fromisoformat(timestamp)
        
        # Store and return
        response = capture_service.store_capture(
            image_bytes=content,
            node_id=node_id,
            camera_id=camera_id,
            timestamp=capture_timestamp,
            exposure=exposure,
            gain=gain,
        )
        return response
    
    @router.get("/captures", response_model=CaptureListResponse)
    async def list_all_captures(limit: int = 100, skip: int = 0) -> CaptureListResponse:
        """
        Get all captures (most recent first).
        
        Parameters:
            limit: Max captures to return (default: 100)
            skip: Number of captures to skip
        """
        captures = capture_service.repository.get_all_captures(limit=limit)
        total = capture_service.repository.count_captures()
        
        # Convert to response models
        capture_responses = [
            CaptureDetailResponse(
                id=c.id,
                uuid=c.uuid,
                node_id=c.node_id,
                camera_id=c.camera_id,
                filename=c.uuid + ".png",
                timestamp=c.timestamp,
                date_folder=c.date_folder,
                period=c.period,
                file_path=c.file_path,
                size_bytes=c.size_bytes,
                created_at=c.created_at,
            )
            for c in captures
        ]
        
        return CaptureListResponse(total=total, captures=capture_responses)
    
    @router.get("/captures/{date_folder}", response_model=CaptureListResponse)
    async def list_captures_by_date(date_folder: str) -> CaptureListResponse:
        """
        Get captures for a specific date (YYYY-MM-DD).
        
        Parameters:
            date_folder: Date string (e.g., "2026-04-18")
        """
        captures = capture_service.repository.get_captures_by_date(date_folder)
        total = len(captures)
        
        capture_responses = [
            CaptureDetailResponse(
                id=c.id,
                uuid=c.uuid,
                node_id=c.node_id,
                camera_id=c.camera_id,
                filename=c.uuid + ".png",
                timestamp=c.timestamp,
                date_folder=c.date_folder,
                period=c.period,
                file_path=c.file_path,
                size_bytes=c.size_bytes,
                created_at=c.created_at,
            )
            for c in captures
        ]
        
        return CaptureListResponse(total=total, captures=capture_responses)
    
    @router.get("/captures/{date_folder}/{period}", response_model=CaptureListResponse)
    async def list_captures_by_date_and_period(
        date_folder: str, 
        period: str,
    ) -> CaptureListResponse:
        """
        Get captures for a specific date and period (day/night).
        
        Parameters:
            date_folder: Date string (e.g., "2026-04-18")
            period: "day" or "night"
        """
        if period not in ["day", "night"]:
            raise HTTPException(status_code=400, detail='Period must be "day" or "night"')
        
        captures = capture_service.repository.get_captures_by_date_and_period(
            date_folder, period
        )
        total = len(captures)
        
        capture_responses = [
            CaptureDetailResponse(
                id=c.id,
                uuid=c.uuid,
                node_id=c.node_id,
                camera_id=c.camera_id,
                filename=c.uuid + ".png",
                timestamp=c.timestamp,
                date_folder=c.date_folder,
                period=c.period,
                file_path=c.file_path,
                size_bytes=c.size_bytes,
                created_at=c.created_at,
            )
            for c in captures
        ]
        
        return CaptureListResponse(total=total, captures=capture_responses)
    
    @router.get("/nodes/{node_id}/captures", response_model=CaptureListResponse)
    async def list_captures_by_node(node_id: str, limit: int = 100) -> CaptureListResponse:
        """
        Get recent captures from a specific node.
        
        Parameters:
            node_id: Node ID (e.g., "node-1")
            limit: Max captures to return (default: 100)
        """
        captures = capture_service.repository.get_captures_by_node(node_id, limit=limit)
        total = len(captures)
        
        capture_responses = [
            CaptureDetailResponse(
                id=c.id,
                uuid=c.uuid,
                node_id=c.node_id,
                camera_id=c.camera_id,
                filename=c.uuid + ".png",
                timestamp=c.timestamp,
                date_folder=c.date_folder,
                period=c.period,
                file_path=c.file_path,
                size_bytes=c.size_bytes,
                created_at=c.created_at,
            )
            for c in captures
        ]
        
        return CaptureListResponse(total=total, captures=capture_responses)
    
    @router.delete("/captures/{uuid}", response_model=CaptureDeleteResponse)
    async def delete_capture(uuid: str) -> CaptureDeleteResponse:
        """
        Delete a capture by UUID.
        
        Parameters:
            uuid: Capture UUID
        """
        success = capture_service.repository.delete_capture(uuid)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Capture {uuid} not found")
        
        return CaptureDeleteResponse(
            success=True,
            message=f"Capture {uuid} deleted successfully",
            uuid=uuid,
        )
    
    return router
    """
    Initialize routes with service dependency.
    
    Args:
        capture_service: CaptureService instance
        
    Returns:
        Configured router
    """
    
    @router.post("/captures", response_model=CaptureUploadResponse)
    async def upload_capture(
        file: UploadFile,
        node_id: str = Form(...),
        camera_id: str = Form(...),
        timestamp: str = Form(...),
        exposure: float = Form(0.0),
        gain: float = Form(0.0),
    ) -> CaptureUploadResponse:
        """
        Upload a capture from a node.
        
        Parameters:
            file: Image file
            node_id: Source node ID
            camera_id: Source camera ID
            timestamp: ISO format timestamp
            exposure: Exposure value
            gain: Gain value
        """
        # Read file
        content = await file.read()
        
        # Parse timestamp
        capture_timestamp = datetime.fromisoformat(timestamp)
        
        # Store and return
        response = capture_service.store_capture(
            image_bytes=content,
            node_id=node_id,
            camera_id=camera_id,
            timestamp=capture_timestamp,
            exposure=exposure,
            gain=gain,
        )
        return response
    
    return router
