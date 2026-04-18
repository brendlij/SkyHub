"""SkyHub Server - FastAPI application."""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from server.core.config import server_settings
from server.database import init_db, SessionLocal
from server.services.storage_service import StorageService
from server.services.capture_service import CaptureService
from server.repositories.capture_repository import CaptureRepository
from server.api.routes import init_routes


# Global service instances
storage_service: StorageService | None = None
capture_service: CaptureService | None = None


def initialize_services() -> None:
    """Initialize all services and database."""
    global storage_service, capture_service
    
    # Initialize database
    init_db()
    
    # Create storage service with location for day/night calculation
    storage_service = StorageService(
        storage_root=server_settings.storage_root,
        latitude=server_settings.latitude,
        longitude=server_settings.longitude,
    )
    storage_service.initialize()
    
    # Create repository with DB session
    db_session = SessionLocal()
    repository = CaptureRepository(db_session)
    
    # Create capture service
    capture_service = CaptureService(storage_service, repository)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    initialize_services()
    # Register routes AFTER initialization
    if capture_service is not None:
        app.include_router(init_routes(capture_service))
    yield
    # Shutdown


# Create app with lifespan
app = FastAPI(title=server_settings.app_name, lifespan=lifespan)


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
