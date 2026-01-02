"""
Task Model - Represents a single todo item with validation and status management.

This module defines the Task class which represents an individual task in the todo application.
Each task has a title, optional description, status (pending/complete), and timestamps.

Example:
    Creating a task:
        >>> task = Task("Buy groceries", "For Sunday dinner")
        >>> task.title
        'Buy groceries'
        >>> task.status
        'pending'

    Managing task status:
        >>> task.mark_complete()
        >>> task.is_complete()
        True
        >>> task.mark_incomplete()
        >>> task.is_pending()
        True
"""

from datetime import datetime


class Task:
    """
    Represents a single todo item with validation, status tracking, and timestamps.

    A Task encapsulates all information needed to manage a todo item: title, description,
    status, and creation/completion timestamps. The Task validates its own state and
    provides methods for status management.

    Attributes:
        id (int): Unique identifier for the task (set by TaskManager). Defaults to None.
        title (str): The task title/heading. Required and cannot be empty.
        description (str): Additional details about the task. Optional, defaults to empty string.
        status (str): Current task status. Either "pending" or "complete".
        created_at (datetime): Timestamp when task was created. Auto-set to current datetime.
        completed_at (datetime): Timestamp when task was marked complete. None if still pending.

    Raises:
        ValueError: If title is empty or contains only whitespace.

    Example:
        >>> task = Task("Buy groceries")
        >>> task.title
        'Buy groceries'
        >>> task.description
        ''
        >>> task.status
        'pending'
        >>> task.is_pending()
        True
    """

    def __init__(self, title: str, description: str = "") -> None:
        """
        Initialize a new Task with title and optional description.

        The Task is created in "pending" status with creation timestamp set to now.
        The title is stripped of leading/trailing whitespace before validation.

        Args:
            title (str): The task title. Required and must not be empty after stripping.
            description (str, optional): Additional task details. Defaults to empty string.

        Raises:
            ValueError: If title is empty or contains only whitespace.

        Example:
            >>> task = Task("Buy groceries")
            >>> task = Task("Cook dinner", "Italian pasta")
            >>> task = Task("")  # Raises ValueError
            >>> task = Task("   ")  # Raises ValueError
        """
        # Validate and set title
        title_stripped = title.strip() if title else ""
        if not title_stripped:
            raise ValueError("Task title cannot be empty")

        # Initialize task attributes
        self.id = None  # Will be set by TaskManager
        self.title = title_stripped
        self.description = description
        self.status = "pending"
        self.created_at = datetime.now()
        self.completed_at = None

    def mark_complete(self) -> None:
        """
        Mark the task as complete and record completion timestamp.

        Sets the task status to "complete" and records the current datetime as
        the completion time. If the task is already complete, this is a no-op
        (idempotent operation).

        Side Effects:
            - Sets status to "complete"
            - Sets completed_at to current datetime

        Example:
            >>> task = Task("Buy groceries")
            >>> task.status
            'pending'
            >>> task.completed_at is None
            True
            >>> task.mark_complete()
            >>> task.status
            'complete'
            >>> task.completed_at is not None
            True
        """
        self.status = "complete"
        self.completed_at = datetime.now()

    def mark_incomplete(self) -> None:
        """
        Mark the task as incomplete and clear completion timestamp.

        Sets the task status to "pending" and clears the completion timestamp.
        If the task is already pending, this is a no-op (idempotent operation).

        Side Effects:
            - Sets status to "pending"
            - Clears completed_at (set to None)

        Example:
            >>> task = Task("Buy groceries")
            >>> task.mark_complete()
            >>> task.status
            'complete'
            >>> task.mark_incomplete()
            >>> task.status
            'pending'
            >>> task.completed_at is None
            True
        """
        self.status = "pending"
        self.completed_at = None

    def is_complete(self) -> bool:
        """
        Check if the task is marked as complete.

        Returns:
            bool: True if task status is "complete", False otherwise.

        Example:
            >>> task = Task("Buy groceries")
            >>> task.is_complete()
            False
            >>> task.mark_complete()
            >>> task.is_complete()
            True
        """
        return self.status == "complete"

    def is_pending(self) -> bool:
        """
        Check if the task is marked as pending.

        Returns:
            bool: True if task status is "pending", False otherwise.

        Example:
            >>> task = Task("Buy groceries")
            >>> task.is_pending()
            True
            >>> task.mark_complete()
            >>> task.is_pending()
            False
        """
        return self.status == "pending"

    def set_title(self, new_title: str) -> None:
        """
        Update the task title with validation.

        The new title is stripped of leading/trailing whitespace before validation.
        The created_at timestamp is not modified when updating the title.

        Args:
            new_title (str): The new task title. Must not be empty after stripping.

        Raises:
            ValueError: If new_title is empty or contains only whitespace.

        Side Effects:
            - Updates self.title
            - Does NOT modify created_at, completed_at, or status

        Example:
            >>> task = Task("Buy groceries")
            >>> original_created = task.created_at
            >>> task.set_title("Buy groceries and cook")
            >>> task.title
            'Buy groceries and cook'
            >>> task.created_at == original_created
            True
            >>> task.set_title("")  # Raises ValueError
        """
        title_stripped = new_title.strip() if new_title else ""
        if not title_stripped:
            raise ValueError("Task title cannot be empty")

        self.title = title_stripped

    def set_description(self, new_description: str) -> None:
        """
        Update the task description.

        The description can be any string including empty. No validation is performed
        on the description. Timestamps and status are not modified.

        Args:
            new_description (str): The new task description. Can be empty string.

        Side Effects:
            - Updates self.description
            - Does NOT modify any other attributes

        Example:
            >>> task = Task("Buy groceries")
            >>> task.set_description("For Sunday dinner")
            >>> task.description
            'For Sunday dinner'
            >>> task.set_description("")  # Valid - description can be empty
            >>> task.description
            ''
        """
        self.description = new_description

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the task.

        Includes task ID, title, status, and creation timestamp. If the task is
        complete, includes the completion timestamp as well.

        Returns:
            str: Human-readable format "[#id] title (status) - Created: timestamp"

        Example:
            >>> task = Task("Buy groceries")
            >>> task.id = 1
            >>> str(task)
            '[#1] Buy groceries (pending) - Created: 2026-01-01 10:00:00'
            >>> task.mark_complete()
            >>> str(task)  # doctest: +ELLIPSIS
            '[#1] Buy groceries (complete) - Created: 2026-01-01 10:00:00 - Completed: 2026-01-01 10:...'
        """
        created_str = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        result = f"[#{self.id}] {self.title} ({self.status}) - Created: {created_str}"

        if self.is_complete() and self.completed_at:
            completed_str = self.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            result += f" - Completed: {completed_str}"

        return result

    def __repr__(self) -> str:
        """
        Return a debug representation of the task.

        Returns a string in the format that shows the most important attributes
        for debugging purposes.

        Returns:
            str: Debug format "Task(id=..., title=..., status=...)"

        Example:
            >>> task = Task("Buy groceries")
            >>> task.id = 1
            >>> repr(task)
            "Task(id=1, title='Buy groceries', status='pending')"
        """
        return f"Task(id={self.id}, title={self.title!r}, status={self.status!r})"
