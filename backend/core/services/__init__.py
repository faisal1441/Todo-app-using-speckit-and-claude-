"""
Services package - Business logic and data management

Exports:
  - TaskManager: In-memory task storage and CRUD operations
  - TaskFileManager: File persistence for tasks
  - TaskSerializer: Serialization utilities
"""

from backend.core.services.task_manager import TaskManager
from backend.core.services.task_persistence import TaskFileManager, TaskSerializer

__all__ = ['TaskManager', 'TaskFileManager', 'TaskSerializer']
