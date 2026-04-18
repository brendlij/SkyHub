"""FastAPI routes for the server."""

from fastapi import APIRouter, UploadFile, Form, HTTPException
from datetime import datetime
from server.services.capture_service import CaptureService
from server.models.capture import (
    CaptureUploadResponse, 
    CaptureDetailResponse,
    CaptureListResponse,
    CaptureDeleteResponse,
    OverallStats,
    StatsByDate,
    StatsByPeriod,
    StatsByNode,
    HealthResponse,
    StorageHealth,
    DatabaseHealth,
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
        exposure: float = Form(None),
        gain: float = Form(None),
        resolution: str = Form(None),
        frame_rate: int = Form(None),
        white_balance: str = Form(None),
        iso: int = Form(None),
    ) -> CaptureUploadResponse:
        """
        Upload a capture from a node.
        
        Parameters:
            file: Image file
            node_id: Source node ID
            camera_id: Source camera ID
            timestamp: ISO format timestamp
            exposure: Exposure time (seconds)
            gain: Gain (%)
            resolution: Resolution (e.g., "1920x1080")
            frame_rate: Frames per second
            white_balance: White balance mode
            iso: ISO sensitivity
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
            resolution=resolution,
            frame_rate=frame_rate,
            white_balance=white_balance,
            iso=iso,
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
                exposure=c.exposure,
                gain=c.gain,
                resolution=c.resolution,
                frame_rate=c.frame_rate,
                white_balance=c.white_balance,
                iso=c.iso,
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
                exposure=c.exposure,
                gain=c.gain,
                resolution=c.resolution,
                frame_rate=c.frame_rate,
                white_balance=c.white_balance,
                iso=c.iso,
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
                exposure=c.exposure,
                gain=c.gain,
                resolution=c.resolution,
                frame_rate=c.frame_rate,
                white_balance=c.white_balance,
                iso=c.iso,
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
                exposure=c.exposure,
                gain=c.gain,
                resolution=c.resolution,
                frame_rate=c.frame_rate,
                white_balance=c.white_balance,
                iso=c.iso,
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
    
    @router.get("/stats")
    async def get_statistics():
        """
        Get overall system statistics.
        
        Returns captures count, size, breakdown by date and node.
        """
        from pathlib import Path
        
        # Get repository stats
        total_size = capture_service.repository.get_total_size_bytes()
        period_counts = capture_service.repository.get_period_counts()
        stats_by_date = capture_service.repository.get_stats_by_date()
        stats_by_node = capture_service.repository.get_stats_by_node()
        unique_nodes = capture_service.repository.get_unique_nodes()
        unique_cameras = capture_service.repository.get_unique_cameras()
        
        # Build date stats
        date_stats = []
        for date_folder in sorted(stats_by_date.keys(), reverse=True):
            periods = stats_by_date[date_folder]
            period_list = [
                StatsByPeriod(
                    period=period,
                    count=periods[period]['count'],
                    total_size_bytes=periods[period]['total_size_bytes'],
                )
                for period in ['day', 'night']
            ]
            date_total = sum(p.count for p in period_list)
            date_size = sum(p.total_size_bytes for p in period_list)
            
            date_stats.append(StatsByDate(
                date_folder=date_folder,
                count=date_total,
                total_size_bytes=date_size,
                by_period=period_list,
            ))
        
        # Build node stats
        node_stats = []
        for node_id in sorted(stats_by_node.keys()):
            cameras = list(stats_by_node[node_id]['cameras'].keys())
            node_stats.append(StatsByNode(
                node_id=node_id,
                count=stats_by_node[node_id]['count'],
                total_size_bytes=stats_by_node[node_id]['total_size'],
                cameras=cameras,
            ))
        
        total_captures = capture_service.repository.count_captures()
        
        return OverallStats(
            total_captures=total_captures,
            total_size_bytes=total_size,
            total_size_gb=round(total_size / (1024**3), 2),
            date_count=len(stats_by_date),
            node_count=len(unique_nodes),
            camera_count=len(unique_cameras),
            day_captures=period_counts.get('day', 0),
            night_captures=period_counts.get('night', 0),
            by_date=date_stats,
            by_node=node_stats,
        )
    
    @router.get("/health")
    async def health_check():
        """
        Check system health: storage, database, connectivity.
        
        Returns health status of storage and database.
        """
        from pathlib import Path
        import time
        
        # Get start time for uptime
        start_time = time.time()
        
        # Check storage
        storage_root = Path(capture_service.storage.storage_root)
        captures_dir = storage_root / "captures"
        db_file = Path(capture_service.storage.storage_root).parent / "storage" / "db" / "skyhub.db"
        
        # Calculate storage size
        total_size = 0
        capture_count = 0
        if captures_dir.exists():
            for file in captures_dir.rglob('*.png'):
                total_size += file.stat().st_size
                capture_count += 1
        
        storage_health = StorageHealth(
            status="ok" if storage_root.exists() else "error",
            storage_root=str(storage_root),
            total_size_bytes=total_size,
            total_size_gb=round(total_size / (1024**3), 2),
            capture_count=capture_count,
            captures_dir_exists=captures_dir.exists(),
            db_file_exists=db_file.exists(),
        )
        
        # Check database
        db_ok = False
        record_count = 0
        error_msg = None
        
        try:
            # Try to query database
            record_count = capture_service.repository.count_captures()
            db_ok = True
        except Exception as e:
            error_msg = str(e)
            db_ok = False
        
        database_health = DatabaseHealth(
            status="ok" if db_ok else "error",
            database_type="sqlite" if "sqlite" in str(capture_service.repository.db.bind.url) else "external",
            connection_ok=db_ok,
            table_count=1,
            record_count=record_count,
            error=error_msg,
        )
        
        # Determine overall status
        overall_status = "ok"
        if not storage_health.captures_dir_exists or not storage_health.db_file_exists:
            overall_status = "degraded"
        if not db_ok:
            overall_status = "error"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            server_uptime_seconds=start_time,
            storage=storage_health,
            database=database_health,
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
