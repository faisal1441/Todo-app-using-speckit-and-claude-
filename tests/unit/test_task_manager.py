"""
Unit tests for the TaskManager service class.

Tests cover:
- TaskManager initialization
- CRUD operations (add, retrieve, update, delete)
- Query and count methods
- Status management
- ID uniqueness and non-reuse
- Error handling and edge cases
"""

import unittest
from src.services.task_manager import TaskManager
from src.models.task import Task


class TestTaskManagerInitialization(unittest.TestCase):
    """Test TaskManager initialization."""

    def test_create_empty_task_manager(self):
        """Test creating a new TaskManager."""
        manager = TaskManager()
        self.assertIsNotNone(manager)
        self.assertEqual(manager.count_tasks(), 0)
        self.assertTrue(manager.is_empty())

    def test_initial_next_id_is_zero(self):
        """Test that initial ID counter is 0."""
        manager = TaskManager()
        self.assertEqual(manager._next_id, 0)

    def test_initial_tasks_list_is_empty(self):
        """Test that initial tasks list is empty."""
        manager = TaskManager()
        self.assertEqual(len(manager.tasks), 0)


class TestTaskManagerAddTask(unittest.TestCase):
    """Test adding tasks to the manager."""

    def setUp(self):
        """Create a fresh manager for each test."""
        self.manager = TaskManager()

    def test_add_task_with_title_only(self):
        """Test adding a task with title only."""
        task = self.manager.add_task("Buy groceries")
        self.assertEqual(task.title, "Buy groceries")
        self.assertEqual(task.description, "")
        self.assertEqual(task.status, "pending")
        self.assertIsNotNone(task.id)

    def test_add_task_with_title_and_description(self):
        """Test adding a task with title and description."""
        task = self.manager.add_task("Cook dinner", "Italian pasta")
        self.assertEqual(task.title, "Cook dinner")
        self.assertEqual(task.description, "Italian pasta")

    def test_add_task_increments_id(self):
        """Test that each new task gets a unique ID."""
        task1 = self.manager.add_task("Task 1")
        task2 = self.manager.add_task("Task 2")
        task3 = self.manager.add_task("Task 3")
        self.assertEqual(task1.id, 1)
        self.assertEqual(task2.id, 2)
        self.assertEqual(task3.id, 3)

    def test_add_task_increments_count(self):
        """Test that adding tasks increments the count."""
        self.assertEqual(self.manager.count_tasks(), 0)
        self.manager.add_task("Task 1")
        self.assertEqual(self.manager.count_tasks(), 1)
        self.manager.add_task("Task 2")
        self.assertEqual(self.manager.count_tasks(), 2)

    def test_add_task_with_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_task("")

    def test_add_task_with_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_added_task_appears_in_list(self):
        """Test that added tasks appear in get_all_tasks()."""
        task = self.manager.add_task("Task")
        all_tasks = self.manager.get_all_tasks()
        self.assertIn(task, all_tasks)

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks."""
        for i in range(5):
            self.manager.add_task(f"Task {i+1}")
        self.assertEqual(self.manager.count_tasks(), 5)


class TestTaskManagerGetTask(unittest.TestCase):
    """Test retrieving tasks."""

    def setUp(self):
        """Create a manager with sample tasks."""
        self.manager = TaskManager()
        self.task1 = self.manager.add_task("Task 1")
        self.task2 = self.manager.add_task("Task 2")
        self.task3 = self.manager.add_task("Task 3")

    def test_get_task_by_id(self):
        """Test retrieving a task by ID."""
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task, self.task1)
        self.assertEqual(task.title, "Task 1")

    def test_get_task_by_different_ids(self):
        """Test retrieving different tasks by ID."""
        task1 = self.manager.get_task_by_id(1)
        task2 = self.manager.get_task_by_id(2)
        task3 = self.manager.get_task_by_id(3)
        self.assertEqual(task1.id, 1)
        self.assertEqual(task2.id, 2)
        self.assertEqual(task3.id, 3)

    def test_get_task_with_invalid_id_raises_error(self):
        """Test that invalid ID raises KeyError."""
        with self.assertRaises(KeyError) as context:
            self.manager.get_task_by_id(999)
        self.assertIn("not found", str(context.exception))

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        all_tasks = self.manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 3)
        self.assertEqual(all_tasks[0].id, 1)
        self.assertEqual(all_tasks[1].id, 2)
        self.assertEqual(all_tasks[2].id, 3)

    def test_get_all_tasks_empty(self):
        """Test getting all tasks when empty."""
        manager = TaskManager()
        all_tasks = manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 0)

    def test_get_all_tasks_returns_copy(self):
        """Test that get_all_tasks returns a copy."""
        all_tasks = self.manager.get_all_tasks()
        all_tasks.pop()  # Modify the returned list
        # Original should be unchanged
        self.assertEqual(self.manager.count_tasks(), 3)


class TestTaskManagerUpdateTask(unittest.TestCase):
    """Test updating tasks."""

    def setUp(self):
        """Create a manager with a sample task."""
        self.manager = TaskManager()
        self.task = self.manager.add_task("Original Title", "Original Desc")

    def test_update_task_title_only(self):
        """Test updating only the title."""
        self.manager.update_task(1, title="New Title")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "New Title")
        self.assertEqual(task.description, "Original Desc")

    def test_update_task_description_only(self):
        """Test updating only the description."""
        self.manager.update_task(1, description="New Desc")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "Original Title")
        self.assertEqual(task.description, "New Desc")

    def test_update_task_both_title_and_description(self):
        """Test updating both title and description."""
        self.manager.update_task(1, title="New Title", description="New Desc")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "New Title")
        self.assertEqual(task.description, "New Desc")

    def test_update_task_with_none_values(self):
        """Test that None values don't modify the task."""
        self.manager.update_task(1, title=None, description=None)
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "Original Title")
        self.assertEqual(task.description, "Original Desc")

    def test_update_nonexistent_task_raises_error(self):
        """Test that updating nonexistent task raises KeyError."""
        with self.assertRaises(KeyError):
            self.manager.update_task(999, title="New Title")

    def test_update_task_with_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.update_task(1, title="")

    def test_update_does_not_change_status(self):
        """Test that update doesn't change task status."""
        self.manager.mark_task_complete(1)
        self.manager.update_task(1, title="New Title")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.status, "complete")

    def test_update_does_not_change_created_at(self):
        """Test that update doesn't change created_at timestamp."""
        original_created = self.task.created_at
        self.manager.update_task(1, title="New Title")
        self.assertEqual(self.task.created_at, original_created)

    def test_multiple_updates_to_same_task(self):
        """Test updating the same task multiple times."""
        self.manager.update_task(1, title="Update 1")
        self.manager.update_task(1, title="Update 2")
        self.manager.update_task(1, title="Update 3")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "Update 3")


