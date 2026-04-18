"""Node entry point - starts capture loop."""

import logging
from node.core.config import node_settings
from node.cameras.mock_camera import MockCamera
from node.network.server_client import ServerClient
from node.network.event_client import EventClient
from node.capture.capture_service import CaptureService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Start the capture node."""
    logger.info(f"Starting SkyHub Node: {node_settings.node_id}")
    
    # Create server client
    server_client = ServerClient(node_settings.server_url)
    
    # Create event client for real-time config updates
    event_client = EventClient(
        node_settings.server_url,
        node_settings.node_id,
        node_settings.camera_id,
    )
    
    # Fetch camera config from server
    logger.info(f"Fetching camera config from server...")
    camera_config = server_client.get_camera_config(
        node_settings.node_id,
        node_settings.camera_id,
    )
    logger.info(f"Camera config: exposure={camera_config.get('exposure')}s, gain={camera_config.get('gain')}%, interval={camera_config.get('capture_interval')}s")
    
    # Create camera with config
    camera = MockCamera(
        camera_id=node_settings.camera_id,
        node_id=node_settings.node_id,
        exposure=camera_config.get('exposure', 5.0),
        gain=camera_config.get('gain', 100.0),
    )
    
    # Create capture service with event client
    capture_service = CaptureService(camera, server_client, event_client)
    
    # Run capture loop with event-based config updates
    try:
        capture_service.capture_loop(
            interval_seconds=camera_config.get('capture_interval', node_settings.capture_interval),
            camera_config=camera_config,
            config_refresh_interval=10,  # Check for config change events every 10 seconds
        )
    except Exception as e:
        logger.error(f"Node error: {e}")
        raise


if __name__ == "__main__":
    main()
