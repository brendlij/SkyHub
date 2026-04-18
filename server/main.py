"""Wrapper for uvicorn to run the FastAPI app."""

from server.app_main import app

__all__ = ["app"]
