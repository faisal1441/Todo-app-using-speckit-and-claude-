"""
Vercel serverless handler for FastAPI application.

This file serves as the entry point for Vercel's Python runtime.
It properly imports and exports the FastAPI ASGI application.
"""

import sys
import os
from pathlib import Path

# Get the directory paths
root_dir = Path(__file__).parent
backend_dir = root_dir / "backend"

# Add backend to Python path
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from api.main import app

# Export the app for Vercel
__all__ = ["app"]
