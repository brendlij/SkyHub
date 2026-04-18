# SkyHub Architecture Summary

## Project Structure

```
SkyHub/
├── server/                    # FastAPI backend
│   ├── core/
│   │   └── config.py         # Server configuration
│   ├── api/
│   │   └── routes.py         # API endpoints (thin layer)
│   ├── services/
│   │   ├── storage_service.py    # File storage
│   │   └── capture_service.py    # Orchestration
│   ├── models/
│   │   └── capture.py        # Request/response schemas
│   ├── repositories/
│   │   └── capture_repository.py # Metadata (DB placeholder)
│   └── main.py               # FastAPI app entry
│
├── node/                      # Camera capture client
│   ├── core/
│   │   └── config.py         # Node configuration
│   ├── cameras/
│   │   ├── base.py           # Camera interface
│   │   └── mock_camera.py    # Mock implementation
│   ├── capture/
│   │   ├── models.py         # CaptureResult dataclass
│   │   └── capture_service.py    # Capture loop
│   ├── network/
│   │   └── server_client.py  # HTTP client
│   └── run.py                # Node entry point
│
├── app/                       # Legacy (can refactor)
│   └── main.py
│
├── ARCHITECTURE.md           # This design document
├── requirements.txt          # Dependencies
└── README.md
```

## Key Abstractions

### Camera Interface
```python
class Camera(ABC):
    connect() → None
    disconnect() → None
    capture_image() → CaptureResult
    get_info() → dict
```

**Implementations:**
- `MockCamera` - Generates fake images (current)
- `ZWOCamera` - ZWO astronomy cameras (stub)
- `RaspberryCameraModule` - RPi camera (future)

### CaptureResult (Node Side)
```python
@dataclass
class CaptureResult:
    node_id: str
    camera_id: str
    timestamp: datetime
    image_bytes: bytes
    exposure: float | None
    gain: float | None
```

### ServerClient (Node Side)
```python
class ServerClient:
    upload_capture(capture: CaptureResult) → dict
```

Sends multipart HTTP POST with file + metadata.

### CaptureService (Node Side)
```python
class CaptureService:
    capture_and_upload() → bool
    capture_loop(interval_seconds: float) → None
```

Orchestrates capture and upload.

### StorageService (Server Side)
```python
class StorageService:
    initialize() → None
    save_capture(image_bytes, node_id, camera_id) → dict
```

Saves files to `./storage/captures/`.

### CaptureService (Server Side)
```python
class CaptureService:
    store_capture(image_bytes, node_id, ...) → CaptureUploadResponse
```

Orchestrates storage + metadata persistence.

### CaptureRepository (Server Side)
```python
class CaptureRepository:
    save_metadata(metadata: dict) → None
    get_by_node(node_id: str) → list
```

**Current:** In-memory storage  
**Future:** SQLite database

## Data Flow (Simple)

```
Node:     camera.capture_image()
            ↓
          CaptureResult
            ↓
          ServerClient.upload_capture()
            ↓
          HTTP POST /api/captures

Server:   FastAPI receives POST
            ↓
          StorageService.save_capture()
            ↓
          CaptureRepository.save_metadata()
            ↓
          CaptureUploadResponse (JSON)
            ↓
Node:     ✓ Success → sleep → repeat
```

## Design Principles

✓ **Thin API routes** - Routes delegate to services  
✓ **Service orchestration** - Services handle business logic  
✓ **Clear abstractions** - Interfaces are easy to extend  
✓ **Minimal for now** - No Redis, plugins, DB yet  
✓ **Ready to grow** - Structure supports multiple nodes, cameras, processing  
✓ **Type hints** - Beginner-friendly with full annotations  
✓ **Pathlib.Path** - All filesystem work uses pathlib  
✓ **Pydantic settings** - Config via settings classes + env vars  

## Extension Points

1. **Real cameras** - Subclass `Camera`, implement interface
2. **Multiple cameras** - Add to node config, spawn per-camera threads
3. **Processing** - Add `ProcessingService`, call after storage
4. **Database** - Replace `CaptureRepository` in-memory with SQLite
5. **Node commands** - Add endpoint for server→node commands
6. **Per-node config** - Extend `NodeSettings`, server can push config

## Running

### Server
```bash
# Terminal 1
uvicorn server.main:app --reload

# Server runs on http://localhost:8000
# POST http://localhost:8000/api/captures accepts captures
```

### Node
```bash
# Terminal 2
python -m node.run

# Captures from mock camera every 10 seconds
# POSTs to http://localhost:8000/api/captures
```

## Configuration

**Server (.env.server):**
```
SKYHUB_SERVER_STORAGE_ROOT=./storage
SKYHUB_SERVER_DEBUG=true
```

**Node (.env.node):**
```
SKYHUB_NODE_SERVER_URL=http://localhost:8000
SKYHUB_NODE_CAPTURE_INTERVAL=10.0
SKYHUB_NODE_NODE_ID=node-1
SKYHUB_NODE_CAMERA_ID=camera-1
```

## Next Steps (Future)

1. Add SQLite database integration to `CaptureRepository`
2. Implement real camera drivers (ZWO, RPi)
3. Add processing pipeline (`ProcessingService`)
4. Add node configuration polling
5. Add command handling (start/stop capture, etc)
6. Add WebSocket support for real-time updates
7. Add web UI for viewing captures
8. Add multi-node dashboard