class TestTaskManagerDeleteTask(unittest.TestCase):
    """Test deleting tasks."""

    def setUp(self):
        """Create a manager with sample tasks."""
        self.manager = TaskManager()
        self.task1 = self.manager.add_task("Task 1")
        self.task2 = self.manager.add_task("Task 2")
        self.task3 = self.manager.add_task("Task 3")

    def test_delete_task(self):
        """Test deleting a task."""
        result = self.manager.delete_task(1)
        self.assertTrue(result)
        self.assertEqual(self.manager.count_tasks(), 2)

    def test_deleted_task_not_in_list(self):
        """Test that deleted task is not in get_all_tasks()."""
        self.manager.delete_task(1)
        all_tasks = self.manager.get_all_tasks()
        task_ids = [t.id for t in all_tasks]
        self.assertNotIn(1, task_ids)

    def test_delete_middle_task(self):
        """Test deleting a task from the middle of the list."""
        self.manager.delete_task(2)
        all_tasks = self.manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 2)
        self.assertEqual(all_tasks[0].id, 1)
        self.assertEqual(all_tasks[1].id, 3)

    def test_delete_nonexistent_task_raises_error(self):
        """Test that deleting nonexistent task raises KeyError."""
        with self.assertRaises(KeyError):
            self.manager.delete_task(999)

    def test_id_not_reused_after_deletion(self):
        """Test that deleted IDs are not reused."""
        self.manager.delete_task(1)
        self.manager.delete_task(2)
        new_task = self.manager.add_task("New Task")
        self.assertEqual(new_task.id, 4)  # Not 1 or 2

    def test_delete_all_tasks(self):
        """Test deleting all tasks."""
        self.manager.delete_task(1)
        self.manager.delete_task(2)
        self.manager.delete_task(3)
        self.assertEqual(self.manager.count_tasks(), 0)
        self.assertTrue(self.manager.is_empty())

    def test_add_after_delete(self):
        """Test adding tasks after deletion."""
        self.manager.delete_task(1)
        self.manager.delete_task(2)
        new_task = self.manager.add_task("New Task")
        self.assertEqual(new_task.id, 4)
        self.assertEqual(self.manager.count_tasks(), 2)


