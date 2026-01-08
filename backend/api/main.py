"""
FastAPI application for Todo API.

This is the entry point for the backend API server.
It configures middleware, routes, and CORS for the application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

from .routes import tasks
from ..core.config import async_init_db

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="RESTful API for managing todo tasks",
    version="2.0.0",
)

# ============================================================================
# CORS Middleware Configuration
# ============================================================================

# Configure CORS to allow frontend to make requests
import os
try:
    origins = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Next.js dev server
        "http://localhost:3001",   # Next.js dev server (alternate port)
        "http://localhost:8000",   # Backend dev server (for testing)
        "http://127.0.0.1:5173",   # Localhost IPv4 (Vite)
        "http://127.0.0.1:3000",   # Localhost IPv4 (Next.js)
        "http://127.0.0.1:3001",   # Localhost IPv4 (Next.js - alternate port)
        "http://127.0.0.1:8000",   # Localhost IPv4 (Backend)
    ]

    # Add production domains when deployed to Vercel
    # Environment variable: VERCEL_URL or specific domain
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        origins.append(f"https://{vercel_url}")
        origins.append(f"https://*.{vercel_url}")
        # Also add www version
        if not vercel_url.startswith("www."):
            origins.append(f"https://www.{vercel_url}")
        # Add with .com extension if it's a custom domain
        if not vercel_url.endswith(".com"):
            origins.append(f"https://{vercel_url}.com")

    # Allow all origins as a fallback for development
    origins.append("*")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("[CORS] CORS middleware configured successfully")
except Exception as e:
    print(f"[CORS] WARNING: Failed to configure CORS: {e}")

# ============================================================================
# Include Routers
# ============================================================================

app.include_router(tasks.router, prefix="/api", tags=["tasks"])

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint providing API information.

    Returns:
        JSON with API details and documentation link
    """
    return {
        "message": "Todo API v2.0",
        "version": "2.0.0",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }


@app.get("/test")
async def test():
    """
    Test endpoint to verify the API is working.

    Returns:
        Simple JSON response
    """
    return {"status": "ok", "message": "API is working!"}


@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring.

    Returns:
        JSON indicating API is healthy
    """
    return {"status": "healthy"}


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(KeyError)
async def key_error_handler(request, exc):
    """Handle KeyError exceptions."""
    return JSONResponse(
        status_code=404,
        content={"detail": f"Not found: {str(exc)}"},
    )


# ============================================================================
# Application Events (Disabled for Vercel Serverless)
# ============================================================================

# NOTE: Startup/shutdown events are disabled for serverless compatibility
# Database initialization will happen on first request instead
# See routes.py for lazy initialization pattern
