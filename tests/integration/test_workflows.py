"""
Integration tests for complete todo application workflows.

Tests cover end-to-end scenarios including:
- Adding tasks
- Viewing tasks
- Updating tasks
- Deleting tasks
- Marking tasks complete/incomplete
- Complex multi-operation workflows
"""

import unittest
from src.services.task_manager import TaskManager


class TestAddTaskWorkflow(unittest.TestCase):
    """Integration tests for adding tasks."""

    def setUp(self):
        """Create a fresh task manager for each test."""
        self.manager = TaskManager()

    def test_add_single_task(self):
        """Test adding a single task to an empty list."""
        task = self.manager.add_task("Buy groceries")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Buy groceries")
        self.assertEqual(task.status, "pending")
        self.assertEqual(self.manager.count_tasks(), 1)

    def test_add_task_with_description(self):
        """Test adding a task with both title and description."""
        task = self.manager.add_task("Cook dinner", "Italian pasta")
        self.assertEqual(task.title, "Cook dinner")
        self.assertEqual(task.description, "Italian pasta")
        self.assertIn(task, self.manager.get_all_tasks())

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks get sequential IDs."""
        t1 = self.manager.add_task("Task 1")
        t2 = self.manager.add_task("Task 2")
        t3 = self.manager.add_task("Task 3")

        self.assertEqual(t1.id, 1)
        self.assertEqual(t2.id, 2)
        self.assertEqual(t3.id, 3)
        self.assertEqual(self.manager.count_tasks(), 3)

    def test_added_tasks_appear_in_view(self):
        """Test that added tasks appear in the task list."""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")

        all_tasks = self.manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 2)
        titles = [t.title for t in all_tasks]
        self.assertIn("Task 1", titles)
        self.assertIn("Task 2", titles)

    def test_add_task_validation(self):
        """Test that invalid tasks are rejected."""
        with self.assertRaises(ValueError):
            self.manager.add_task("")

        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

        self.assertEqual(self.manager.count_tasks(), 0)


class TestViewTaskWorkflow(unittest.TestCase):
    """Integration tests for viewing tasks."""

    def setUp(self):
        """Create a manager with sample tasks."""
        self.manager = TaskManager()
        self.t1 = self.manager.add_task("Task 1")
        self.t2 = self.manager.add_task("Task 2", "Description")
        self.manager.mark_task_complete(1)

    def test_view_all_tasks(self):
        """Test viewing all tasks."""
        all_tasks = self.manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 2)

    def test_view_empty_list(self):
        """Test viewing an empty task list."""
        manager = TaskManager()
        all_tasks = manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 0)
        self.assertTrue(manager.is_empty())

    def test_view_pending_and_complete_tasks(self):
        """Test viewing pending and completed tasks separately."""
        pending = self.manager.get_pending_tasks()
        completed = self.manager.get_completed_tasks()

        self.assertEqual(len(pending), 1)
        self.assertEqual(len(completed), 1)
        self.assertEqual(pending[0].id, 2)
        self.assertEqual(completed[0].id, 1)

    def test_view_all_tasks_shows_correct_details(self):
        """Test that viewed tasks have all correct details."""
        all_tasks = self.manager.get_all_tasks()

        task1 = all_tasks[0]
        self.assertEqual(task1.id, 1)
        self.assertEqual(task1.title, "Task 1")
        self.assertEqual(task1.status, "complete")
        self.assertIsNotNone(task1.completed_at)

        task2 = all_tasks[1]
        self.assertEqual(task2.id, 2)
        self.assertEqual(task2.title, "Task 2")
        self.assertEqual(task2.description, "Description")
        self.assertEqual(task2.status, "pending")
        self.assertIsNone(task2.completed_at)


class TestUpdateTaskWorkflow(unittest.TestCase):
    """Integration tests for updating tasks."""

    def setUp(self):
        """Create a manager with a sample task."""
        self.manager = TaskManager()
        self.task = self.manager.add_task("Original Title", "Original Desc")

    def test_update_title_only(self):
        """Test updating only a task's title."""
        self.manager.update_task(1, title="New Title")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "New Title")
        self.assertEqual(task.description, "Original Desc")

    def test_update_description_only(self):
        """Test updating only a task's description."""
        self.manager.update_task(1, description="New Desc")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "Original Title")
        self.assertEqual(task.description, "New Desc")

    def test_update_both_title_and_description(self):
        """Test updating both title and description."""
        self.manager.update_task(1, title="New Title", description="New Desc")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.title, "New Title")
        self.assertEqual(task.description, "New Desc")

    def test_update_preserves_status(self):
        """Test that update doesn't change task status."""
        self.manager.mark_task_complete(1)
        self.manager.update_task(1, title="Updated Title")
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.status, "complete")

    def test_update_preserves_timestamps(self):
        """Test that update preserves creation and completion timestamps."""
        original_created = self.task.created_at
        self.manager.mark_task_complete(1)
        original_completed = self.task.completed_at

        self.manager.update_task(1, title="New Title")

        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.created_at, original_created)
        self.assertEqual(task.completed_at, original_completed)

    def test_update_nonexistent_task(self):
        """Test that updating nonexistent task raises error."""
        with self.assertRaises(KeyError):
            self.manager.update_task(999, title="New Title")

    def test_update_with_invalid_title(self):
        """Test that empty title is rejected."""
        with self.assertRaises(ValueError):
            self.manager.update_task(1, title="")


