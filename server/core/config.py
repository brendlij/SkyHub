"""Server configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Settings for the SkyHub server."""
    
    app_name: str = "SkyHub Server"
    debug: bool = True
    storage_root: str = "./storage"
    
    # Location for day/night calculation (default: Vienna)
    latitude: float = 48.2082
    longitude: float = 16.3738
    
    # Database configuration
    database_type: str = "sqlite"  # "sqlite", "postgresql", "mysql"
    database_url: str = "sqlite:///./storage/db/skyhub.db"  # Default SQLite
    
    # Optional: PostgreSQL/MySQL override
    # Set to "postgresql://user:password@localhost/skyhub" for external DB
    
    model_config = SettingsConfigDict(
        env_prefix="SKYHUB_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


server_settings = ServerSettings()
