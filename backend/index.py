"""
Vercel entry point for FastAPI application.

This is the standard entry point that Vercel looks for when deploying Python applications.
Vercel automatically wraps this ASGI app with its runtime handler.
"""

import sys
import os

# Ensure we can import from the backend package
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("[index.py] Attempting to import FastAPI app...")
    from api.main import app
    print("[index.py] SUCCESS: FastAPI app imported successfully")
except ImportError as e:
    print(f"[index.py] IMPORT ERROR: {e}")
    raise
except Exception as e:
    print(f"[index.py] UNEXPECTED ERROR during import: {e}")
    import traceback
    traceback.print_exc()
    raise

# Export the FastAPI ASGI app for Vercel
__all__ = ["app"]
