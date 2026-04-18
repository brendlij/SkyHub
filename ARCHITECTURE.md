"""Complete end-to-end example of the SkyHub system."""

"""
ARCHITECTURE OVERVIEW

┌─────────────────────────────────────────────────────────────────┐
│                         SkyHub System                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐           ┌──────────────────────┐   │
│  │   SkyHub Node        │           │  SkyHub Server       │   │
│  │                      │           │                      │   │
│  │  ┌────────────────┐  │           │  ┌────────────────┐  │   │
│  │  │  MockCamera    │  │           │  │   FastAPI      │  │   │
│  │  │   (or ZWO,     │  │           │  │                │  │   │
│  │  │    RPi, etc)   │  │           │  │  Routes:       │  │   │
│  │  └────────────────┘  │           │  │  - POST        │  │   │
│  │         ↓            │           │  │    /captures   │  │   │
│  │  ┌────────────────┐  │           │  │  - GET /health │  │   │
│  │  │ CaptureService │  │──POST────→│  │  - GET /       │  │   │
│  │  │  (orchestrate) │  │ /api/     │  └────────────────┘  │   │
│  │  └────────────────┘  │ captures  │         ↓            │   │
│  │         ↓            │  (files   │  ┌────────────────┐  │   │
│  │  ┌────────────────┐  │   + meta) │  │ CaptureService │  │   │
│  │  │ ServerClient   │  │           │  │  (orchestrate) │  │   │
│  │  │  (HTTP client) │  │           │  └────────────────┘  │   │
│  │  └────────────────┘  │           │         ↓            │   │
│  │                      │           │  ┌────────────────┐  │   │
│  └──────────────────────┘           │  │ StorageService │  │   │
│                                     │  │  (save files)  │  │   │
│                                     │  └────────────────┘  │   │
│                                     │         ↓            │   │
│                                     │  ┌────────────────┐  │   │
│                                     │  │ Capture        │  │   │
│                                     │  │ Repository     │  │   │
│                                     │  │ (metadata DB)  │  │   │
│                                     │  └────────────────┘  │   │
│                                     │         ↓            │   │
│                                     │   ./storage/        │   │
│                                     │   ├─ captures/      │   │
│                                     │   ├─ derived/       │   │
│                                     │   └─ db/            │   │
│                                     │                      │   │
│                                     └──────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


MINIMAL FLOW (One Capture Cycle):

1. Node starts → MockCamera.connect()
2. MockCamera.capture_image() → creates fake image bytes
3. CaptureResult(node_id, camera_id, timestamp, image_bytes, exposure, gain)
4. ServerClient.upload_capture(capture) → HTTP multipart POST
5. Server receives at POST /api/captures
6. StorageService.save_capture() → writes file to ./storage/captures/
7. CaptureRepository.save_metadata() → stores metadata
8. Returns CaptureUploadResponse with filename, path, size
9. Node logs success → sleeps interval_seconds → loop repeats


DATA FLOW:

Node Side:
  MockCamera.capture_image()
         ↓
  CaptureResult (dataclass)
  - node_id: "node-1"
  - camera_id: "camera-1"
  - timestamp: datetime.utcnow()
  - image_bytes: bytes
  - exposure: 10.0
  - gain: 50
         ↓
  ServerClient.upload_capture(capture)
  - Creates multipart POST with file + metadata
  - Sends to server_url/api/captures
         ↓
  HTTP Request: POST http://localhost:8000/api/captures
  - file: raw image bytes
  - node_id: "node-1"
  - camera_id: "camera-1"
  - timestamp: "2026-04-18T12:34:56.123456"
  - exposure: 10.0
  - gain: 50.0

Server Side:
  @app.post("/captures")
  async def upload_capture(file, node_id, camera_id, timestamp, exposure, gain)
         ↓
  CaptureService.store_capture()
  - StorageService.save_capture()
    - filename: "node-1_camera-1_<uuid>.raw"
    - path: "./storage/captures/node-1_camera-1_<uuid>.raw"
    - size_bytes: length of image_bytes
  - CaptureRepository.save_metadata()
    - {"node_id": "node-1", "camera_id": "camera-1", ...}
         ↓
  CaptureUploadResponse
  {
    "node_id": "node-1",
    "camera_id": "camera-1",
    "filename": "node-1_camera-1_<uuid>.raw",
    "path": "./storage/captures/node-1_camera-1_<uuid>.raw",
    "size_bytes": 262144,
    "timestamp": "2026-04-18T12:34:56.123456"
  }


EXTENSION POINTS:

1. Real Camera Drivers:
   - Create new class inheriting from Camera
   - Implement connect(), disconnect(), capture_image(), get_info()
   - Examples: ZWOCamera, RaspberryCameraModule, GigECamera

2. Multiple Cameras:
   - Create list of cameras in node/run.py
   - Spawn thread per camera running CaptureService
   - Each with own camera_id in config

3. Processing:
   - Add ProcessingService in server/services/
   - Call after StorageService.save_capture()
   - Example: dark frame subtraction, stacking

4. Database:
   - Replace CaptureRepository in-memory list with SQLite
   - add_column migration scripts
   - Query endpoints: GET /captures?node_id=X

5. Node Configuration:
   - Extend NodeSettings with camera-specific params
   - Per-camera config file or API endpoint
   - Server can push config to nodes

6. Commands:
   - Add endpoint: POST /nodes/<node_id>/commands
   - Node polls or WebSocket subscription
   - Examples: start/stop capture, change settings
"""


