"""
Vercel serverless handler for FastAPI application.

This is the entry point for Vercel's Python builder.
Vercel automatically wraps this ASGI application for serverless execution.
"""

import sys
from pathlib import Path

# Add backend to Python path for imports
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import and export the FastAPI ASGI application
# Vercel will automatically wrap this for serverless execution
from api.main import app

# Vercel looks for 'app' in the module
__all__ = ["app"]
