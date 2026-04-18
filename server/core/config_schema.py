"""Configuration schema definition - Single Source of Truth."""

from typing import Any, Dict, Literal

# ============================================================================
# SYSTEM CONFIGURATION SCHEMA
# ============================================================================

SYSTEM_CONFIG_SCHEMA: Dict[str, Dict[str, Any]] = {
    "observer_name": {
        "type": "str",
        "default": "Main Observatory",
        "description": "Observatory identifier",
        "min_length": 1,
        "max_length": 100,
    },
    "storage_policy": {
        "type": "str",
        "default": "keep_all",
        "description": "Storage policy: keep_all | auto_cleanup",
        "allowed_values": ["keep_all", "auto_cleanup"],
    },
    "auto_cleanup_days": {
        "type": "int",
        "default": 90,
        "description": "Auto-cleanup after N days (0 = disabled)",
        "min": 0,
        "max": 3650,
    },
    "max_storage_gb": {
        "type": "int",
        "default": 1000,
        "description": "Maximum storage size in GB (0 = unlimited)",
        "min": 0,
    },
    "image_format": {
        "type": "str",
        "default": "png",
        "description": "Image format: png | jpg | fits",
        "allowed_values": ["png", "jpg", "fits"],
    },
    "compression_level": {
        "type": "int",
        "default": 9,
        "description": "Compression level 0-9",
        "min": 0,
        "max": 9,
    },
}

# ============================================================================
# CAMERA CONFIGURATION SCHEMA
# ============================================================================

CAMERA_CONFIG_SCHEMA: Dict[str, Dict[str, Any]] = {
    "exposure": {
        "type": "float",
        "default": 5.0,
        "description": "Exposure time in seconds",
        "min": 0.001,
        "max": 60.0,
        "unit": "seconds",
    },
    "gain": {
        "type": "float",
        "default": 100.0,
        "description": "Camera gain",
        "min": 0.0,
        "max": 400.0,
        "unit": "%",
    },
    "resolution": {
        "type": "str",
        "default": "1920x1080",
        "description": "Resolution as WIDTHxHEIGHT",
        "allowed_values": ["640x480", "1280x720", "1920x1080", "2560x1440", "3840x2160"],
    },
    "frame_rate": {
        "type": "int",
        "default": 30,
        "description": "Frames per second",
        "min": 1,
        "max": 120,
    },
    "enabled": {
        "type": "bool",
        "default": True,
        "description": "Camera enabled for capture",
    },
    "capture_interval": {
        "type": "float",
        "default": 10.0,
        "description": "Time between captures in seconds",
        "min": 0.5,
        "max": 3600.0,
        "unit": "seconds",
    },
    "white_balance": {
        "type": "str",
        "default": "auto",
        "description": "White balance mode",
        "allowed_values": ["auto", "manual", "daylight", "cloudy", "tungsten", "fluorescent"],
    },
    "iso": {
        "type": "int",
        "default": 400,
        "description": "ISO sensitivity",
        "min": 100,
        "max": 6400,
    },
}

# ============================================================================
# NODE CONFIGURATION SCHEMA
# ============================================================================

NODE_CONFIG_SCHEMA: Dict[str, Dict[str, Any]] = {
    "capture_enabled": {
        "type": "bool",
        "default": True,
        "description": "Enable capture on this node",
    },
    "upload_enabled": {
        "type": "bool",
        "default": True,
        "description": "Upload captures to server",
    },
    "upload_interval": {
        "type": "int",
        "default": 60,
        "description": "Upload batch interval in seconds",
        "min": 5,
        "max": 3600,
    },
    "max_retries": {
        "type": "int",
        "default": 3,
        "description": "Upload retry attempts",
        "min": 0,
        "max": 10,
    },
}

# ============================================================================
# VALIDATION & HELPER FUNCTIONS
# ============================================================================


def validate_config_value(key: str, value: Any, schema: Dict[str, Dict[str, Any]]) -> tuple[bool, str]:
    """Validate a config value against schema.
    
    Returns: (is_valid, error_message)
    """
    if key not in schema:
        return False, f"Unknown config key: {key}"
    
    config_def = schema[key]
    expected_type = config_def["type"]
    
    # Type validation
    type_map = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
    }
    
    if expected_type not in type_map:
        return False, f"Invalid schema type: {expected_type}"
    
    # Convert string to correct type
    try:
        if expected_type == "bool":
            if isinstance(value, bool):
                typed_value = value
            elif isinstance(value, str):
                typed_value = value.lower() in ("true", "1", "yes", "on")
            else:
                typed_value = bool(value)
        else:
            typed_value = type_map[expected_type](value)
    except (ValueError, TypeError):
        return False, f"Cannot convert {value} to {expected_type}"
    
    # Value validation
    if "allowed_values" in config_def:
        if typed_value not in config_def["allowed_values"]:
            return False, f"{key} must be one of {config_def['allowed_values']}"
    
    if "min" in config_def and typed_value < config_def["min"]:
        return False, f"{key} must be >= {config_def['min']}"
    
    if "max" in config_def and typed_value > config_def["max"]:
        return False, f"{key} must be <= {config_def['max']}"
    
    if "min_length" in config_def and len(typed_value) < config_def["min_length"]:
        return False, f"{key} must be at least {config_def['min_length']} chars"
    
    if "max_length" in config_def and len(typed_value) > config_def["max_length"]:
        return False, f"{key} must be at most {config_def['max_length']} chars"
    
    return True, ""


def get_default_config(scope: Literal["system", "camera", "node"]) -> Dict[str, Any]:
    """Get all default configs for a scope."""
    schemas = {
        "system": SYSTEM_CONFIG_SCHEMA,
        "camera": CAMERA_CONFIG_SCHEMA,
        "node": NODE_CONFIG_SCHEMA,
    }
    
    schema = schemas.get(scope, {})
    return {key: conf["default"] for key, conf in schema.items()}


def get_config_description(key: str, scope: Literal["system", "camera", "node"]) -> str:
    """Get description for a config key."""
    schemas = {
        "system": SYSTEM_CONFIG_SCHEMA,
        "camera": CAMERA_CONFIG_SCHEMA,
        "node": NODE_CONFIG_SCHEMA,
    }
    
    schema = schemas.get(scope, {})
    return schema.get(key, {}).get("description", "No description")
