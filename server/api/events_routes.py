"""Event API routes for real-time updates."""

from fastapi import APIRouter, Query
from datetime import datetime
from pydantic import BaseModel
from server.events.event_system import event_system


router = APIRouter(prefix="/api/events", tags=["events"])


class EventResponse(BaseModel):
    """Event response model."""
    type: str
    timestamp: str
    scope: str
    data: dict


def init_events_routes() -> APIRouter:
    """Initialize event routes."""
    
    @router.get("/camera/{node_id}/{camera_id}")
    async def get_camera_events(
        node_id: str,
        camera_id: str,
        since: str = Query(None, description="ISO format timestamp - only return events after this"),
    ) -> list[EventResponse]:
        """
        Get events for a camera since a given time.
        
        Parameters:
            node_id: Node identifier
            camera_id: Camera identifier
            since: ISO format timestamp (e.g., "2026-04-18T13:57:35")
        """
        scope = f"camera:{node_id}:{camera_id}"
        
        # Parse since timestamp
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                since_dt = datetime.utcnow()
        else:
            since_dt = datetime.utcnow()
        
        # Get events
        events = event_system.get_events_since(scope, since_dt)
        
        return [EventResponse(**e.to_dict()) for e in events]
    
    @router.get("/node/{node_id}")
    async def get_node_events(
        node_id: str,
        since: str = Query(None, description="ISO format timestamp"),
    ) -> list[EventResponse]:
        """
        Get events for a node since a given time.
        
        Parameters:
            node_id: Node identifier
            since: ISO format timestamp
        """
        scope = f"node:{node_id}"
        
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                since_dt = datetime.utcnow()
        else:
            since_dt = datetime.utcnow()
        
        events = event_system.get_events_since(scope, since_dt)
        return [EventResponse(**e.to_dict()) for e in events]
    
    @router.get("/")
    async def get_all_events(
        since: str = Query(None, description="ISO format timestamp"),
    ) -> list[EventResponse]:
        """
        Get all events since a given time.
        
        Parameters:
            since: ISO format timestamp
        """
        scope = "global"
        
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                since_dt = datetime.utcnow()
        else:
            since_dt = datetime.utcnow()
        
        events = event_system.get_events_since(scope, since_dt)
        return [EventResponse(**e.to_dict()) for e in events]
    
    return router
