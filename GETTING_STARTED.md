# SkyHub: Getting Started Guide

## What is SkyHub?

A **modular, extensible Python system** for:
- **Node**: Capture images from cameras and upload them
- **Server**: Receive captures, store files, and manage metadata

Designed to support **multiple nodes** and **multiple cameras per node** in the future, while staying simple today.

---

## Installation

```bash
cd SkyHub
pip install -r requirements.txt
```

---

## Quick Start (Local Testing)

### Terminal 1: Start the Server

```bash
uvicorn server.main:app --reload
```

Server will run on `http://localhost:8000`

Check it's alive:
```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### Terminal 2: Start the Node

```bash
python -m node.run
```

The node will:
1. Connect to the mock camera
2. Capture a fake image every 10 seconds
3. Upload to the server
4. Log success or errors

You should see output like:
```
INFO:node.capture.capture_service:Capturing from camera-1...
INFO:node.capture.capture_service:Captured 0.25MB
INFO:node.capture.capture_service:Uploading to server...
INFO:node.capture.capture_service:Upload successful: {...}
```

### Check the Server

In a third terminal:
```bash
ls -la storage/captures/
```

You should see files like:
```
node-1_camera-1_a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p.raw
node-1_camera-1_b2c3d4e5-f6g7-4h8i-9j0k-1l2m3n4o5p6q.raw
```

---

## Configuration

### Server Configuration (.env.server)

```bash
# Optional: create .env.server in SkyHub root
SKYHUB_SERVER_STORAGE_ROOT=./storage
SKYHUB_SERVER_DEBUG=true
```

### Node Configuration (.env.node)

```bash
# Optional: create .env.node in SkyHub root
SKYHUB_NODE_NODE_ID=node-1
SKYHUB_NODE_CAMERA_ID=camera-1
SKYHUB_NODE_SERVER_URL=http://localhost:8000
SKYHUB_NODE_CAPTURE_INTERVAL=10.0
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Node                                                        │
├─────────────────────────────────────────────────────────────┤
│ MockCamera.capture_image() → CaptureResult                  │
│            ↓                                                 │
│ ServerClient.upload_capture() → HTTP POST /api/captures    │
└─────────────────────────────────────────────────────────────┘
                        ↓
                    (network)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Server (FastAPI)                                            │
├─────────────────────────────────────────────────────────────┤
│ POST /api/captures → CaptureService.store_capture()         │
│                       ↓                                     │
│                StorageService.save_capture()                │
│                ├─ saves file to ./storage/captures/         │
│                └─ generates unique filename                 │
│                       ↓                                     │
│                CaptureRepository.save_metadata()            │
│                └─ stores metadata (in-memory for now)       │
│                       ↓                                     │
│                Returns CaptureUploadResponse                │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

**Key Files:**

- `node/run.py` - **Node entry point**. Start here to understand the flow.
- `node/cameras/base.py` - **Camera interface**. Add new cameras here.
- `node/cameras/mock_camera.py` - **Mock implementation**. Replace to use real camera.
- `node/network/server_client.py` - **HTTP client**. How node uploads.

- `server/main.py` - **Server entry point**. FastAPI app setup.
- `server/api/routes.py` - **API routes**. Thin layer handling requests.
- `server/services/capture_service.py` - **Business logic**. Orchestrates storage.
- `server/services/storage_service.py` - **File I/O**. Where captures are saved.

---

## Use Cases

### Current (Works Now)

- [x] Mock camera generates fake images
- [x] Node captures and uploads to server
- [x] Server saves files to disk
- [x] Metadata stored in memory

### Next Steps (Easy to Add)

- [ ] Real camera drivers (ZWO, Raspberry Pi, GigE)
- [ ] Multiple cameras per node
- [ ] SQLite database for metadata
- [ ] Image processing pipeline
- [ ] Server → Node commands
- [ ] Web UI dashboard

---

## Extending: Add a Real Camera Driver

### Step 1: Create camera class

Create `node/cameras/zwo_camera.py`:

```python
from node.cameras.base import Camera
from node.capture.models import CaptureResult
from datetime import datetime

class ZWOCamera(Camera):
    """ZWO astronomy camera driver."""
    
    def connect(self) -> None:
        # Connect to ZWO camera via SDK
        pass
    
    def disconnect(self) -> None:
        # Disconnect
        pass
    
    def capture_image(self) -> CaptureResult:
        # Use ZWO SDK to capture
        image_bytes = ...  # Get from camera
        return CaptureResult(
            node_id=self.node_id,
            camera_id=self.camera_id,
            timestamp=datetime.utcnow(),
            image_bytes=image_bytes,
            exposure=...,
            gain=...,
        )
    
    def get_info(self) -> dict:
        return {"type": "ZWOCamera", ...}
```

### Step 2: Use it in node/run.py

```python
# In node/run.py, replace:
# camera = MockCamera(...)

from node.cameras.zwo_camera import ZWOCamera
camera = ZWOCamera(...)
```

That's it! No other changes needed.

---

## Testing

### Manual Test: One Capture Cycle

```python
from node.cameras.mock_camera import MockCamera
from node.network.server_client import ServerClient
from node.capture.capture_service import CaptureService
from node.core.config import node_settings

# Create components
camera = MockCamera(node_settings.camera_id, node_settings.node_id)
camera.connect()

client = ServerClient(node_settings.server_url)
service = CaptureService(camera, client)

# One capture
service.capture_and_upload()

camera.disconnect()
```

---

## Troubleshooting

### Node can't connect to server

```bash
# Check server is running
curl http://localhost:8000/health

# Check node config
cat .env.node
# Make sure SKYHUB_NODE_SERVER_URL=http://localhost:8000
```

### No files in storage/captures/

```bash
# Check server is saving files
ls -la storage/captures/

# Check server logs for errors
# (Terminal 1 where you ran uvicorn)
```

### Module import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Make sure you're in the SkyHub root directory
pwd
# Should be: /path/to/SkyHub
```

---

## Next: Add Database

Replace in-memory storage with SQLite:

1. Create `server/db.py` with SQLAlchemy models
2. Update `CaptureRepository` to use SQLite
3. Add migration scripts for schema changes
4. Add GET endpoints to query captures

See `ARCHITECTURE.md` for more details.

---

## References

- `ARCHITECTURE_SUMMARY.md` - Quick reference
- `ARCHITECTURE.md` - Detailed design + example code
- `STRUCTURE.txt` - Complete file listing and responsibilities

---

Happy capturing! 📸