class TestDeleteTaskWorkflow(unittest.TestCase):
    """Integration tests for deleting tasks."""

    def setUp(self):
        """Create a manager with sample tasks."""
        self.manager = TaskManager()
        self.t1 = self.manager.add_task("Task 1")
        self.t2 = self.manager.add_task("Task 2")
        self.t3 = self.manager.add_task("Task 3")

    def test_delete_task(self):
        """Test deleting a task."""
        self.manager.delete_task(1)
        self.assertEqual(self.manager.count_tasks(), 2)
        self.assertFalse(self.manager.is_task_exists(1))

    def test_delete_task_preserves_other_tasks(self):
        """Test that deleting one task doesn't affect others."""
        self.manager.delete_task(2)
        self.assertTrue(self.manager.is_task_exists(1))
        self.assertFalse(self.manager.is_task_exists(2))
        self.assertTrue(self.manager.is_task_exists(3))

    def test_delete_does_not_reuse_ids(self):
        """Test that deleted IDs are not reused."""
        self.manager.delete_task(1)
        self.manager.delete_task(2)
        new_task = self.manager.add_task("New Task")
        self.assertEqual(new_task.id, 4)

    def test_delete_nonexistent_task(self):
        """Test that deleting nonexistent task raises error."""
        with self.assertRaises(KeyError):
            self.manager.delete_task(999)

    def test_delete_all_tasks(self):
        """Test deleting all tasks leaves empty list."""
        self.manager.delete_task(1)
        self.manager.delete_task(2)
        self.manager.delete_task(3)
        self.assertEqual(self.manager.count_tasks(), 0)
        self.assertTrue(self.manager.is_empty())

    def test_add_after_delete(self):
        """Test that adding tasks after deletion works correctly."""
        self.manager.delete_task(2)
        new_task = self.manager.add_task("New Task")
        self.assertEqual(new_task.id, 4)
        self.assertEqual(self.manager.count_tasks(), 3)


class TestMarkCompleteWorkflow(unittest.TestCase):
    """Integration tests for marking tasks complete/incomplete."""

    def setUp(self):
        """Create a manager with sample tasks."""
        self.manager = TaskManager()
        self.t1 = self.manager.add_task("Task 1")
        self.t2 = self.manager.add_task("Task 2")

    def test_mark_pending_task_complete(self):
        """Test marking a pending task as complete."""
        self.manager.mark_task_complete(1)
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.status, "complete")
        self.assertIsNotNone(task.completed_at)

    def test_mark_complete_task_incomplete(self):
        """Test marking a complete task back to pending."""
        self.manager.mark_task_complete(1)
        self.manager.mark_task_incomplete(1)
        task = self.manager.get_task_by_id(1)
        self.assertEqual(task.status, "pending")
        self.assertIsNone(task.completed_at)

    def test_toggle_completion_multiple_times(self):
        """Test toggling completion status multiple times."""
        task = self.manager.get_task_by_id(1)

        # Toggle 5 times
        for i in range(5):
            if i % 2 == 0:
                self.manager.mark_task_complete(1)
                self.assertEqual(task.status, "complete")
            else:
                self.manager.mark_task_incomplete(1)
                self.assertEqual(task.status, "pending")

    def test_mark_task_does_not_affect_others(self):
        """Test that marking one task doesn't affect others."""
        self.manager.mark_task_complete(1)
        task2 = self.manager.get_task_by_id(2)
        self.assertEqual(task2.status, "pending")

    def test_count_after_marking_complete(self):
        """Test that counts update correctly after marking complete."""
        self.assertEqual(self.manager.count_pending(), 2)
        self.assertEqual(self.manager.count_completed(), 0)

        self.manager.mark_task_complete(1)
        self.assertEqual(self.manager.count_pending(), 1)
        self.assertEqual(self.manager.count_completed(), 1)

        self.manager.mark_task_complete(2)
        self.assertEqual(self.manager.count_pending(), 0)
        self.assertEqual(self.manager.count_completed(), 2)

    def test_mark_nonexistent_task(self):
        """Test that marking nonexistent task raises error."""
        with self.assertRaises(KeyError):
            self.manager.mark_task_complete(999)