def example_usage():
    """Example showing how to use the system."""
    
    # ============ SERVER SIDE ============
    print("=== SERVER ===")
    from server.core.config import server_settings
    from server.services.storage_service import StorageService
    from server.repositories.capture_repository import CaptureRepository
    from server.services.capture_service import CaptureService
    
    # Initialize services
    storage = StorageService(server_settings.storage_root)
    storage.initialize()
    repo = CaptureRepository()
    capture_svc = CaptureService(storage, repo)
    print("✓ Server services initialized")
    
    # ============ NODE SIDE ============
    print("\n=== NODE ===")
    from node.core.config import node_settings
    from node.cameras.mock_camera import MockCamera
    from node.network.server_client import ServerClient
    from node.capture.capture_service import CaptureService as NodeCaptureService
    
    # Create mock camera
    camera = MockCamera(node_settings.camera_id, node_settings.node_id)
    camera.connect()
    print(f"✓ Camera connected: {camera.get_info()}")
    
    # Create server client
    client = ServerClient(node_settings.server_url)
    print(f"✓ Server client configured: {node_settings.server_url}")
    
    # Create capture service
    node_capture_svc = NodeCaptureService(camera, client)
    print("✓ Node capture service ready")
    
    # ============ SIMULATE ONE CAPTURE CYCLE ============
    print("\n=== CAPTURE CYCLE (SIMULATED) ===")
    
    # 1. Node captures
    print("1. Node: Capturing image...")
    capture = camera.capture_image()
    print(f"   ✓ Captured {capture.size_mb():.2f}MB")
    print(f"   - timestamp: {capture.timestamp}")
    print(f"   - node_id: {capture.node_id}")
    print(f"   - camera_id: {capture.camera_id}")
    print(f"   - exposure: {capture.exposure}")
    print(f"   - gain: {capture.gain}")
    
    # 2. Server receives (simulated - normally via HTTP)
    print("\n2. Server: Storing capture...")
    response = capture_svc.store_capture(
        image_bytes=capture.image_bytes,
        node_id=capture.node_id,
        camera_id=capture.camera_id,
        timestamp=capture.timestamp,
        exposure=capture.exposure,
        gain=capture.gain,
    )
    print(f"   ✓ Stored")
    print(f"   - filename: {response.filename}")
    print(f"   - path: {response.path}")
    print(f"   - size: {response.size_bytes} bytes")
    
    # 3. Verify metadata was stored
    print("\n3. Server: Checking metadata...")
    metadata = repo.get_by_node(node_settings.node_id)
    print(f"   ✓ Found {len(metadata)} captures for {node_settings.node_id}")
    
    print("\n=== CYCLE COMPLETE ===")
    camera.disconnect()


if __name__ == "__main__":
    example_usage()
