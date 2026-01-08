"""
WSGI entry point for Vercel deployment.

Vercel expects a WSGI-compatible application at the root of the Python package.
This module exports the FastAPI app wrapped with a compatible ASGI-to-WSGI adapter.
"""

from api.main import app

__all__ = ["app"]
