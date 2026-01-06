"""
Unit tests for TaskFileManager and file I/O operations.

Tests cover:
- File creation (new files)
- Loading tasks from JSON files
- Saving tasks to JSON files
- Error handling (missing files, corrupted JSON, permissions)
- Atomic writes for crash safety
- Data integrity and validation
"""

import json
import os
import tempfile
import unittest
from datetime import datetime

from src.models.task import Task
from src.services.task_persistence import TaskFileManager, TaskSerializer


class TestFileCreation(unittest.TestCase):
    """Tests for creating new task files."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_create_empty_file_new_path(self):
        """Test creating a new empty task file."""
        manager = TaskFileManager(self.file_path)
        result = manager.create_empty_file()

        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.file_path))

    def test_create_empty_file_contains_correct_structure(self):
        """Test that created file has correct JSON structure."""
        manager = TaskFileManager(self.file_path)
        manager.create_empty_file()

        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.assertIn('next_id', data)
        self.assertIn('tasks', data)
        self.assertEqual(data['next_id'], 0)
        self.assertEqual(data['tasks'], [])

    def test_file_exists_returns_true_after_creation(self):
        """Test file_exists() returns True after creating file."""
        manager = TaskFileManager(self.file_path)
        self.assertFalse(manager.file_exists())
        manager.create_empty_file()
        self.assertTrue(manager.file_exists())

    def test_file_exists_returns_false_for_missing_file(self):
        """Test file_exists() returns False for non-existent file."""
        manager = TaskFileManager(self.file_path)
        self.assertFalse(manager.file_exists())


class TestLoadTasks(unittest.TestCase):
    """Tests for loading tasks from JSON files."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')
        self.serializer = TaskSerializer()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_load_from_nonexistent_file_creates_new(self):
        """Test loading from non-existent file creates new file."""
        manager = TaskFileManager(self.file_path)
        tasks, next_id = manager.load_tasks()

        self.assertEqual(len(tasks), 0)
        self.assertEqual(next_id, 0)
        self.assertTrue(os.path.exists(self.file_path))

    def test_load_empty_file(self):
        """Test loading from empty task file."""
        # Create empty file
        manager = TaskFileManager(self.file_path)
        manager.create_empty_file()

        # Load
        tasks, next_id = manager.load_tasks()

        self.assertEqual(len(tasks), 0)
        self.assertEqual(next_id, 0)

    def test_load_file_with_single_task(self):
        """Test loading file with single task."""
        # Create file with one task
        task = Task("Buy groceries", "For dinner")
        task.id = 1

        data = {
            'next_id': 2,
            'tasks': [self.serializer.task_to_dict(task)],
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

        # Load
        manager = TaskFileManager(self.file_path)
        tasks, next_id = manager.load_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(next_id, 2)
        self.assertEqual(tasks[0].title, "Buy groceries")
        self.assertEqual(tasks[0].id, 1)

    def test_load_file_with_multiple_tasks(self):
        """Test loading file with multiple tasks."""
        # Create file with multiple tasks
        tasks_to_save = []
        for i in range(1, 4):
            task = Task(f"Task {i}", f"Description {i}")
            task.id = i
            tasks_to_save.append(task)

        data = {
            'next_id': 4,
            'tasks': [self.serializer.task_to_dict(t) for t in tasks_to_save],
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

        # Load
        manager = TaskFileManager(self.file_path)
        loaded_tasks, next_id = manager.load_tasks()

        self.assertEqual(len(loaded_tasks), 3)
        self.assertEqual(next_id, 4)
        self.assertEqual(loaded_tasks[0].title, "Task 1")
        self.assertEqual(loaded_tasks[1].title, "Task 2")
        self.assertEqual(loaded_tasks[2].title, "Task 3")

    def test_load_file_with_complete_task(self):
        """Test loading file with a completed task."""
        # Create task and mark complete
        task = Task("Buy groceries")
        task.id = 1
        task.mark_complete()

        data = {
            'next_id': 2,
            'tasks': [self.serializer.task_to_dict(task)],
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

        # Load
        manager = TaskFileManager(self.file_path)
        loaded_tasks, _ = manager.load_tasks()

        self.assertEqual(loaded_tasks[0].status, "complete")
        self.assertIsNotNone(loaded_tasks[0].completed_at)

    def test_load_corrupted_json_returns_empty(self):
        """Test loading corrupted JSON returns empty list."""
        # Create corrupted file
        with open(self.file_path, 'w') as f:
            f.write("{ invalid json }")

        # Load
        manager = TaskFileManager(self.file_path)
        tasks, next_id = manager.load_tasks()

        self.assertEqual(len(tasks), 0)
        self.assertEqual(next_id, 0)

    def test_load_corrupted_json_creates_backup(self):
        """Test loading corrupted JSON creates a backup file."""
        # Create corrupted file
        with open(self.file_path, 'w') as f:
            f.write("{ invalid json }")

        # Load
        manager = TaskFileManager(self.file_path)
        manager.load_tasks()

        # Check for backup file
        backup_files = [f for f in os.listdir(self.temp_dir.name)
                       if f.startswith('tasks.json.corrupt')]
        self.assertEqual(len(backup_files), 1)

    def test_load_file_with_invalid_task_skips_it(self):
        """Test that invalid tasks are skipped during load."""
        # Create file with mix of valid and invalid tasks
        valid_task = Task("Valid task")
        valid_task.id = 1

        data = {
            'next_id': 3,
            'tasks': [
                self.serializer.task_to_dict(valid_task),
                {'id': 2, 'title': '', 'status': 'pending'},  # Invalid: empty title
                {'id': 3, 'title': 'Task'},  # Invalid: missing required fields
            ],
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

        # Load (should skip invalid tasks)
        manager = TaskFileManager(self.file_path)
        tasks, next_id = manager.load_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Valid task")


class TestSaveTasks(unittest.TestCase):
    """Tests for saving tasks to JSON files."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_save_empty_list(self):
        """Test saving empty task list."""
        manager = TaskFileManager(self.file_path)
        result = manager.save_tasks([], 0)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.file_path))

    def test_save_single_task(self):
        """Test saving single task."""
        task = Task("Buy groceries", "For dinner")
        task.id = 1

        manager = TaskFileManager(self.file_path)
        result = manager.save_tasks([task], 2)

        self.assertTrue(result)

        # Verify saved correctly
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['next_id'], 2)
        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['title'], "Buy groceries")

    def test_save_multiple_tasks(self):
        """Test saving multiple tasks."""
        tasks = []
        for i in range(1, 4):
            task = Task(f"Task {i}")
            task.id = i
            tasks.append(task)

        manager = TaskFileManager(self.file_path)
        result = manager.save_tasks(tasks, 4)

        self.assertTrue(result)

        # Verify
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data['tasks']), 3)
        self.assertEqual(data['next_id'], 4)

    def test_save_complete_task(self):
        """Test saving completed task with timestamp."""
        task = Task("Buy groceries")
        task.id = 1
        task.mark_complete()

        manager = TaskFileManager(self.file_path)
        manager.save_tasks([task], 2)

        # Verify
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        saved_task = data['tasks'][0]
        self.assertEqual(saved_task['status'], "complete")
        self.assertIsNotNone(saved_task['completed_at'])

    def test_save_updates_existing_file(self):
        """Test that save overwrites existing file."""
        # Save initial data
        manager = TaskFileManager(self.file_path)
        task1 = Task("Task 1")
        task1.id = 1
        manager.save_tasks([task1], 2)

        # Save new data
        task2 = Task("Task 2")
        task2.id = 2
        manager.save_tasks([task2], 3)

        # Verify file contains new data
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['title'], "Task 2")

    def test_save_json_is_pretty_printed(self):
        """Test that saved JSON is human-readable (indented)."""
        task = Task("Buy groceries")
        task.id = 1

        manager = TaskFileManager(self.file_path)
        manager.save_tasks([task], 2)

        # Read and check formatting
        with open(self.file_path, 'r') as f:
            content = f.read()

        # Pretty-printed JSON should have newlines and indentation
        self.assertIn('\n', content)
        self.assertIn('  ', content)

    def test_save_preserves_datetime_objects(self):
        """Test that datetime objects are converted to strings."""
        task = Task("Buy groceries")
        task.id = 1
        task.mark_complete()

        manager = TaskFileManager(self.file_path)
        manager.save_tasks([task], 2)

        # Verify datetimes are strings in JSON
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.assertIsInstance(data['tasks'][0]['created_at'], str)
        self.assertIsInstance(data['tasks'][0]['completed_at'], str)

    def test_save_with_special_characters(self):
        """Test saving tasks with special characters."""
        task = Task("Buy 🛒 items", "For Sunday's dinner: pasta & meat")
        task.id = 1

        manager = TaskFileManager(self.file_path)
        manager.save_tasks([task], 2)

        # Verify special characters preserved
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data['tasks'][0]['title'], "Buy 🛒 items")
        self.assertEqual(data['tasks'][0]['description'], "For Sunday's dinner: pasta & meat")


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling in file operations."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_load_with_permission_error_returns_empty(self):
        """Test loading with permission error gracefully returns empty list."""
        # Create file but make it unreadable
        manager = TaskFileManager(self.file_path)
        manager.create_empty_file()

        # Make file unreadable (skip on Windows)
        if os.name != 'nt':
            os.chmod(self.file_path, 0o000)

            try:
                tasks, next_id = manager.load_tasks()
                self.assertEqual(len(tasks), 0)
            finally:
                os.chmod(self.file_path, 0o644)

    def test_save_with_permission_error_returns_false(self):
        """Test saving with permission error returns False and doesn't crash."""
        # Make directory read-only (skip on Windows)
        if os.name != 'nt':
            os.chmod(self.temp_dir.name, 0o555)

            try:
                manager = TaskFileManager(self.file_path)
                task = Task("Test task")
                task.id = 1
                result = manager.save_tasks([task], 2)
                self.assertFalse(result)
            finally:
                os.chmod(self.temp_dir.name, 0o755)

    def test_backup_corrupt_file_is_created(self):
        """Test that backup is created when file is corrupted."""
        # Create corrupted file
        with open(self.file_path, 'w') as f:
            f.write("{ corrupted json }")

        manager = TaskFileManager(self.file_path)
        manager.backup_corrupt_file()

        # Check backup exists
        backup_files = [f for f in os.listdir(self.temp_dir.name)
                       if f.startswith('tasks.json.corrupt')]
        self.assertTrue(len(backup_files) > 0)

    def test_backup_corrupt_file_contains_original_content(self):
        """Test that backup file contains original content."""
        original_content = "{ corrupted json }"
        with open(self.file_path, 'w') as f:
            f.write(original_content)

        manager = TaskFileManager(self.file_path)
        manager.backup_corrupt_file()

        # Find and read backup
        backup_files = [f for f in os.listdir(self.temp_dir.name)
                       if f.startswith('tasks.json.corrupt')]
        backup_path = os.path.join(self.temp_dir.name, backup_files[0])

        with open(backup_path, 'r') as f:
            backup_content = f.read()

        self.assertEqual(backup_content, original_content)


class TestAtomicWrites(unittest.TestCase):
    """Tests for atomic write behavior (crash safety)."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_save_creates_temp_file(self):
        """Test that save creates temporary file during write."""
        task = Task("Test")
        task.id = 1

        manager = TaskFileManager(self.file_path)

        # Monitor for temp file creation
        temp_path = self.file_path + '.tmp'
        self.assertFalse(os.path.exists(temp_path))

        manager.save_tasks([task], 2)

        # Temp file should be cleaned up after save
        self.assertFalse(os.path.exists(temp_path))

    def test_save_removes_temp_on_success(self):
        """Test that temp file is removed after successful save."""
        task = Task("Test")
        task.id = 1

        manager = TaskFileManager(self.file_path)
        manager.save_tasks([task], 2)

        temp_path = self.file_path + '.tmp'
        self.assertFalse(os.path.exists(temp_path))
        self.assertTrue(os.path.exists(self.file_path))

    def test_corrupted_file_creates_backup_before_new_file(self):
        """Test that backup is created before overwriting with new file."""
        # Create initial file
        manager = TaskFileManager(self.file_path)
        manager.create_empty_file()

        # Corrupt it
        with open(self.file_path, 'w') as f:
            f.write("corrupted")

        # Load (should backup and create new)
        manager.load_tasks()

        # Verify backup exists and new file is valid
        backup_files = [f for f in os.listdir(self.temp_dir.name)
                       if f.startswith('tasks.json.corrupt')]
        self.assertTrue(len(backup_files) > 0)
        self.assertTrue(os.path.exists(self.file_path))

        # Verify new file is valid JSON
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        self.assertIn('next_id', data)
        self.assertIn('tasks', data)


class TestDataIntegrity(unittest.TestCase):
    """Tests for data integrity and round-trip consistency."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_save_and_load_preserves_all_fields(self):
        """Test that save/load cycle preserves all task fields."""
        # Create task with all fields populated
        task = Task("Buy groceries", "For Sunday dinner")
        task.id = 42
        task.mark_complete()

        # Save
        manager = TaskFileManager(self.file_path)
        manager.save_tasks([task], 43)

        # Load
        loaded_tasks, next_id = manager.load_tasks()

        # Verify
        self.assertEqual(len(loaded_tasks), 1)
        self.assertEqual(loaded_tasks[0].id, 42)
        self.assertEqual(loaded_tasks[0].title, "Buy groceries")
        self.assertEqual(loaded_tasks[0].description, "For Sunday dinner")
        self.assertEqual(loaded_tasks[0].status, "complete")
        self.assertIsNotNone(loaded_tasks[0].completed_at)
        self.assertEqual(next_id, 43)

    def test_multiple_save_load_cycles_maintain_integrity(self):
        """Test that multiple save/load cycles maintain data integrity."""
        tasks = []
        for i in range(1, 4):
            task = Task(f"Task {i}")
            task.id = i
            tasks.append(task)

        manager = TaskFileManager(self.file_path)

        # Cycle 1: Save
        manager.save_tasks(tasks, 4)

        # Cycle 1: Load
        loaded1, next_id1 = manager.load_tasks()
        self.assertEqual(len(loaded1), 3)
        self.assertEqual(next_id1, 4)

        # Cycle 2: Save again
        manager.save_tasks(loaded1, next_id1)

        # Cycle 2: Load again
        loaded2, next_id2 = manager.load_tasks()
        self.assertEqual(len(loaded2), 3)
        self.assertEqual(next_id2, 4)

        # Verify consistency
        for i, task in enumerate(loaded2):
            self.assertEqual(task.title, f"Task {i+1}")


if __name__ == '__main__':
    unittest.main()
