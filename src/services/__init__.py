"""
Services package - Business logic and data management

Exports:
  - TaskManager: In-memory task storage and CRUD operations
"""

from .task_manager import TaskManager

__all__ = ['TaskManager']
