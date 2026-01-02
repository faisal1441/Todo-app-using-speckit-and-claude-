"""
Task API endpoints.

This module defines all API routes for task operations:
- GET /api/tasks - List all tasks (with optional status filter)
- POST /api/tasks - Create new task
- GET /api/tasks/{id} - Get task by ID
- PUT /api/tasks/{id} - Update task
- DELETE /api/tasks/{id} - Delete task
- PATCH /api/tasks/{id}/complete - Mark task complete
- PATCH /api/tasks/{id}/incomplete - Mark task incomplete
- GET /api/tasks/stats - Get task statistics
"""

import os
import tempfile
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.core.services.task_manager import TaskManager
from backend.api.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStats,
)

# Create router
router = APIRouter(tags=["tasks"])

# Initialize TaskManager with persistence
# Use system temp directory for cross-platform compatibility
# (will reset on Vercel cold starts, but works locally)
temp_dir = tempfile.gettempdir()
persistence_file = os.path.join(temp_dir, "tasks.json")
manager = TaskManager(persistence_file=persistence_file)


# ============================================================================
# Utility function to convert Task to Pydantic model
# ============================================================================

def task_to_response(task) -> TaskResponse:
    """Convert Task object to TaskResponse Pydantic model."""
    return TaskResponse.model_validate(task, from_attributes=True)


# ============================================================================
# Error handlers
# ============================================================================

def handle_errors(func):
    """Decorator to handle common errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    return wrapper


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/tasks", response_model=list[TaskResponse])
async def get_all_tasks(status: Optional[str] = Query(None, pattern="^(pending|complete)$")):
    """
    Get all tasks, optionally filtered by status.

    Query Parameters:
        status (optional): Filter by status - "pending" or "complete"

    Returns:
        List of TaskResponse objects
    """
    try:
        if status == "pending":
            tasks = manager.get_pending_tasks()
        elif status == "complete":
            tasks = manager.get_completed_tasks()
        else:
            tasks = manager.get_all_tasks()

        return [task_to_response(task) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate):
    """
    Create a new task.

    Request body:
        - title (required): Task title
        - description (optional): Task description

    Returns:
        Created TaskResponse object
    """
    try:
        task = manager.add_task(task_data.title, task_data.description)
        return task_to_response(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@router.get("/tasks/stats", response_model=TaskStats)
async def get_stats():
    """
    Get task statistics.

    Returns:
        TaskStats object with total, pending, and completed counts
    """
    try:
        return TaskStats(
            total=manager.count_tasks(),
            pending=manager.count_pending(),
            completed=manager.count_completed()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """
    Get a specific task by ID.

    Path Parameters:
        task_id: The task ID

    Returns:
        TaskResponse object

    Raises:
        404: If task not found
    """
    try:
        task = manager.get_task_by_id(task_id)
        return task_to_response(task)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskUpdate):
    """
    Update a task's title and/or description.

    Path Parameters:
        task_id: The task ID

    Request body:
        - title (optional): New task title
        - description (optional): New task description

    Returns:
        Updated TaskResponse object

    Raises:
        404: If task not found
        400: If title is invalid
    """
    try:
        task = manager.update_task(
            task_id,
            title=task_data.title,
            description=task_data.description
        )
        return task_to_response(task)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    """
    Delete a task.

    Path Parameters:
        task_id: The task ID

    Raises:
        404: If task not found
    """
    try:
        manager.delete_task(task_id)
        return None
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def mark_complete(task_id: int):
    """
    Mark a task as complete.

    Path Parameters:
        task_id: The task ID

    Returns:
        Updated TaskResponse object

    Raises:
        404: If task not found
    """
    try:
        task = manager.mark_task_complete(task_id)
        return task_to_response(task)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking task complete: {str(e)}")


@router.patch("/tasks/{task_id}/incomplete", response_model=TaskResponse)
async def mark_incomplete(task_id: int):
    """
    Mark a task as incomplete.

    Path Parameters:
        task_id: The task ID

    Returns:
        Updated TaskResponse object

    Raises:
        404: If task not found
    """
    try:
        task = manager.mark_task_incomplete(task_id)
        return task_to_response(task)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking task incomplete: {str(e)}")


