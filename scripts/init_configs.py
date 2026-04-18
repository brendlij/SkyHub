"""Initialize default configurations."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.database import SessionLocal, engine, Base
from server.services.config_service import ConfigService, CameraConfigService
from server.core.config_schema import SYSTEM_CONFIG_SCHEMA, CAMERA_CONFIG_SCHEMA


def init_default_configs():
    """Initialize default system and camera configurations."""
    
    # Create all tables first
    print("🗄️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ Tables ready\n")
    
    db = SessionLocal()
    config_service = ConfigService(db)
    camera_config_service = CameraConfigService(db)
    
    # System configs - from schema
    print("📋 Setting system configs...")
    for key, config_def in SYSTEM_CONFIG_SCHEMA.items():
        existing = config_service.get(key, scope="system")
        if existing is None:
            config_service.set(
                key=key,
                value=config_def["default"],
                scope="system",
                description=config_def["description"]
            )
            print(f"  ✓ {key} = {config_def['default']}")
        else:
            print(f"  • {key} (already set)")
    
    # Default camera configs for mock camera
    print("\n📷 Setting camera configs...")
    default_camera_config = {
        key: config_def["default"] 
        for key, config_def in CAMERA_CONFIG_SCHEMA.items()
    }
    
    camera_config_service.set_camera_config(
        node_id="node-1",
        camera_id="camera-1",
        config_data=default_camera_config,
    )
    print(f"  ✓ node-1/camera-1 configured")
    
    db.close()
    print("\n✅ Default configurations initialized!")


if __name__ == "__main__":
    init_default_configs()