class TestComplexWorkflow(unittest.TestCase):
    """Integration tests for complex multi-operation workflows."""

    def test_complete_user_workflow(self):
        """Test a complete workflow: add, view, update, complete, delete."""
        manager = TaskManager()

        # Add tasks
        t1 = manager.add_task("Buy groceries")
        t2 = manager.add_task("Cook dinner", "Italian pasta")
        t3 = manager.add_task("Clean house")
        self.assertEqual(manager.count_tasks(), 3)

        # View all
        all_tasks = manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 3)

        # Update task 2
        manager.update_task(2, title="Cook Italian dinner")
        task2 = manager.get_task_by_id(2)
        self.assertEqual(task2.title, "Cook Italian dinner")

        # Mark task 1 complete
        manager.mark_task_complete(1)
        self.assertEqual(manager.count_completed(), 1)
        self.assertEqual(manager.count_pending(), 2)

        # Delete task 3
        manager.delete_task(3)
        self.assertEqual(manager.count_tasks(), 2)

        # Add new task (ID should be 4)
        t4 = manager.add_task("New task")
        self.assertEqual(t4.id, 4)

        # Verify final state
        self.assertEqual(manager.count_tasks(), 3)
        self.assertEqual(manager.count_pending(), 2)
        self.assertEqual(manager.count_completed(), 1)

    def test_large_dataset_operations(self):
        """Test operations on a large dataset (100 tasks)."""
        manager = TaskManager()

        # Add 100 tasks
        for i in range(100):
            manager.add_task(f"Task {i+1}")

        self.assertEqual(manager.count_tasks(), 100)

        # Mark 50 as complete
        for i in range(1, 51):
            manager.mark_task_complete(i)

        self.assertEqual(manager.count_pending(), 50)
        self.assertEqual(manager.count_completed(), 50)

        # Update some
        for i in range(10, 20):
            manager.update_task(i, title=f"Updated Task {i}")

        # Delete some
        for i in range(1, 11):
            manager.delete_task(i)

        self.assertEqual(manager.count_tasks(), 90)
        self.assertEqual(manager.count_completed(), 40)

    def test_empty_to_full_to_empty_workflow(self):
        """Test workflow from empty to full to empty again."""
        manager = TaskManager()

        # Start empty
        self.assertTrue(manager.is_empty())
        self.assertEqual(manager.count_tasks(), 0)

        # Add tasks
        for i in range(5):
            manager.add_task(f"Task {i+1}")

        self.assertFalse(manager.is_empty())
        self.assertEqual(manager.count_tasks(), 5)

        # Delete all
        for i in range(1, 6):
            manager.delete_task(i)

        self.assertTrue(manager.is_empty())
        self.assertEqual(manager.count_tasks(), 0)

    def test_operation_sequence_maintains_integrity(self):
        """Test that complex operation sequences maintain data integrity."""
        manager = TaskManager()

        # Create tasks
        t1 = manager.add_task("Task 1")
        t2 = manager.add_task("Task 2")
        t3 = manager.add_task("Task 3")

        # Perform mixed operations
        manager.mark_task_complete(1)
        manager.update_task(2, title="Updated Task 2")
        manager.delete_task(3)
        t4 = manager.add_task("Task 4")
        manager.mark_task_complete(2)
        manager.mark_task_incomplete(1)

        # Verify integrity
        all_tasks = manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 3)

        task_ids = sorted([t.id for t in all_tasks])
        self.assertEqual(task_ids, [1, 2, 4])

        # After operations:
        # Task 1: marked complete, then incomplete -> pending
        # Task 2: updated, then marked complete -> complete
        # Task 4: added as pending -> pending
        # Result: 2 pending, 1 complete
        self.assertEqual(manager.count_pending(), 2)
        self.assertEqual(manager.count_completed(), 1)

        # Verify individual states
        self.assertEqual(manager.get_task_by_id(1).status, "pending")
        self.assertEqual(manager.get_task_by_id(2).status, "complete")
        self.assertEqual(manager.get_task_by_id(4).status, "pending")


if __name__ == "__main__":
    unittest.main()
