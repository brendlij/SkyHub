# SkyHub - All-Sky Camera System

A distributed all-sky camera capture and storage system with node-server architecture. Designed for automated capture of astronomical observations with support for multiple nodes, cameras, and day/night classification.

## Overview

SkyHub consists of two main components:

- **Node**: Capture client that runs on camera hardware (Raspberry Pi, etc.), captures images, and uploads to server
- **Server**: FastAPI backend that receives captures, organizes by date/time, stores metadata in database

Images are automatically organized by:
- Calendar date (YYYY-MM-DD)
- Astronomical period (day/night) based on sunrise/sunset calculations
- Source node and camera identification
- Sequential numbering for easy stacking

## Features

- Distributed node-server architecture
- Automatic day/night classification using astronomical calculations
- SQLite database with support for PostgreSQL/MySQL
- Organized storage with date and period-based folders
- RESTful API for capture retrieval and management
- Mock camera support for testing
- Configurable observer location for accurate sunrise/sunset calculations
- Comprehensive capture metadata tracking

## Requirements

- Python 3.10+
- pip for dependency management

## Installation

### 1. Clone repository and create environment

```bash
git clone <repository-url>
cd SkyHub
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create `.env` file in project root:

```env
SKYHUB_STORAGE_ROOT=./storage
SKYHUB_DATABASE_URL=sqlite:///./storage/db/skyhub.db
SKYHUB_LATITUDE=48.2082
SKYHUB_LONGITUDE=16.3738
SKYHUB_DEBUG=True
```

For external database:
```env
SKYHUB_DATABASE_URL=postgresql://user:password@localhost/skyhub
SKYHUB_DATABASE_URL=mysql://user:password@localhost/skyhub
```

## Project Structure

```
SkyHub/
├── server/                      # Backend server
│   ├── app_main.py             # FastAPI application
│   ├── main.py                 # Entry point (imports app)
│   ├── database.py             # SQLAlchemy setup
│   ├── astronomy.py            # Sunrise/sunset calculations
│   │
│   ├── core/
│   │   └── config.py           # Server settings
│   │
│   ├── models/
│   │   ├── capture.py          # API schemas
│   │   └── database_models.py  # SQLAlchemy ORM models
│   │
│   ├── services/
│   │   ├── storage_service.py  # File storage operations
│   │   └── capture_service.py  # Capture orchestration
│   │
│   ├── repositories/
│   │   └── capture_repository.py # Database access layer
│   │
│   ├── api/
│   │   └── routes.py           # API endpoints
│   │
│   └── requirements.txt
│
├── node/                        # Capture client
│   ├── run.py                  # Entry point
│   │
│   ├── core/
│   │   └── config.py           # Node settings
│   │
│   ├── cameras/
│   │   ├── base.py             # Camera interface
│   │   └── mock_camera.py      # Test camera implementation
│   │
│   ├── capture/
│   │   ├── models.py           # CaptureResult dataclass
│   │   └── capture_service.py  # Capture loop orchestration
│   │
│   └── network/
│       └── server_client.py    # HTTP upload client
│
├── storage/                     # Runtime data (gitignored)
│   ├── captures/               # Organized captures
│   │   └── 2026-04-18/
│   │       ├── day/
│   │       │   └── 2026-04-18_12-39-09_day_001_node-1_camera-1.png
│   │       └── night/
│   │
│   └── db/
│       └── skyhub.db
│
├── requirements.txt            # Python dependencies
├── .gitignore
├── README.md
└── .env                       # Configuration (gitignored)
```

## Running

### Terminal 1: Start Server

```bash
python -m uvicorn server.main:app --reload
```

Server runs on `http://localhost:8000`

### Terminal 2: Start Node

```bash
python -m node.run
```

Node connects to `http://localhost:8000` and begins capture loop.

## API Endpoints

All responses are JSON formatted.

### Upload Capture

```http
POST /api/captures
Content-Type: multipart/form-data

file: <binary image data>
node_id: string
camera_id: string
timestamp: ISO 8601 datetime
exposure: float (optional)
gain: float (optional)
```

Response:
```json
{
  "node_id": "node-1",
  "camera_id": "camera-1",
  "filename": "2026-04-18_12-39-09_day_001_node-1_camera-1.png",
  "path": "storage/captures/2026-04-18/day/2026-04-18_12-39-09_day_001_node-1_camera-1.png",
  "size_bytes": 257,
  "timestamp": "2026-04-18T10:39:09.631541"
}
```

### List All Captures

```http
GET /api/captures?limit=100&skip=0
```

Response:
```json
{
  "total": 42,
  "captures": [
    {
      "id": 1,
      "uuid": "113b3310-2331-4331-abf0-e959708eae74",
      "node_id": "node-1",
      "camera_id": "camera-1",
      "filename": "2026-04-18_12-39-09_day_001_node-1_camera-1.png",
      "timestamp": "2026-04-18T10:39:09.631541",
      "date_folder": "2026-04-18",
      "period": "day",
      "file_path": "storage/captures/2026-04-18/day/...",
      "size_bytes": 257,
      "created_at": "2026-04-18T10:39:12.136124"
    }
  ]
}
```

### List Captures by Date

```http
GET /api/captures/2026-04-18
```

### List Captures by Date and Period

```http
GET /api/captures/2026-04-18/day
GET /api/captures/2026-04-18/night
```

### List Captures by Node

```http
GET /api/nodes/node-1/captures?limit=100
```

### Delete Capture

```http
DELETE /api/captures/{uuid}
```

Response:
```json
{
  "success": true,
  "message": "Capture deleted successfully",
  "uuid": "113b3310-2331-4331-abf0-e959708eae74"
}
```

## Configuration

