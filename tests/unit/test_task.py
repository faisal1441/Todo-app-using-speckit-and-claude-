"""
Unit tests for the Task model class.

Tests cover:
- Task constructor with validation
- Status management methods
- Property setters
- String representations
- Edge cases and error handling
"""

import unittest
from datetime import datetime
from src.models.task import Task


class TestTaskConstructor(unittest.TestCase):
    """Test Task constructor and initialization."""

    def test_create_task_with_valid_title(self):
        """Test creating a task with a valid title."""
        task = Task("Buy groceries")
        self.assertEqual(task.title, "Buy groceries")
        self.assertEqual(task.description, "")
        self.assertEqual(task.status, "pending")
        self.assertIsNone(task.id)
        self.assertIsNotNone(task.created_at)
        self.assertIsNone(task.completed_at)

    def test_create_task_with_title_and_description(self):
        """Test creating a task with both title and description."""
        task = Task("Cook dinner", "Italian pasta")
        self.assertEqual(task.title, "Cook dinner")
        self.assertEqual(task.description, "Italian pasta")
        self.assertEqual(task.status, "pending")

    def test_create_task_with_empty_description(self):
        """Test that description defaults to empty string."""
        task = Task("Buy groceries")
        self.assertEqual(task.description, "")

    def test_create_task_strips_whitespace_from_title(self):
        """Test that title is stripped of leading/trailing whitespace."""
        task = Task("  Buy groceries  ")
        self.assertEqual(task.title, "Buy groceries")

    def test_create_task_with_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Task("")
        self.assertIn("Task title cannot be empty", str(context.exception))

    def test_create_task_with_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Task("   ")
        self.assertIn("Task title cannot be empty", str(context.exception))

    def test_create_task_with_none_title_raises_error(self):
        """Test that None title raises ValueError."""
        with self.assertRaises(ValueError):
            Task(None)

    def test_task_status_defaults_to_pending(self):
        """Test that new tasks default to pending status."""
        task = Task("Task")
        self.assertEqual(task.status, "pending")
        self.assertTrue(task.is_pending())
        self.assertFalse(task.is_complete())

    def test_task_created_at_is_set_automatically(self):
        """Test that created_at is set to current datetime."""
        before = datetime.now()
        task = Task("Task")
        after = datetime.now()
        self.assertGreaterEqual(task.created_at, before)
        self.assertLessEqual(task.created_at, after)

    def test_task_completed_at_is_none_initially(self):
        """Test that completed_at is None for new tasks."""
        task = Task("Task")
        self.assertIsNone(task.completed_at)

    def test_task_id_is_none_initially(self):
        """Test that task ID is None (set by TaskManager)."""
        task = Task("Task")
        self.assertIsNone(task.id)


class TestTaskStatusMethods(unittest.TestCase):
    """Test Task status management methods."""

    def setUp(self):
        """Create a fresh task for each test."""
        self.task = Task("Test task")

    def test_mark_complete_sets_status(self):
        """Test that mark_complete() changes status to complete."""
        self.assertEqual(self.task.status, "pending")
        self.task.mark_complete()
        self.assertEqual(self.task.status, "complete")

    def test_mark_complete_sets_completed_at(self):
        """Test that mark_complete() records completion time."""
        self.assertIsNone(self.task.completed_at)
        before = datetime.now()
        self.task.mark_complete()
        after = datetime.now()
        self.assertIsNotNone(self.task.completed_at)
        self.assertGreaterEqual(self.task.completed_at, before)
        self.assertLessEqual(self.task.completed_at, after)

    def test_mark_complete_is_idempotent(self):
        """Test that marking complete multiple times is safe."""
        self.task.mark_complete()
        first_completion = self.task.completed_at
        self.task.mark_complete()
        # Should have new timestamp (not idempotent for timestamp)
        self.assertIsNotNone(self.task.completed_at)

    def test_mark_incomplete_sets_status(self):
        """Test that mark_incomplete() changes status to pending."""
        self.task.mark_complete()
        self.assertEqual(self.task.status, "complete")
        self.task.mark_incomplete()
        self.assertEqual(self.task.status, "pending")

    def test_mark_incomplete_clears_completed_at(self):
        """Test that mark_incomplete() clears the completion timestamp."""
        self.task.mark_complete()
        self.assertIsNotNone(self.task.completed_at)
        self.task.mark_incomplete()
        self.assertIsNone(self.task.completed_at)

    def test_mark_incomplete_from_pending_is_safe(self):
        """Test that marking incomplete on pending task is safe."""
        # Already pending, should not raise error
        self.task.mark_incomplete()
        self.assertEqual(self.task.status, "pending")
        self.assertIsNone(self.task.completed_at)

    def test_is_complete_returns_true_when_complete(self):
        """Test is_complete() returns True for complete tasks."""
        self.task.mark_complete()
        self.assertTrue(self.task.is_complete())

    def test_is_complete_returns_false_when_pending(self):
        """Test is_complete() returns False for pending tasks."""
        self.assertFalse(self.task.is_complete())

    def test_is_pending_returns_true_when_pending(self):
        """Test is_pending() returns True for pending tasks."""
        self.assertTrue(self.task.is_pending())

    def test_is_pending_returns_false_when_complete(self):
        """Test is_pending() returns False for complete tasks."""
        self.task.mark_complete()
        self.assertFalse(self.task.is_pending())

    def test_toggle_completion_multiple_times(self):
        """Test toggling completion status multiple times."""
        self.assertTrue(self.task.is_pending())
        self.task.mark_complete()
        self.assertTrue(self.task.is_complete())
        self.task.mark_incomplete()
        self.assertTrue(self.task.is_pending())
        self.task.mark_complete()
        self.assertTrue(self.task.is_complete())