class TestTaskManagerStatusOperations(unittest.TestCase):
    """Test task status management."""

    def setUp(self):
        """Create a manager with sample tasks."""
        self.manager = TaskManager()
        self.task = self.manager.add_task("Task")

    def test_mark_task_complete(self):
        """Test marking a task complete."""
        self.manager.mark_task_complete(1)
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.status, "complete")

    def test_mark_task_incomplete(self):
        """Test marking a task incomplete."""
        self.manager.mark_task_complete(1)
        self.manager.mark_task_incomplete(1)
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.status, "pending")

    def test_mark_nonexistent_task_complete_raises_error(self):
        """Test that marking nonexistent task raises KeyError."""
        with self.assertRaises(KeyError):
            self.manager.mark_task_complete(999)

    def test_mark_nonexistent_task_incomplete_raises_error(self):
        """Test that marking nonexistent task incomplete raises KeyError."""
        with self.assertRaises(KeyError):
            self.manager.mark_task_incomplete(999)

    def test_toggle_completion_multiple_times(self):
        """Test toggling completion status multiple times."""
        for i in range(5):
            is_even = (i % 2) == 0
            if is_even:
                self.manager.mark_task_complete(1)
                self.assertTrue(self.manager.get_task_by_id(1).is_complete())
            else:
                self.manager.mark_task_incomplete(1)
                self.assertTrue(self.manager.get_task_by_id(1).is_pending())


class TestTaskManagerQueryOperations(unittest.TestCase):
    """Test task query and filtering operations."""

    def setUp(self):
        """Create a manager with mixed task statuses."""
        self.manager = TaskManager()
        self.t1 = self.manager.add_task("Task 1")
        self.t2 = self.manager.add_task("Task 2")
        self.t3 = self.manager.add_task("Task 3")
        self.manager.mark_task_complete(1)
        self.manager.mark_task_complete(3)

    def test_get_pending_tasks(self):
        """Test getting pending tasks."""
        pending = self.manager.get_pending_tasks()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].id, 2)

    def test_get_completed_tasks(self):
        """Test getting completed tasks."""
        completed = self.manager.get_completed_tasks()
        self.assertEqual(len(completed), 2)
        task_ids = [t.id for t in completed]
        self.assertEqual(sorted(task_ids), [1, 3])

    def test_get_pending_tasks_empty(self):
        """Test getting pending tasks when all are complete."""
        manager = TaskManager()
        task = manager.add_task("Task")
        manager.mark_task_complete(1)
        pending = manager.get_pending_tasks()
        self.assertEqual(len(pending), 0)

    def test_get_completed_tasks_empty(self):
        """Test getting completed tasks when all are pending."""
        manager = TaskManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        completed = manager.get_completed_tasks()
        self.assertEqual(len(completed), 0)

    def test_count_pending(self):
        """Test counting pending tasks."""
        self.assertEqual(self.manager.count_pending(), 1)

    def test_count_completed(self):
        """Test counting completed tasks."""
        self.assertEqual(self.manager.count_completed(), 2)

    def test_count_tasks(self):
        """Test counting total tasks."""
        self.assertEqual(self.manager.count_tasks(), 3)

    def test_count_after_changes(self):
        """Test counts after adding and completing tasks."""
        self.manager.add_task("Task 4")
        self.assertEqual(self.manager.count_tasks(), 4)
        self.assertEqual(self.manager.count_pending(), 2)
        self.manager.mark_task_complete(2)
        self.assertEqual(self.manager.count_pending(), 1)
        self.assertEqual(self.manager.count_completed(), 3)


