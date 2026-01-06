"""
Integration tests for persistence workflows.

Tests cover:
- Basic persistence (save and load)
- Multiple sessions (save in one manager, load in another)
- Error recovery (corrupted files, missing files)
- Backward compatibility (in-memory mode still works)
- Complex workflows with persistence
"""

import json
import os
import tempfile
import unittest

from src.models.task import Task
from src.services.task_manager import TaskManager


class TestBasicPersistence(unittest.TestCase):
    """Tests for basic persistence workflows."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_save_single_task_to_file(self):
        """Test saving a single task to file."""
        manager = TaskManager(persistence_file=self.file_path)
        manager.add_task("Buy groceries", "For dinner")

        # Verify file was created
        self.assertTrue(os.path.exists(self.file_path))

        # Verify file contains the task
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['title'], "Buy groceries")

    def test_save_multiple_tasks_to_file(self):
        """Test saving multiple tasks to file."""
        manager = TaskManager(persistence_file=self.file_path)
        manager.add_task("Task 1", "Description 1")
        manager.add_task("Task 2", "Description 2")
        manager.add_task("Task 3")

        # Verify all tasks saved
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data['tasks']), 3)
        self.assertEqual(data['next_id'], 3)  # Counter is at 3 after 3 tasks

    def test_save_after_each_operation(self):
        """Test that file is updated after each operation."""
        manager = TaskManager(persistence_file=self.file_path)

        # Add first task
        manager.add_task("Task 1")
        with open(self.file_path, 'r') as f:
            data1 = json.load(f)
        self.assertEqual(len(data1['tasks']), 1)

        # Add second task
        manager.add_task("Task 2")
        with open(self.file_path, 'r') as f:
            data2 = json.load(f)
        self.assertEqual(len(data2['tasks']), 2)

        # Mark task complete
        manager.mark_task_complete(1)
        with open(self.file_path, 'r') as f:
            data3 = json.load(f)
        self.assertEqual(data3['tasks'][0]['status'], "complete")

    def test_load_existing_file(self):
        """Test loading tasks from an existing file."""
        # Create manager and add task
        manager1 = TaskManager(persistence_file=self.file_path)
        manager1.add_task("Buy groceries")

        # Create new manager and load from same file
        manager2 = TaskManager(persistence_file=self.file_path)

        # Verify task was loaded
        self.assertEqual(manager2.count_tasks(), 1)
        self.assertEqual(manager2.get_all_tasks()[0].title, "Buy groceries")

    def test_load_creates_new_file_if_missing(self):
        """Test that loading creates file if it doesn't exist."""
        self.assertFalse(os.path.exists(self.file_path))

        manager = TaskManager(persistence_file=self.file_path)

        self.assertTrue(os.path.exists(self.file_path))


