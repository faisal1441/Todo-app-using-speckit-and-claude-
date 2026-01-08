"""
Vercel entry point for FastAPI application.

Exports the FastAPI ASGI application for Vercel's Python runtime.
"""

from api.main import app

# Vercel will automatically wrap this ASGI app with its runtime handler
__all__ = ["app"]
