"""
CLI package - Command-line user interface

Exports:
  - main: Entry point for the console application
  - TaskManager: Task management service
"""

from src.cli.main import main
from src.services.task_manager import TaskManager

__all__ = ['main', 'TaskManager']