class TestTaskManagerUtilityOperations(unittest.TestCase):
    """Test utility methods."""

    def setUp(self):
        """Create a fresh manager."""
        self.manager = TaskManager()

    def test_is_empty_initially(self):
        """Test that new manager is empty."""
        self.assertTrue(self.manager.is_empty())

    def test_is_empty_after_adding_task(self):
        """Test that is_empty is False after adding task."""
        self.manager.add_task("Task")
        self.assertFalse(self.manager.is_empty())

    def test_is_empty_after_deleting_all_tasks(self):
        """Test that is_empty is True after deleting all tasks."""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.delete_task(1)
        self.manager.delete_task(2)
        self.assertTrue(self.manager.is_empty())

    def test_is_task_exists_true(self):
        """Test is_task_exists for existing task."""
        self.manager.add_task("Task")
        self.assertTrue(self.manager.is_task_exists(1))

    def test_is_task_exists_false(self):
        """Test is_task_exists for nonexistent task."""
        self.assertFalse(self.manager.is_task_exists(999))

    def test_is_task_exists_after_delete(self):
        """Test is_task_exists after deleting task."""
        self.manager.add_task("Task")
        self.assertTrue(self.manager.is_task_exists(1))
        self.manager.delete_task(1)
        self.assertFalse(self.manager.is_task_exists(1))


class TestTaskManagerEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def test_large_number_of_tasks(self):
        """Test managing a large number of tasks."""
        manager = TaskManager()
        for i in range(100):
            manager.add_task(f"Task {i+1}")
        self.assertEqual(manager.count_tasks(), 100)

    def test_id_generation_with_many_deletes(self):
        """Test ID generation after many deletions."""
        manager = TaskManager()
        # Add 10 tasks
        for i in range(10):
            manager.add_task(f"Task {i+1}")
        # Delete every other task
        for i in range(1, 11, 2):
            manager.delete_task(i)
        # Add new task - should have ID 11
        new_task = manager.add_task("New Task")
        self.assertEqual(new_task.id, 11)

    def test_complex_workflow(self):
        """Test a complex workflow with multiple operations."""
        manager = TaskManager()

        # Add tasks
        t1 = manager.add_task("Task 1")
        t2 = manager.add_task("Task 2")
        t3 = manager.add_task("Task 3")

        # Update some
        manager.update_task(1, title="Updated Task 1")

        # Complete some
        manager.mark_task_complete(1)
        manager.mark_task_complete(3)

        # Delete one
        manager.delete_task(2)

        # Verify state
        self.assertEqual(manager.count_tasks(), 2)
        self.assertEqual(manager.count_completed(), 2)
        self.assertEqual(manager.count_pending(), 0)

        # Add new task
        t4 = manager.add_task("Task 4")
        self.assertEqual(t4.id, 4)


if __name__ == "__main__":
    unittest.main()
