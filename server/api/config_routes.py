"""Configuration API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.config_service import ConfigService, CameraConfigService


router = APIRouter(prefix="/api/config", tags=["configuration"])


class ConfigItem(BaseModel):
    """Configuration item."""
    key: str
    value: dict | str | int | float | bool
    scope: str = "system"
    description: str | None = None


class ConfigResponse(BaseModel):
    """Response for config operations."""
    key: str
    value: dict | str | int | float | bool
    scope: str
    description: str | None = None
    set_at: str | None = None
    success: bool = True


class CameraConfigItem(BaseModel):
    """Camera configuration."""
    node_id: str | None = None
    camera_id: str | None = None
    exposure: float | None = None
    gain: float | None = None
    resolution: str | None = None
    frame_rate: int | None = None
    enabled: bool | None = None
    capture_interval: float | None = None
    white_balance: str | None = None
    iso: int | None = None


def init_config_routes(config_service: ConfigService, camera_config_service: CameraConfigService) -> APIRouter:
    """Initialize configuration routes."""
    
    @router.get("/")
    async def get_all_configs(scope: str = "system") -> dict:
        """
        Get all configuration for a scope.
        
        Parameters:
            scope: "system", "node:{id}", "camera:{id}"
        """
        return config_service.get_all(scope=scope)
    
    @router.get("/{key}")
    async def get_config(key: str, scope: str = "system") -> ConfigResponse:
        """
        Get a specific configuration value.
        
        Parameters:
            key: Configuration key
            scope: "system", "node:{id}", "camera:{id}"
        """
        value = config_service.get(key, scope=scope)
        
        if value is None:
            raise HTTPException(status_code=404, detail=f"Config {key} not found")
        
        return ConfigResponse(key=key, value=value, scope=scope)
    
    @router.post("/")
    async def set_config(item: ConfigItem) -> ConfigResponse:
        """
        Set or update configuration.
        
        Parameters:
            key: Configuration key
            value: Configuration value
            scope: "system", "node:{id}", "camera:{id}"
            description: Optional description
        """
        try:
            config_service.set(
                key=item.key,
                value=item.value,
                scope=item.scope,
                description=item.description,
            )
            
            return ConfigResponse(
                key=item.key,
                value=item.value,
                scope=item.scope,
                success=True,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.delete("/{key}")
    async def delete_config(key: str, scope: str = "system") -> dict:
        """
        Delete configuration.
        
        Parameters:
            key: Configuration key
            scope: "system", "node:{id}", "camera:{id}"
        """
        config_service.delete(key, scope=scope)
        return {"success": True, "key": key, "scope": scope}
    
    @router.get("/camera/{node_id}/{camera_id}")
    async def get_camera_config(node_id: str, camera_id: str) -> dict:
        """
        Get camera-specific configuration.
        
        Parameters:
            node_id: Node identifier
            camera_id: Camera identifier
        """
        return camera_config_service.get_camera_config(node_id, camera_id)
    
    @router.post("/camera/{node_id}/{camera_id}")
    async def set_camera_config(node_id: str, camera_id: str, config: CameraConfigItem) -> dict:
        """
        Update camera configuration.
        
        Parameters:
            node_id: Node identifier
            camera_id: Camera identifier
            config: Camera configuration object
        """
        try:
            config_data = config.dict(exclude_none=True)
            return camera_config_service.set_camera_config(node_id, camera_id, config_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/camera/all")
    async def get_all_camera_configs() -> list:
        """Get all camera configurations."""
        return camera_config_service.get_all_camera_configs()
    
    return router
