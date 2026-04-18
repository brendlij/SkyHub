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
    
    def upload_capture(self, capture: CaptureResult) -> dict:
        """
        Upload a capture to the server.
        
        Args:
            capture: CaptureResult to upload
            
        Returns:
            Server response as dict
            
        Raises:
            httpx.HTTPError if upload fails
        """
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
                "exposure": capture.exposure or 0,
                "gain": capture.gain or 0,
            }
            
            response = client.post(
                f"{self.server_url}/api/captures",
                files=files,
                data=data,
            )
            response.raise_for_status()
            return response.json()
