"""
TaskManager Service - In-memory task storage and CRUD operations.

This module provides the TaskManager class which manages all task operations including
creation, retrieval, updating, deletion, and querying. It maintains data integrity
by ensuring unique IDs and valid task states.

Example:
    Creating and managing tasks:
        >>> manager = TaskManager()
        >>> task = manager.add_task("Buy groceries")
        >>> task.id
        1
        >>> task = manager.add_task("Cook dinner", "Italian pasta")
        >>> manager.count_tasks()
        2
        >>> manager.mark_task_complete(1)
        >>> manager.count_completed()
        1
"""

from typing import Optional

from ..models.task import Task
from .task_persistence import TaskFileManager


class TaskManager:
    """
    Manages in-memory task storage with CRUD operations and queries.

    The TaskManager maintains a list of Task objects and provides methods for:
    - Creating new tasks with automatic unique ID assignment
    - Retrieving tasks by ID or filtering by status
    - Updating task properties
    - Deleting tasks
    - Querying task statistics

    Attributes:
        tasks (list[Task]): Collection of all Task objects.
        _next_id (int): Counter for generating unique task IDs. Starts at 0, increments to 1 for first task.

    Properties:
        All tasks are validated before creation. IDs are never reused after deletion.

    Example:
        >>> manager = TaskManager()
        >>> task1 = manager.add_task("Task 1")
        >>> task2 = manager.add_task("Task 2", "Description")
        >>> manager.count_tasks()
        2
        >>> manager.mark_task_complete(1)
        >>> manager.count_completed()
        1
        >>> manager.delete_task(2)
        >>> manager.count_tasks()
        1
    """

    def __init__(self, persistence_file: Optional[str] = None) -> None:
        """
        Initialize a new TaskManager with optional file persistence.

        Creates a task manager that can optionally load and save tasks to a JSON file.
        If persistence_file is provided and the file exists, tasks are loaded from the file.
        If the file doesn't exist, a new empty file is created.
        If persistence_file is None, the manager operates in pure in-memory mode.

        Args:
            persistence_file: Optional path to JSON file for task persistence.
                            If None, operates in in-memory mode (no file I/O).

        Example:
            >>> # In-memory mode (no persistence)
            >>> manager = TaskManager()
            >>> manager.count_tasks()
            0

            >>> # With persistence
            >>> manager = TaskManager(persistence_file="tasks.json")
            >>> # Tasks loaded from tasks.json if it exists
        """
        if persistence_file:
            self._file_manager = TaskFileManager(persistence_file)
            self.tasks, self._next_id = self._file_manager.load_tasks()
        else:
            self._file_manager = None
            self.tasks = []
            self._next_id = 0

    def _save_if_persistent(self) -> None:
        """
        Save tasks to file if persistence is enabled.

        Called after each mutating operation to automatically save changes.
        If persistence is not enabled, this method does nothing.
        On save errors, prints a warning but doesn't crash the application.

        Side Effects:
            - Writes tasks to JSON file if persistence_file was provided in __init__
            - Prints warning if save fails
        """
        if self._file_manager:
            try:
                self._file_manager.save_tasks(self.tasks, self._next_id)
            except Exception as e:
                print(f"Warning: Could not save tasks: {e}")

    # CRUD Operations

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Create and add a new task to the task list.

        Creates a Task object with the provided title and description, assigns it
        a unique ID, and adds it to the task list. The task is created in "pending"
        status with the current timestamp.

        Args:
            title (str): The task title. Required and must not be empty.
            description (str, optional): Task description. Defaults to empty string.

        Returns:
            Task: The newly created and stored Task object with assigned ID.

        Raises:
            ValueError: If the title is empty or contains only whitespace (from Task validation).

        Side Effects:
            - Increments the ID counter
            - Appends task to the tasks list

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Buy groceries")
            >>> task.id
            1
            >>> task = manager.add_task("Cook", "Italian")
            >>> task.id
            2
            >>> manager.add_task("")  # Raises ValueError
        """
        # Create Task object (may raise ValueError if invalid)
        task = Task(title, description)

        # Assign unique ID and add to list
        self._next_id += 1
        task.id = self._next_id
        self.tasks.append(task)

        # Save to file if persistence is enabled
        self._save_if_persistent()

        return task

    def get_task_by_id(self, task_id: int) -> Task:
        """
        Retrieve a task by its unique ID.

        Searches the task list for a task matching the given ID and returns it.

        Args:
            task_id (int): The unique ID of the task to retrieve.

        Returns:
            Task: The task with the matching ID.

        Raises:
            KeyError: If no task with the given ID exists.

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Task")
            >>> retrieved = manager.get_task_by_id(1)
            >>> retrieved.id == task.id
            True
            >>> manager.get_task_by_id(999)  # Raises KeyError
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"Task with ID {task_id} not found")

    def update_task(
        self, task_id: int, title: str = None, description: str = None
    ) -> Task:
        """
        Update a task's title and/or description.

        Retrieves the task by ID and updates the specified properties. Only provided
        arguments are updated; None values are skipped. The task's status and timestamps
        are not modified.

        Args:
            task_id (int): The ID of the task to update.
            title (str, optional): New title. None means no change.
            description (str, optional): New description. None means no change.

        Returns:
            Task: The updated Task object.

        Raises:
            KeyError: If the task with given ID doesn't exist.
            ValueError: If the new title is invalid (empty or whitespace-only).

        Side Effects:
            - Modifies task.title if title is provided and valid
            - Modifies task.description if description is provided
            - Does NOT modify status or timestamps

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Original", "Desc")
            >>> task = manager.update_task(1, title="Updated")
            >>> task.title
            'Updated'
            >>> task.description
            'Desc'
            >>> manager.update_task(1, description="New desc")
            >>> manager.get_task_by_id(1).description
            'New desc'
        """
        # Get the task (raises KeyError if not found)
        task = self.get_task_by_id(task_id)

        # Update title if provided
        if title is not None:
            task.set_title(title)

        # Update description if provided
        if description is not None:
            task.set_description(description)

        # Save to file if persistence is enabled
        self._save_if_persistent()

        return task

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task from the task list.

        Removes the task with the given ID from the task list permanently.
        The task ID is NOT reused; future tasks will have new IDs that continue
        incrementing from the current counter.

        Args:
            task_id (int): The ID of the task to delete.

        Returns:
            bool: True if deletion was successful.

        Raises:
            KeyError: If no task with the given ID exists.

        Side Effects:
            - Removes task from self.tasks
            - Does NOT reset or reuse the ID

        Example:
            >>> manager = TaskManager()
            >>> t1 = manager.add_task("Task 1")  # ID: 1
            >>> t2 = manager.add_task("Task 2")  # ID: 2
            >>> manager.delete_task(1)
            True
            >>> manager.count_tasks()
            1
            >>> t3 = manager.add_task("Task 3")  # ID: 3, not 1
            >>> t3.id
            3
            >>> manager.delete_task(999)  # Raises KeyError
        """
        # Find and remove the task
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                # Save to file if persistence is enabled
                self._save_if_persistent()
                return True

        # Task not found
        raise KeyError(f"Task with ID {task_id} not found")

    # Status Management

    def mark_task_complete(self, task_id: int) -> Task:
        """
        Mark a task as complete.

        Retrieves the task by ID and marks it as complete, recording the completion
        timestamp.

        Args:
            task_id (int): The ID of the task to mark complete.

        Returns:
            Task: The updated Task object.

        Raises:
            KeyError: If no task with the given ID exists.

        Side Effects:
            - Changes task.status to "complete"
            - Sets task.completed_at to current datetime

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Task")
            >>> task.status
            'pending'
            >>> manager.mark_task_complete(1)
            >>> task.status
            'complete'
        """
        task = self.get_task_by_id(task_id)
        task.mark_complete()
        # Save to file if persistence is enabled
        self._save_if_persistent()
        return task

    def mark_task_incomplete(self, task_id: int) -> Task:
        """
        Mark a task as incomplete.

        Retrieves the task by ID and marks it as incomplete, clearing the completion
        timestamp.

        Args:
            task_id (int): The ID of the task to mark incomplete.

        Returns:
            Task: The updated Task object.

        Raises:
            KeyError: If no task with the given ID exists.

        Side Effects:
            - Changes task.status to "pending"
            - Clears task.completed_at (set to None)

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Task")
            >>> manager.mark_task_complete(1)
            >>> manager.mark_task_incomplete(1)
            >>> task.status
            'pending'
        """
        task = self.get_task_by_id(task_id)
        task.mark_incomplete()
        # Save to file if persistence is enabled
        self._save_if_persistent()
        return task

    # Query Operations

    def get_all_tasks(self) -> list:
        """
        Retrieve all tasks in creation order.

        Returns a list of all Task objects currently in storage. If no tasks exist,
        returns an empty list.

        Returns:
            list[Task]: All tasks in creation order.

        Example:
            >>> manager = TaskManager()
            >>> manager.get_all_tasks()
            []
            >>> manager.add_task("Task 1")
            >>> manager.add_task("Task 2")
            >>> len(manager.get_all_tasks())
            2
        """
        return self.tasks.copy()

    def get_pending_tasks(self) -> list:
        """
        Retrieve all tasks with pending status.

        Returns a filtered list of tasks that have status "pending".

        Returns:
            list[Task]: All pending tasks in creation order.

        Example:
            >>> manager = TaskManager()
            >>> t1 = manager.add_task("Task 1")
            >>> t2 = manager.add_task("Task 2")
            >>> manager.mark_task_complete(1)
            >>> len(manager.get_pending_tasks())
            1
        """
        return [task for task in self.tasks if task.is_pending()]

    def get_completed_tasks(self) -> list:
        """
        Retrieve all tasks with complete status.

        Returns a filtered list of tasks that have status "complete".

        Returns:
            list[Task]: All completed tasks.

        Example:
            >>> manager = TaskManager()
            >>> t1 = manager.add_task("Task 1")
            >>> t2 = manager.add_task("Task 2")
            >>> manager.mark_task_complete(1)
            >>> len(manager.get_completed_tasks())
            1
        """
        return [task for task in self.tasks if task.is_complete()]

    # Count Operations

    def count_tasks(self) -> int:
        """
        Get the total number of tasks.

        Returns:
            int: Total number of tasks in the task list.

        Example:
            >>> manager = TaskManager()
            >>> manager.count_tasks()
            0
            >>> manager.add_task("Task")
            >>> manager.count_tasks()
            1
        """
        return len(self.tasks)

    def count_pending(self) -> int:
        """
        Get the count of pending tasks.

        Returns:
            int: Number of tasks with "pending" status.

        Example:
            >>> manager = TaskManager()
            >>> manager.add_task("Task 1")
            >>> manager.add_task("Task 2")
            >>> manager.count_pending()
            2
            >>> manager.mark_task_complete(1)
            >>> manager.count_pending()
            1
        """
        return len(self.get_pending_tasks())

    def count_completed(self) -> int:
        """
        Get the count of completed tasks.

        Returns:
            int: Number of tasks with "complete" status.

        Example:
            >>> manager = TaskManager()
            >>> manager.add_task("Task")
            >>> manager.count_completed()
            0
            >>> manager.mark_task_complete(1)
            >>> manager.count_completed()
            1
        """
        return len(self.get_completed_tasks())

    # Utility Operations

    def is_task_exists(self, task_id: int) -> bool:
        """
        Check if a task with the given ID exists.

        Returns:
            bool: True if a task with the ID exists, False otherwise.

        Example:
            >>> manager = TaskManager()
            >>> manager.add_task("Task")
            >>> manager.is_task_exists(1)
            True
            >>> manager.is_task_exists(999)
            False
        """
        for task in self.tasks:
            if task.id == task_id:
                return True
        return False

    def is_empty(self) -> bool:
        """
        Check if the task list is empty.

        Returns:
            bool: True if no tasks exist, False otherwise.

        Example:
            >>> manager = TaskManager()
            >>> manager.is_empty()
            True
            >>> manager.add_task("Task")
            >>> manager.is_empty()
            False
        """
        return len(self.tasks) == 0
