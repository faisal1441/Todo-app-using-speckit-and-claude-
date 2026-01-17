"""
Task API endpoints.

This module defines all API routes for task operations using SQLModel and PostgreSQL with asyncpg:
- GET /api/tasks - List all tasks (with optional status filter)
- POST /api/tasks - Create new task
- GET /api/tasks/{id} - Get task by ID
- PUT /api/tasks/{id} - Update task
- DELETE /api/tasks/{id} - Delete task
- PATCH /api/tasks/{id}/complete - Mark task complete
- PATCH /api/tasks/{id}/incomplete - Mark task incomplete
- GET /api/tasks/stats - Get task statistics
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from core.models.task import Task
from core.config import get_session
from api.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStats,
)

# Create router
router = APIRouter(tags=["tasks"])


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/tasks/stats", response_model=TaskStats)
async def get_stats(session: AsyncSession = Depends(get_session)):
    """
    Get task statistics.

    Returns:
        TaskStats object with total, pending, and completed counts
    """
    try:
        # Get total count
        total_result = await session.execute(select(func.count(Task.id)))
        total = total_result.scalar() or 0

        # Get pending count
        pending_result = await session.execute(
            select(func.count(Task.id)).where(Task.status == "pending")
        )
        pending = pending_result.scalar() or 0

        # Get completed count
        completed_result = await session.execute(
            select(func.count(Task.id)).where(Task.status == "complete")
        )
        completed = completed_result.scalar() or 0

        return TaskStats(total=total, pending=pending, completed=completed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.get("/tasks", response_model=list[TaskResponse])
async def get_all_tasks(
    status: Optional[str] = Query(None, pattern="^(pending|complete)$"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all tasks, optionally filtered by status.

    Query Parameters:
        status (optional): Filter by status - "pending" or "complete"

    Returns:
        List of TaskResponse objects
    """
    try:
        statement = select(Task).order_by(Task.created_at.desc())

        if status:
            statement = statement.where(Task.status == status)

        result = await session.execute(statement)
        tasks = result.scalars().all()
        return [TaskResponse.model_validate(task, from_attributes=True) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate, session: AsyncSession = Depends(get_session)):
    """
    Create a new task.

    Request body:
        - title (required): Task title
        - description (optional): Task description

    Returns:
        Created TaskResponse object
    """
    try:
        if not task_data.title or not task_data.title.strip():
            raise ValueError("Task title cannot be empty")

        task = Task(title=task_data.title, description=task_data.description)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return TaskResponse.model_validate(task, from_attributes=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)):
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
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return TaskResponse.model_validate(task, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, task_data: TaskUpdate, session: AsyncSession = Depends(get_session)
):
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
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        if task_data.title is not None:
            if not task_data.title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = task_data.title

        if task_data.description is not None:
            task.description = task_data.description

        session.add(task)
        await session.commit()
        await session.refresh(task)
        return TaskResponse.model_validate(task, from_attributes=True)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    """
    Delete a task.

    Path Parameters:
        task_id: The task ID

    Raises:
        404: If task not found
    """
    try:
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        session.delete(task)
        await session.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def mark_complete(task_id: int, session: AsyncSession = Depends(get_session)):
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
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        task.mark_complete()
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return TaskResponse.model_validate(task, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking task complete: {str(e)}")


@router.patch("/tasks/{task_id}/incomplete", response_model=TaskResponse)
async def mark_incomplete(task_id: int, session: AsyncSession = Depends(get_session)):
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
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        task.mark_incomplete()
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return TaskResponse.model_validate(task, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking task incomplete: {str(e)}")
