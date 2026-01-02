"""
Pydantic schemas for Task API validation.

These models define the shape of request/response data for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Used in POST /api/tasks requests.
    """
    title: str = Field(..., min_length=1, max_length=200, description="Task title (required)")
    description: str = Field(default="", max_length=1000, description="Task description (optional)")


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    Used in PUT /api/tasks/{id} requests. Both fields are optional.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")


class TaskResponse(BaseModel):
    """
    Schema for task response in API endpoints.

    Represents a complete Task object returned by the API.
    """
    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    status: str = Field(..., description="Task status: 'pending' or 'complete'")
    created_at: datetime = Field(..., description="Timestamp when task was created")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when task was marked complete")

    class Config:
        from_attributes = True  # Allow creating from Task object using attribute names


class TaskStats(BaseModel):
    """
    Schema for task statistics response.

    Used in GET /api/tasks/stats endpoint.
    """
    total: int = Field(..., description="Total number of tasks")
    pending: int = Field(..., description="Number of pending tasks")
    completed: int = Field(..., description="Number of completed tasks")
