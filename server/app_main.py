"""SkyHub Server - FastAPI application."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from server.core.config import server_settings
from server.database import init_db, SessionLocal
from server.services.storage_service import StorageService
from server.services.capture_service import CaptureService
from server.services.config_service import ConfigService, CameraConfigService
from server.repositories.capture_repository import CaptureRepository
from server.api.routes import init_routes
from server.api.config_routes import init_config_routes
from server.api.events_routes import init_events_routes


# Global service instances
storage_service: StorageService | None = None
capture_service: CaptureService | None = None
capture_repository: CaptureRepository | None = None
config_service: ConfigService | None = None
camera_config_service: CameraConfigService | None = None


def initialize_services() -> None:
    """Initialize all services and database."""
    global storage_service, capture_service, capture_repository, config_service, camera_config_service
    
    # Initialize database
    init_db()
    
    # Create storage service with location for day/night calculation
    storage_service = StorageService(
        storage_root=server_settings.storage_root,
        latitude=server_settings.latitude,
        longitude=server_settings.longitude,
    )
    storage_service.initialize()
    
    # Create database session
    db_session = SessionLocal()
    
    # Create repository with DB session
    capture_repository = CaptureRepository(db_session)
    
    # Create capture service
    capture_service = CaptureService(storage_service, capture_repository)
    
    # Create config services
    config_service = ConfigService(db_session)
    camera_config_service = CameraConfigService(db_session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    initialize_services()
    
    # Initialize default configs if DB is empty
    system_configs = config_service.get_all(scope="system")
    if not system_configs:
        print("📋 Initializing default configurations...\n")
        from server.core.config_schema import SYSTEM_CONFIG_SCHEMA, CAMERA_CONFIG_SCHEMA
        
        # System configs
        for key, config_def in SYSTEM_CONFIG_SCHEMA.items():
            config_service.set(
                key=key,
                value=config_def["default"],
                scope="system",
                description=config_def["description"]
            )
            print(f"  ✓ {key} = {config_def['default']}")
        
        # Camera configs
        default_camera_config = {
            key: config_def["default"] 
            for key, config_def in CAMERA_CONFIG_SCHEMA.items()
        }
        camera_config_service.set_camera_config(
            node_id="node-1",
            camera_id="camera-1",
            config_data=default_camera_config,
        )
        print(f"  ✓ node-1/camera-1 configured\n")
    
    # Register routes AFTER initialization
    if capture_service is not None:
        app.include_router(init_routes(capture_service))
    if config_service is not None and camera_config_service is not None:
        app.include_router(init_config_routes(config_service, camera_config_service))
    
    # Register event routes
    app.include_router(init_events_routes())
    yield
    # Shutdown


# Create app with lifespan
app = FastAPI(title=server_settings.app_name, lifespan=lifespan)


# Mount static files (Vue build output)
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_dir):
    app.mount('/assets', StaticFiles(directory=os.path.join(static_dir, 'assets')), name='assets')


# Serve Vue app (must be last)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve Vue SPA (fallback to index.html)."""
    # Skip API routes
    if full_path.startswith('api/'):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for all other routes (Vue Router handles them)
    index_path = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=f.read())
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="index.html not found")


# Add routes
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"{server_settings.app_name} is running",
        "debug": server_settings.debug,
        "storage_root": server_settings.storage_root,
    }


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}
