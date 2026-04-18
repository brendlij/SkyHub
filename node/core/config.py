"""Node configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class NodeSettings(BaseSettings):
    """Settings for the SkyHub node."""
    
    node_id: str = "node-1"
    camera_id: str = "camera-1"
    server_url: str = "http://localhost:8000"
    capture_interval: float = 10.0
    
    model_config = SettingsConfigDict(
        env_prefix="SKYHUB_NODE_",
        env_file=".env.node",
        env_file_encoding="utf-8",
    )


node_settings = NodeSettings()
