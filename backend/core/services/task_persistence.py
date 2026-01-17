"""
Task persistence module for saving and loading tasks from JSON files.

This module provides:
- DateTime conversion helpers for ISO 8601 serialization
- TaskSerializer for Task object serialization/deserialization
- TaskFileManager for file I/O operations with error handling
"""

import json
import os
import shutil
from datetime import datetime
from typing import Optional, Tuple, List

from ..models.task import Task


# ============================================================================
# DateTime Conversion Helpers
# ============================================================================

def datetime_to_str(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime object to ISO 8601 string.

    Args:
        dt: datetime object or None

    Returns:
        ISO 8601 formatted string (e.g., "2026-01-01T10:00:00.123456") or None
    """
    if dt is None:
        return None
    return dt.isoformat()


def str_to_datetime(s: Optional[str]) -> Optional[datetime]:
    """
    Convert ISO 8601 string to datetime object.

    Args:
        s: ISO 8601 formatted string or None

    Returns:
        datetime object or None if string is None or invalid format
    """
    if s is None:
        return None
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


# ============================================================================
# TaskSerializer Class
# ============================================================================

class TaskSerializer:
    """
    Handles serialization and deserialization of Task objects to/from JSON.

    This class converts Task objects to dictionaries suitable for JSON storage
    and reconstructs Task objects from those dictionaries.
    """

    def task_to_dict(self, task: Task) -> dict:
        """
        Convert a Task object to a dictionary for JSON serialization.

        Args:
            task: Task object to serialize

        Returns:
            Dictionary with keys: id, title, description, status, created_at, completed_at
        """
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'created_at': datetime_to_str(task.created_at),
            'completed_at': datetime_to_str(task.completed_at),
        }

    def dict_to_task(self, data: dict) -> Optional[Task]:
        """
        Convert a dictionary to a Task object.

        Validates data before creating Task. Returns None if data is invalid.

        Args:
            data: Dictionary with task data

        Returns:
            Task object or None if data is invalid
        """
        if not self.validate_task_dict(data):
            return None

        try:
            # Create Task with title and description
            task = Task(title=data['title'], description=data.get('description', ''))

            # Manually set fields that bypass __init__
            task.id = data.get('id')
            task.status = data.get('status', 'pending')
            task.created_at = str_to_datetime(data.get('created_at'))
            task.completed_at = str_to_datetime(data.get('completed_at'))

            return task
        except (KeyError, TypeError, ValueError):
            return None

    def validate_task_dict(self, data: dict) -> bool:
        """
        Validate that a dictionary has all required task fields with correct types.

        Args:
            data: Dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False

        # Check required fields
        required_fields = ['id', 'title', 'description', 'status', 'created_at']
        for field in required_fields:
            if field not in data:
                return False

        # Check field types
        if not isinstance(data['id'], int):
            return False
        if not isinstance(data['title'], str) or not data['title'].strip():
            return False
        if not isinstance(data['description'], str):
            return False
        if data['status'] not in ('pending', 'complete'):
            return False
        if data['created_at'] is not None and not isinstance(data['created_at'], str):
            return False

        # completed_at can be None or string
        completed_at = data.get('completed_at')
        if completed_at is not None and not isinstance(completed_at, str):
            return False

        return True


# ============================================================================
# TaskFileManager Class
# ============================================================================

class TaskFileManager:
    """
    Manages file I/O operations for task persistence.

    Handles loading tasks from and saving tasks to JSON files with comprehensive
    error handling and atomic writes for crash safety.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize file manager with a file path.

        Args:
            file_path: Path to the JSON file for storing tasks
        """
        self.file_path = file_path
        self.serializer = TaskSerializer()

    def load_tasks(self) -> Tuple[List[Task], int]:
        """
        Load tasks from the JSON file.

        Returns (tasks_list, next_id). On any error, returns ([], 0) and prints warning.

        Returns:
            Tuple of (list of Task objects, next_id counter)
        """
        # File doesn't exist - create new
        if not os.path.exists(self.file_path):
            self.create_empty_file()
            return [], 0

        # File exists - try to load
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract next_id
            next_id = data.get('next_id', 0)

            # Load and validate tasks
            valid_tasks = []
            skipped = 0

            for task_data in data.get('tasks', []):
                task = self.serializer.dict_to_task(task_data)
                if task:
                    valid_tasks.append(task)
                else:
                    skipped += 1

            if skipped > 0:
                print(f"Warning: {skipped} tasks skipped due to invalid data")

            return valid_tasks, next_id

        except json.JSONDecodeError as e:
            print(f"Warning: Task file corrupted ({e}). Starting fresh.")
            self.backup_corrupt_file()
            self.create_empty_file()
            return [], 0

        except (PermissionError, OSError) as e:
            print(f"Warning: Cannot access task file ({e}). Using in-memory mode.")
            return [], 0

    def save_tasks(self, tasks: List[Task], next_id: int) -> bool:
        """
        Save tasks to the JSON file using atomic writes.

        Writes to temporary file first, then renames to final location to prevent
        corruption if the application crashes during write.

        Args:
            tasks: List of Task objects to save
            next_id: Next ID counter value

        Returns:
            True if successful, False on error
        """
        try:
            # Build data structure
            data = {
                'next_id': next_id,
                'tasks': [self.serializer.task_to_dict(task) for task in tasks],
            }

            # Write to temporary file first (atomic write)
            temp_path = self.file_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            # Atomic rename
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(temp_path, self.file_path)

            return True

        except (PermissionError, OSError) as e:
            print(f"Warning: Cannot save tasks ({e})")
            # Clean up temp file if it exists
            temp_path = self.file_path + '.tmp'
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return False

    def create_empty_file(self) -> bool:
        """
        Create a new empty tasks file.

        Returns:
            True if successful, False on error
        """
        try:
            data = {'next_id': 0, 'tasks': []}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Creating new task file: {self.file_path}")
            return True
        except (PermissionError, OSError) as e:
            print(f"Warning: Cannot create task file ({e})")
            return False

    def backup_corrupt_file(self) -> None:
        """
        Backup a corrupt file by renaming it with a .corrupt.{timestamp} suffix.

        This preserves the corrupt file for potential manual recovery while
        allowing the application to continue with a fresh file.
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.file_path}.corrupt.{timestamp}"
            shutil.copy2(self.file_path, backup_path)
            os.remove(self.file_path)
            print(f"Corrupt file backed up to: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not backup corrupt file ({e})")

    def file_exists(self) -> bool:
        """
        Check if the tasks file exists.

        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(self.file_path)
