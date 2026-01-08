"""
ASGI entry point for Vercel deployment.

Vercel expects either a WSGI or ASGI application at the root level.
FastAPI is an ASGI framework, so we export the app directly.
"""

import sys
import os

print(f"[WSGI] Python path: {sys.path}")
print(f"[WSGI] Current directory: {os.getcwd()}")
print(f"[WSGI] Python version: {sys.version}")

try:
    from api.main import app
    print("[WSGI] Successfully imported FastAPI app from api.main")
except Exception as e:
    print(f"[WSGI] ERROR importing app: {e}")
    import traceback
    traceback.print_exc()
    raise

__all__ = ["app"]
