"""Node entry point - starts capture loop."""

import logging
from node.core.config import node_settings
from node.cameras.mock_camera import MockCamera
from node.network.server_client import ServerClient
from node.capture.capture_service import CaptureService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Start the capture node."""
    logger.info(f"Starting SkyHub Node: {node_settings.node_id}")
    
    # Create camera (currently mock, can be swapped for real camera later)
    camera = MockCamera(
        camera_id=node_settings.camera_id,
        node_id=node_settings.node_id,
    )
    
    # Create server client
    server_client = ServerClient(node_settings.server_url)
    
    # Create capture service
    capture_service = CaptureService(camera, server_client)
    
    # Run capture loop
    try:
        capture_service.capture_loop(interval_seconds=node_settings.capture_interval)
    except Exception as e:
        logger.error(f"Node error: {e}")
        raise


if __name__ == "__main__":
    main()
