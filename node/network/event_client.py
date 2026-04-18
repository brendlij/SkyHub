"""Event client for Node to receive real-time updates."""

import httpx
from datetime import datetime
from typing import Optional, Callable


class EventClient:
    """Subscribes to server events for real-time config updates."""
    
    def __init__(self, server_url: str, node_id: str, camera_id: str):
        """
        Args:
            server_url: Base URL of the server
            node_id: Node identifier
            camera_id: Camera identifier
        """
        self.server_url = server_url.rstrip("/")
        self.node_id = node_id
        self.camera_id = camera_id
        self.last_check = datetime.utcnow()
    
    def get_config_changed_events(self, since: Optional[datetime] = None) -> list:
        """
        Get CONFIG_CHANGED events for this camera since a given time.
        
        Args:
            since: Only return events after this timestamp
            
        Returns:
            List of events
        """
        if since is None:
            since = self.last_check
        
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(
                    f"{self.server_url}/api/events/camera/{self.node_id}/{self.camera_id}",
                    params={"since": since.isoformat()}
                )
                response.raise_for_status()
                self.last_check = datetime.utcnow()
                return response.json()
        except Exception as e:
            print(f"Could not fetch events: {e}")
            return []
    
    def has_config_updates(self) -> bool:
        """Check if there are any CONFIG_CHANGED events."""
        events = self.get_config_changed_events()
        return any(e.get("type") == "CONFIG_CHANGED" for e in events)
    
    def get_latest_config_event(self):
        """Get the most recent CONFIG_CHANGED event, if any."""
        events = self.get_config_changed_events()
        config_events = [e for e in events if e.get("type") == "CONFIG_CHANGED"]
        return config_events[-1] if config_events else None
