"""
Vercel entry point for FastAPI application.

This is the standard entry point that Vercel looks for when deploying Python applications.
Vercel automatically runs this file as the serverless function handler.
"""

from api.main import app

# Export the FastAPI app instance for Vercel
# Vercel will wrap this with its runtime handler
__all__ = ["app"]

# For Vercel Python runtime, the app instance is directly used