class TestTaskPropertySetters(unittest.TestCase):
    """Test Task property setter methods."""

    def setUp(self):
        """Create a fresh task for each test."""
        self.task = Task("Original title", "Original description")

    def test_set_title_updates_title(self):
        """Test that set_title() updates the title."""
        self.task.set_title("New title")
        self.assertEqual(self.task.title, "New title")

    def test_set_title_strips_whitespace(self):
        """Test that set_title() strips leading/trailing whitespace."""
        self.task.set_title("  New title  ")
        self.assertEqual(self.task.title, "New title")

    def test_set_title_does_not_modify_created_at(self):
        """Test that set_title() doesn't change created_at timestamp."""
        original_created = self.task.created_at
        self.task.set_title("New title")
        self.assertEqual(self.task.created_at, original_created)

    def test_set_title_does_not_modify_status(self):
        """Test that set_title() doesn't change status."""
        self.task.mark_complete()
        self.task.set_title("New title")
        self.assertEqual(self.task.status, "complete")

    def test_set_title_does_not_modify_completed_at(self):
        """Test that set_title() doesn't change completed_at."""
        self.task.mark_complete()
        original_completed = self.task.completed_at
        self.task.set_title("New title")
        self.assertEqual(self.task.completed_at, original_completed)

    def test_set_title_empty_string_raises_error(self):
        """Test that set_title() with empty string raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.task.set_title("")
        self.assertIn("Task title cannot be empty", str(context.exception))

    def test_set_title_whitespace_only_raises_error(self):
        """Test that set_title() with whitespace-only raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.task.set_title("   ")
        self.assertIn("Task title cannot be empty", str(context.exception))

    def test_set_title_none_raises_error(self):
        """Test that set_title() with None raises ValueError."""
        with self.assertRaises(ValueError):
            self.task.set_title(None)

    def test_set_description_updates_description(self):
        """Test that set_description() updates the description."""
        self.task.set_description("New description")
        self.assertEqual(self.task.description, "New description")

    def test_set_description_can_be_empty(self):
        """Test that set_description() can set empty string."""
        self.task.set_description("")
        self.assertEqual(self.task.description, "")

    def test_set_description_does_not_modify_other_attributes(self):
        """Test that set_description() doesn't change other attributes."""
        original_title = self.task.title
        original_status = self.task.status
        original_created = self.task.created_at
        self.task.set_description("New description")
        self.assertEqual(self.task.title, original_title)
        self.assertEqual(self.task.status, original_status)
        self.assertEqual(self.task.created_at, original_created)

    def test_multiple_updates_to_title(self):
        """Test updating title multiple times."""
        self.task.set_title("First update")
        self.assertEqual(self.task.title, "First update")
        self.task.set_title("Second update")
        self.assertEqual(self.task.title, "Second update")
        self.task.set_title("Third update")
        self.assertEqual(self.task.title, "Third update")


