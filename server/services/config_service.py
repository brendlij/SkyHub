"""Configuration management service."""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from server.models.config_models import ConfigOverride, CameraConfig
from server.core.config_schema import (
    SYSTEM_CONFIG_SCHEMA,
    CAMERA_CONFIG_SCHEMA,
    NODE_CONFIG_SCHEMA,
    validate_config_value,
)


class ConfigService:
    """Manages runtime configuration with database persistence."""
    
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}  # In-memory cache
    
    def get(self, key: str, scope: str = "system", default=None):
        """
        Get configuration value.
        
        Args:
            key: Config key
            scope: "system", "node:{id}", "camera:{id}"
            default: Default value if not found
            
        Returns:
            Config value or default
        """
        cache_key = f"{scope}:{key}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        config = self.db.query(ConfigOverride).filter(
            ConfigOverride.key == key,
            ConfigOverride.scope == scope,
        ).first()
        
        if config:
            # Parse JSON value
            try:
                value = json.loads(config.value)
            except:
                value = config.value
            
            # Cache it
            self._cache[cache_key] = value
            return value
        
        return default
    
    def set(self, key: str, value, scope: str = "system", description: str = None):
        """
        Set configuration value (persisted to DB).
        
        Args:
            key: Config key
            value: Config value (will be JSON serialized)
            scope: "system", "node:{id}", "camera:{id}"
            description: Optional description
            
        Raises:
            ValueError: If config is invalid
        """
        # Determine schema based on scope
        if scope == "system":
            schema = SYSTEM_CONFIG_SCHEMA
        elif scope.startswith("node:"):
            schema = NODE_CONFIG_SCHEMA
        elif scope.startswith("camera:"):
            schema = CAMERA_CONFIG_SCHEMA
        else:
            raise ValueError(f"Invalid scope: {scope}")
        
        # Validate against schema
        is_valid, error = validate_config_value(key, value, schema)
        if not is_valid:
            raise ValueError(f"Invalid config value: {error}")
        
        # Serialize value
        json_value = json.dumps(value)
        
        # Insert or update
        config = self.db.query(ConfigOverride).filter(
            ConfigOverride.key == key,
            ConfigOverride.scope == scope,
        ).first()
        
        if config:
            config.value = json_value
            config.description = description
            config.set_at = datetime.utcnow()
        else:
            config = ConfigOverride(
                key=key,
                scope=scope,
                value=json_value,
                description=description,
            )
            self.db.add(config)
        
        self.db.commit()
        
        # Update cache
        cache_key = f"{scope}:{key}"
        self._cache[cache_key] = value
        
        # Emit CONFIG_CHANGED event
        try:
            from server.events.event_system import event_system, Event, EventType
            event_system.emit(Event(
                type=EventType.CONFIG_CHANGED,
                timestamp=datetime.utcnow(),
                scope=scope,
                data={"key": key, "value": value, "description": description}
            ))
        except ImportError:
            pass  # Event system not available
    
    def get_all(self, scope: str = "system") -> dict:
        """Get all configs for a scope."""
        configs = self.db.query(ConfigOverride).filter(
            ConfigOverride.scope == scope
        ).all()
        
        result = {}
        for config in configs:
            try:
                result[config.key] = json.loads(config.value)
            except:
                result[config.key] = config.value
        
        return result
    
    def delete(self, key: str, scope: str = "system"):
        """Delete configuration."""
        self.db.query(ConfigOverride).filter(
            ConfigOverride.key == key,
            ConfigOverride.scope == scope,
        ).delete()
        self.db.commit()
        
        # Clear cache
        cache_key = f"{scope}:{key}"
        if cache_key in self._cache:
            del self._cache[cache_key]
    
    def clear_cache(self):
        """Clear in-memory cache."""
        self._cache.clear()


class CameraConfigService:
    """Manages camera-specific configuration."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_camera_config(self, node_id: str, camera_id: str) -> dict:
        """Get configuration for a specific camera."""
        config_id = f"{node_id}:{camera_id}"
        
        config = self.db.query(CameraConfig).filter(
            CameraConfig.id == config_id
        ).first()
        
        if config:
            return {
                "node_id": config.node_id,
                "camera_id": config.camera_id,
                "exposure": float(config.exposure),
                "gain": float(config.gain),
                "resolution": config.resolution,
                "frame_rate": int(config.frame_rate),
                "enabled": config.enabled == "true",
                "capture_interval": float(config.capture_interval),
                "white_balance": getattr(config, "white_balance", "auto"),
                "iso": int(getattr(config, "iso", 400)),
            }
        
        # Return defaults from schema
        defaults = {key: conf["default"] for key, conf in CAMERA_CONFIG_SCHEMA.items()}
        defaults["node_id"] = node_id
        defaults["camera_id"] = camera_id
        return defaults
    
    def set_camera_config(self, node_id: str, camera_id: str, config_data: dict):
        """Update camera configuration with validation."""
        # Validate each field against schema
        for key, value in config_data.items():
            if key not in ["node_id", "camera_id"]:
                is_valid, error = validate_config_value(key, value, CAMERA_CONFIG_SCHEMA)
                if not is_valid:
                    raise ValueError(f"Invalid camera config: {error}")
        
        config_id = f"{node_id}:{camera_id}"
        
        config = self.db.query(CameraConfig).filter(
            CameraConfig.id == config_id
        ).first()
        
        if config:
            # Update existing
            config.exposure = str(config_data.get("exposure", config.exposure))
            config.gain = str(config_data.get("gain", config.gain))
            config.resolution = config_data.get("resolution", config.resolution)
            config.frame_rate = str(config_data.get("frame_rate", config.frame_rate))
            config.enabled = "true" if config_data.get("enabled", True) else "false"
            config.capture_interval = str(config_data.get("capture_interval", config.capture_interval))
            config.updated_at = datetime.utcnow()
        else:
            # Create new with defaults
            camera_defaults = {k: v["default"] for k, v in CAMERA_CONFIG_SCHEMA.items()}
            camera_defaults.update(config_data)
            
            config = CameraConfig(
                id=config_id,
                node_id=node_id,
                camera_id=camera_id,
                exposure=str(camera_defaults.get("exposure")),
                gain=str(camera_defaults.get("gain")),
                resolution=camera_defaults.get("resolution"),
                frame_rate=str(camera_defaults.get("frame_rate")),
                enabled="true" if camera_defaults.get("enabled") else "false",
                capture_interval=str(camera_defaults.get("capture_interval")),
            )
            self.db.add(config)
        
        self.db.commit()
        result = self.get_camera_config(node_id, camera_id)
        
        # Emit CONFIG_CHANGED event for camera
        try:
            from server.events.event_system import event_system, Event, EventType
            event_system.emit(Event(
                type=EventType.CONFIG_CHANGED,
                timestamp=datetime.utcnow(),
                scope=f"camera:{node_id}:{camera_id}",
                data=result
            ))
        except ImportError:
            pass  # Event system not available
        
        return result
    
    def get_all_camera_configs(self) -> list:
        """Get all camera configurations."""
        configs = self.db.query(CameraConfig).all()
        return [self.get_camera_config(c.node_id, c.camera_id) for c in configs]