class TestPersistenceAcrossSessions(unittest.TestCase):
    """Tests for persistence across multiple sessions."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_tasks_persist_across_sessions(self):
        """Test that tasks persist across multiple manager instances."""
        # Session 1: Add tasks
        manager1 = TaskManager(persistence_file=self.file_path)
        t1 = manager1.add_task("Task 1", "Description 1")
        t2 = manager1.add_task("Task 2")
        self.assertEqual(manager1.count_tasks(), 2)

        # Session 2: Load and verify
        manager2 = TaskManager(persistence_file=self.file_path)
        self.assertEqual(manager2.count_tasks(), 2)
        all_tasks = manager2.get_all_tasks()
        self.assertEqual(all_tasks[0].title, "Task 1")
        self.assertEqual(all_tasks[1].title, "Task 2")

    def test_completed_status_persists(self):
        """Test that task completion status persists across sessions."""
        # Session 1: Add and complete task
        manager1 = TaskManager(persistence_file=self.file_path)
        manager1.add_task("Task 1")
        manager1.mark_task_complete(1)

        # Session 2: Verify status
        manager2 = TaskManager(persistence_file=self.file_path)
        task = manager2.get_task_by_id(1)
        self.assertEqual(task.status, "complete")
        self.assertIsNotNone(task.completed_at)

    def test_id_counter_persists(self):
        """Test that ID counter persists across sessions."""
        # Session 1: Add tasks
        manager1 = TaskManager(persistence_file=self.file_path)
        manager1.add_task("Task 1")
        manager1.add_task("Task 2")
        manager1.delete_task(1)  # Delete task with ID 1

        # Session 2: Add new task, should get ID 3 (not 1)
        manager2 = TaskManager(persistence_file=self.file_path)
        new_task = manager2.add_task("Task 3")
        self.assertEqual(new_task.id, 3)

    def test_multiple_operations_across_sessions(self):
        """Test complex workflow across multiple sessions."""
        # Session 1: Add and modify
        mgr1 = TaskManager(persistence_file=self.file_path)
        mgr1.add_task("Task 1", "Desc 1")
        mgr1.add_task("Task 2", "Desc 2")
        mgr1.add_task("Task 3", "Desc 3")
        self.assertEqual(mgr1.count_tasks(), 3)

        # Session 2: Update and mark complete
        mgr2 = TaskManager(persistence_file=self.file_path)
        self.assertEqual(mgr2.count_tasks(), 3)
        mgr2.update_task(1, title="Updated Task 1")
        mgr2.mark_task_complete(2)

        # Session 3: Delete and verify
        mgr3 = TaskManager(persistence_file=self.file_path)
        self.assertEqual(mgr3.count_tasks(), 3)
        self.assertEqual(mgr3.get_task_by_id(1).title, "Updated Task 1")
        self.assertEqual(mgr3.get_task_by_id(2).status, "complete")
        mgr3.delete_task(3)
        self.assertEqual(mgr3.count_tasks(), 2)

        # Session 4: Add and verify counts
        mgr4 = TaskManager(persistence_file=self.file_path)
        self.assertEqual(mgr4.count_tasks(), 2)
        self.assertEqual(mgr4.count_completed(), 1)
        self.assertEqual(mgr4.count_pending(), 1)

    def test_timestamps_preserved(self):
        """Test that creation and completion timestamps persist."""
        # Session 1: Add and complete
        mgr1 = TaskManager(persistence_file=self.file_path)
        task = mgr1.add_task("Task 1")
        created_at_1 = task.created_at
        mgr1.mark_task_complete(1)
        completed_at_1 = task.completed_at

        # Session 2: Verify timestamps
        mgr2 = TaskManager(persistence_file=self.file_path)
        task2 = mgr2.get_task_by_id(1)
        self.assertEqual(task2.created_at, created_at_1)
        self.assertEqual(task2.completed_at, completed_at_1)


class TestErrorRecovery(unittest.TestCase):
    """Tests for error handling and recovery."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_corrupted_file_recovery(self):
        """Test recovery from corrupted file."""
        # Create corrupted file
        with open(self.file_path, 'w') as f:
            f.write("{ invalid json }")

        # Load from corrupted file should start fresh
        manager = TaskManager(persistence_file=self.file_path)

        # Should be empty
        self.assertEqual(manager.count_tasks(), 0)

        # Should be able to add tasks
        manager.add_task("New task")
        self.assertEqual(manager.count_tasks(), 1)

    def test_missing_file_creates_empty(self):
        """Test that missing file is created as empty."""
        self.assertFalse(os.path.exists(self.file_path))

        manager = TaskManager(persistence_file=self.file_path)

        # File should exist
        self.assertTrue(os.path.exists(self.file_path))

        # Should be empty
        self.assertEqual(manager.count_tasks(), 0)

        # Should be able to add tasks
        manager.add_task("Task 1")
        self.assertEqual(manager.count_tasks(), 1)

    def test_partial_invalid_data_loads_valid(self):
        """Test that partially corrupted data loads valid tasks."""
        # Create file with mix of valid and invalid tasks
        data = {
            'next_id': 3,
            'tasks': [
                {'id': 1, 'title': 'Valid Task', 'description': '', 'status': 'pending', 'created_at': '2026-01-01T10:00:00', 'completed_at': None},
                {'id': 2, 'title': '', 'description': '', 'status': 'pending'},  # Invalid: empty title
            ]
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

        # Load should get valid task only
        manager = TaskManager(persistence_file=self.file_path)
        self.assertEqual(manager.count_tasks(), 1)
        self.assertEqual(manager.get_task_by_id(1).title, "Valid Task")


class TestBackwardCompatibility(unittest.TestCase):
    """Tests for backward compatibility with in-memory mode."""

    def test_in_memory_mode_still_works(self):
        """Test that in-memory mode (no persistence_file) still works."""
        # Create manager without persistence
        manager = TaskManager()

        # Add tasks
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")

        # Tasks should be in memory
        self.assertEqual(manager.count_tasks(), 2)
        self.assertEqual(task1.id, 1)
        self.assertEqual(task2.id, 2)

        # Mark complete
        manager.mark_task_complete(1)
        self.assertEqual(manager.count_completed(), 1)

        # Update
        manager.update_task(2, title="Updated Task 2")
        self.assertEqual(manager.get_task_by_id(2).title, "Updated Task 2")

        # Delete
        manager.delete_task(1)
        self.assertEqual(manager.count_tasks(), 1)

    def test_in_memory_mode_no_file_operations(self):
        """Test that in-memory mode doesn't interact with files."""
        temp_dir = tempfile.TemporaryDirectory()
        file_path = os.path.join(temp_dir.name, 'tasks.json')

        try:
            # Create in-memory manager
            manager = TaskManager()
            manager.add_task("Task 1")

            # No file should be created
            self.assertFalse(os.path.exists(file_path))
        finally:
            temp_dir.cleanup()

    def test_persistence_optional_parameter(self):
        """Test that persistence parameter is optional."""
        # Both should work
        manager1 = TaskManager()
        manager2 = TaskManager(persistence_file=None)

        manager1.add_task("Task 1")
        manager2.add_task("Task 2")

        self.assertEqual(manager1.count_tasks(), 1)
        self.assertEqual(manager2.count_tasks(), 1)


class TestComplexPersistenceWorkflows(unittest.TestCase):
    """Tests for complex persistence workflows."""

    def setUp(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'tasks.json')

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_large_task_set_persistence(self):
        """Test persistence with large number of tasks."""
        # Session 1: Add many tasks
        mgr1 = TaskManager(persistence_file=self.file_path)
        for i in range(50):
            mgr1.add_task(f"Task {i+1}", f"Description for task {i+1}")

        self.assertEqual(mgr1.count_tasks(), 50)

        # Session 2: Verify all loaded
        mgr2 = TaskManager(persistence_file=self.file_path)
        self.assertEqual(mgr2.count_tasks(), 50)

        # Session 3: Mark some complete
        for i in range(1, 26):
            mgr2.mark_task_complete(i)
        self.assertEqual(mgr2.count_completed(), 25)

        # Session 4: Verify counts
        mgr3 = TaskManager(persistence_file=self.file_path)
        self.assertEqual(mgr3.count_completed(), 25)
        self.assertEqual(mgr3.count_pending(), 25)

    def test_stress_test_mixed_operations(self):
        """Test persistence with rapid mixed operations."""
        mgr = TaskManager(persistence_file=self.file_path)

        # Add, update, complete, delete in sequence
        for i in range(1, 11):
            task = mgr.add_task(f"Task {i}")
            if i % 3 == 0:
                mgr.mark_task_complete(task.id)
            if i % 5 == 0:
                mgr.update_task(task.id, title=f"Updated Task {i}")

        # Delete every other task
        for i in range(1, 11, 2):
            if mgr.is_task_exists(i):
                mgr.delete_task(i)

        # Load in new session and verify counts
        mgr2 = TaskManager(persistence_file=self.file_path)
        self.assertGreater(mgr2.count_tasks(), 0)
        self.assertLess(mgr2.count_tasks(), 10)

    def test_persistence_with_special_characters(self):
        """Test persistence with special characters in tasks."""
        mgr1 = TaskManager(persistence_file=self.file_path)
        mgr1.add_task("Buy 🛒 items", "For Sunday's dinner: pasta & meat\nwith fresh 🍅")

        # Load and verify
        mgr2 = TaskManager(persistence_file=self.file_path)
        task = mgr2.get_task_by_id(1)
        self.assertEqual(task.title, "Buy 🛒 items")
        self.assertIn("Sunday's", task.description)
        self.assertIn("🍅", task.description)


if __name__ == '__main__':
    unittest.main()