class TestTaskStringMethods(unittest.TestCase):
    """Test Task string representation methods."""

    def setUp(self):
        """Create a fresh task for each test."""
        self.task = Task("Test task", "Test description")
        self.task.id = 1

    def test_str_includes_id(self):
        """Test that __str__() includes task ID."""
        str_repr = str(self.task)
        self.assertIn("#1", str_repr)

    def test_str_includes_title(self):
        """Test that __str__() includes task title."""
        str_repr = str(self.task)
        self.assertIn("Test task", str_repr)

    def test_str_includes_status(self):
        """Test that __str__() includes task status."""
        str_repr = str(self.task)
        self.assertIn("pending", str_repr)

    def test_str_includes_created_at(self):
        """Test that __str__() includes created timestamp."""
        str_repr = str(self.task)
        self.assertIn("Created:", str_repr)

    def test_str_pending_task_format(self):
        """Test __str__() format for pending task."""
        str_repr = str(self.task)
        self.assertIn("[#1]", str_repr)
        self.assertIn("Test task", str_repr)
        self.assertIn("pending", str_repr)
        self.assertIn("Created:", str_repr)

    def test_str_complete_task_includes_completed_at(self):
        """Test that __str__() includes completion timestamp for complete tasks."""
        self.task.mark_complete()
        str_repr = str(self.task)
        self.assertIn("Completed:", str_repr)

    def test_str_complete_task_format(self):
        """Test __str__() format for complete task."""
        self.task.mark_complete()
        str_repr = str(self.task)
        self.assertIn("[#1]", str_repr)
        self.assertIn("Test task", str_repr)
        self.assertIn("complete", str_repr)
        self.assertIn("Created:", str_repr)
        self.assertIn("Completed:", str_repr)

    def test_repr_format(self):
        """Test __repr__() format."""
        repr_str = repr(self.task)
        self.assertIn("Task(", repr_str)
        self.assertIn("id=1", repr_str)
        self.assertIn("title=", repr_str)
        self.assertIn("status=", repr_str)

    def test_repr_includes_id(self):
        """Test that __repr__() includes task ID."""
        repr_str = repr(self.task)
        self.assertIn("id=1", repr_str)

    def test_repr_includes_title_quoted(self):
        """Test that __repr__() includes title with quotes."""
        repr_str = repr(self.task)
        self.assertIn("'Test task'", repr_str)

    def test_repr_includes_status_quoted(self):
        """Test that __repr__() includes status with quotes."""
        repr_str = repr(self.task)
        self.assertIn("'pending'", repr_str)

    def test_str_with_none_id(self):
        """Test __str__() when ID is None."""
        task = Task("Task")
        str_repr = str(task)
        self.assertIn("[#None]", str_repr)


class TestTaskEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def test_task_with_very_long_title(self):
        """Test creating task with very long title."""
        long_title = "a" * 500
        task = Task(long_title)
        self.assertEqual(task.title, long_title)

    def test_task_with_special_characters_in_title(self):
        """Test task with special characters in title."""
        task = Task("Buy milk & eggs @ store #5!")
        self.assertEqual(task.title, "Buy milk & eggs @ store #5!")

    def test_task_with_unicode_characters(self):
        """Test task with Unicode characters."""
        task = Task("买菜 🛒 生菜")
        self.assertEqual(task.title, "买菜 🛒 生菜")

    def test_task_with_newlines_in_description(self):
        """Test task with newlines in description."""
        desc = "Line 1\nLine 2\nLine 3"
        task = Task("Task", desc)
        self.assertEqual(task.description, desc)

    def test_multiple_status_changes(self):
        """Test changing status many times."""
        task = Task("Task")
        for i in range(10):
            if i % 2 == 0:
                task.mark_complete()
                self.assertTrue(task.is_complete())
            else:
                task.mark_incomplete()
                self.assertTrue(task.is_pending())

    def test_task_created_at_before_modified_at(self):
        """Test that created_at is before any modifications."""
        import time
        task = Task("Task")
        created_time = task.created_at
        time.sleep(0.01)  # Small delay
        task.mark_complete()
        self.assertLess(created_time, task.completed_at)


if __name__ == "__main__":
    unittest.main()
