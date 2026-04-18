# SkyHub Server

FastAPI-based backend for the SkyHub all-sky camera system.

## Structure

```
server/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Configuration
│   ├── models/       # Pydantic schemas
│   ├── repositories/ # Data access
│   ├── services/     # Business logic
│   └── main.py       # FastAPI app
├── .env              # Configuration
├── requirements.txt  # Dependencies
├── README.md         # This file
└── main.py           # Entry point for uvicorn
```

## Running

From the **root SkyHub directory**:

```bash
pip install -r server/requirements.txt
uvicorn server.main:app --reload
```

Server runs on `http://localhost:8000`

## API

- **POST /api/captures** - Upload capture from node
- **GET /health** - Health check
- **GET /** - Root endpoint

## Configuration

Settings are loaded from `.env` in the root directory:

```
SKYHUB_DEBUG=true
SKYHUB_STORAGE_ROOT=./storage
```

All captures are saved to `./storage/captures/`

