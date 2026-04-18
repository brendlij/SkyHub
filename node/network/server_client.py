"""Client for uploading captures to the server."""

import httpx
from pathlib import Path
from node.capture.models import CaptureResult


class ServerClient:
    """Uploads captures to the remote SkyHub server."""
    
    def __init__(self, server_url: str):
        """
        Args:
            server_url: Base URL of the server (e.g., http://localhost:8000)
        """
        self.server_url = server_url.rstrip("/")
    
    def upload_capture(self, capture, camera_config: dict = None) -> dict:
        """
        Upload a capture to the server.
        
        Args:
            capture: CaptureResult to upload
            camera_config: Optional camera configuration dict with metadata
            
        Returns:
            Server response as dict
            
        Raises:
            httpx.HTTPError if upload fails
        """
        if camera_config is None:
            camera_config = {}
            
        with httpx.Client() as client:
            files = {
                "file": (
                    f"{capture.timestamp.isoformat()}.raw",
                    capture.image_bytes,
                    "application/octet-stream"
                )
            }
            data = {
                "node_id": capture.node_id,
                "camera_id": capture.camera_id,
                "timestamp": capture.timestamp.isoformat(),
                "exposure": camera_config.get("exposure", capture.exposure or 0),
                "gain": camera_config.get("gain", capture.gain or 0),
                "resolution": camera_config.get("resolution"),
                "frame_rate": camera_config.get("frame_rate"),
                "white_balance": camera_config.get("white_balance"),
                "iso": camera_config.get("iso"),
            }
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            response = client.post(
                f"{self.server_url}/api/captures",
                files=files,
                data=data,
            )
            response.raise_for_status()
            return response.json()
    
    def get_camera_config(self, node_id: str, camera_id: str) -> dict:
        """
        Fetch camera configuration from server.
        
        Args:
            node_id: Node identifier
            camera_id: Camera identifier
            
        Returns:
            Camera config dict or defaults if not available
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.server_url}/api/config/camera/{node_id}/{camera_id}",
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            # Return defaults if can't fetch from server
            print(f"Could not fetch config from server: {e}, using defaults")
            return {
                "node_id": node_id,
                "camera_id": camera_id,
                "exposure": 5.0,
                "gain": 100.0,
                "resolution": "1920x1080",
                "frame_rate": 30,
                "enabled": True,
                "capture_interval": 10.0,
            }