### Server Settings (.env)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| SKYHUB_STORAGE_ROOT | string | ./storage | Root directory for capture storage |
| SKYHUB_DATABASE_URL | string | sqlite:///./storage/db/skyhub.db | Database connection URL |
| SKYHUB_LATITUDE | float | 48.2082 | Observer latitude (degrees) |
| SKYHUB_LONGITUDE | float | 16.3738 | Observer longitude (degrees) |
| SKYHUB_DEBUG | bool | True | Debug mode |

### Node Settings

Configure in `node/core/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| node_id | node-1 | Node identifier |
| camera_id | camera-1 | Camera identifier |
| server_url | http://localhost:8000 | Server base URL |
| capture_interval | 10.0 | Seconds between captures |

## Database Schema

### Captures Table

```sql
CREATE TABLE captures (
  id INTEGER PRIMARY KEY,
  uuid VARCHAR(36) UNIQUE NOT NULL,
  node_id VARCHAR(50) NOT NULL,
  camera_id VARCHAR(50) NOT NULL,
  timestamp DATETIME NOT NULL,
  date_folder VARCHAR(10) NOT NULL,
  period VARCHAR(5) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  size_bytes INTEGER NOT NULL,
  created_at DATETIME NOT NULL
);
```

Indexes: uuid, node_id, camera_id, timestamp, date_folder, period

## File Organization

Images are stored with automatic classification:

```
storage/captures/
├── 2026-04-18/
│   ├── day/
│   │   ├── 2026-04-18_12-39-09_day_001_node-1_camera-1.png
│   │   ├── 2026-04-18_12-49-09_day_002_node-1_camera-1.png
│   │   └── 2026-04-18_13-59-09_day_003_node-1_camera-1.png
│   └── night/
│       ├── 2026-04-18_22-15-32_night_001_node-1_camera-1.png
│       └── 2026-04-18_23-45-22_night_002_node-1_camera-1.png
└── 2026-04-19/
    ├── day/
    └── night/
```

Day/Night Classification:

- **Day**: Between astronomical sunrise and sunset
- **Night**: Between astronomical sunset and sunrise (stored under the day it begins)

Sunrise/sunset calculated using PyEphem library based on observer location.

## Example Usage

### Query captures from specific date

```bash
curl http://localhost:8000/api/captures/2026-04-18
```

### Query night captures

```bash
curl http://localhost:8000/api/captures/2026-04-18/night
```

### Query specific node

```bash
curl http://localhost:8000/api/nodes/node-1/captures
```

### Upload with curl

```bash
curl -X POST \
  -F "file=@capture.png" \
  -F "node_id=node-1" \
  -F "camera_id=camera-1" \
  -F "timestamp=2026-04-18T12:39:09.631541" \
  -F "exposure=5.0" \
  -F "gain=100.0" \
  http://localhost:8000/api/captures
```

## Troubleshooting

### ModuleNotFoundError

Ensure venv is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Database locked

Ensure only one server instance is running. SQLite does not support concurrent writers.

### Captures not uploading

Check server is running:
```bash
curl http://localhost:8000/health
```

Verify node configuration and check logs for network errors.

## Future Features

- Real camera drivers (ZWO ASI, Raspberry Pi)
- Image processing pipeline
- Web UI for browse/display
- Multi-camera support per node
- Image metadata extraction
- Automated backup and archival

## License

Proprietary

```

## Configuration

Edit `.env` at the root to customize:

```
# Server
SKYHUB_DEBUG=true
SKYHUB_STORAGE_ROOT=./storage

# Node
SKYHUB_NODE_ID=node-1
SKYHUB_NODE_CAMERA_ID=camera-1
SKYHUB_NODE_SERVER_URL=http://localhost:8000
SKYHUB_NODE_CAPTURE_INTERVAL=10.0
```

## Documentation

- **[ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)** - Architecture overview and design patterns
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Detailed getting started guide
- **[STRUCTURE.txt](STRUCTURE.txt)** - Complete file structure and responsibilities
- **[server/README.md](server/README.md)** - Server-specific documentation

## Extending

### Add a Real Camera Driver

Create a new class in `node/cameras/` inheriting from `Camera`:

```python
from node.cameras.base import Camera
from node.capture.models import CaptureResult

class MyCamera(Camera):
    def connect(self):
        # Connect to camera
        pass
    
    def capture_image(self):
        # Capture and return CaptureResult
        pass
    
    def disconnect(self):
        # Disconnect
        pass
    
    def get_info(self):
        # Return camera metadata
        pass
```

Update `node/run.py` to use your camera:

```python
camera = MyCamera(node_settings.camera_id, node_settings.node_id)
```

That's it! No other changes needed.

### Add SQLite Database

Replace the in-memory `CaptureRepository` with SQLite integration in `server/app/repositories/`.

### Multiple Cameras per Node

Create multiple camera instances and spawn a thread for each in `node/run.py`.

## Key Abstractions

| Component | Location | Purpose |
|-----------|----------|---------|
| `Camera` | `node/cameras/base.py` | Abstract interface for cameras |
| `CaptureResult` | `node/capture/models.py` | Capture data model |
| `ServerClient` | `node/network/server_client.py` | HTTP client for uploads |
| `CaptureService` | `server/app/services/capture_service.py` | Orchestration layer |
| `StorageService` | `server/app/services/storage_service.py` | File storage |

## Technologies

- **Backend**: FastAPI + Uvicorn
- **Configuration**: Pydantic Settings
- **HTTP Client**: httpx
- **Storage**: File-based (SQLite ready)

## Next Steps

- [ ] Add real camera drivers (ZWO, Raspberry Pi, GigE)
- [ ] Implement SQLite for metadata
- [ ] Add image processing pipeline
- [ ] Add web UI dashboard
- [ ] Add node configuration polling
- [ ] Add command handling

## License

(Add your license here)
