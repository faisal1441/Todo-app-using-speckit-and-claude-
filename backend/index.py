"""
Vercel entry point for FastAPI application.

Exports the FastAPI ASGI application for Vercel's Python runtime.
"""

import sys
import os

# Add backend directory to Python path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from api.main import app

# Vercel will automatically wrap this ASGI app with its runtime handler
__all__ = ["app"]
