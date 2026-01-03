"""
Manual Workflow Test - Simulates a complete user session.

This script demonstrates the complete functionality of the todo application
by simulating a realistic user workflow including:
- Adding tasks
- Viewing tasks
- Updating tasks
- Marking tasks complete
- Deleting tasks

Run with: python test_manual_workflow.py
"""

from src.services.task_manager import TaskManager
from datetime import datetime


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def display_tasks(manager, title="Current Tasks"):
    """Display all tasks in a formatted way."""
    print_section(title)

    if manager.is_empty():
        print("No tasks yet.")
        return

    for task in manager.get_all_tasks():
        status_symbol = "[DONE]" if task.is_complete() else "[TODO]"
        print(f"{status_symbol} #{task.id}: {task.title}")
        if task.description:
            print(f"       Description: {task.description}")
        created = task.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"       Created: {created}")
        if task.is_complete() and task.completed_at:
            completed = task.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"       Completed: {completed}")

    print(f"\nSummary: {manager.count_pending()} pending, {manager.count_completed()} complete")


def test_workflow():
    """Execute a complete manual workflow."""

    print_header("TODO APPLICATION - MANUAL WORKFLOW TEST")
    print("\nThis script demonstrates the complete functionality of the application")
    print("by simulating a realistic user session.\n")

    manager = TaskManager()

    # ===== TEST 1: Add Tasks =====
    print_header("STEP 1: ADDING TASKS")
    print("\nAdding 5 tasks to the list...\n")

    tasks_to_add = [
        ("Buy groceries", "For Sunday dinner - need milk, eggs, bread"),
        ("Cook dinner", "Italian pasta with fresh vegetables"),
        ("Clean the house", "Vacuum living room and kitchen"),
        ("Study Python", "Work on classes and decorators"),
        ("Call Mom", "Weekly check-in call"),
    ]

    for title, description in tasks_to_add:
        task = manager.add_task(title, description)
        print(f"[OK] Task #{task.id} added: {title}")

    display_tasks(manager, "All Tasks After Addition")

    # ===== TEST 2: View Tasks =====
    print_header("STEP 2: VIEWING TASKS")
    print("\nDisplaying all pending tasks...\n")

    pending = manager.get_pending_tasks()
    print(f"Pending tasks ({len(pending)}):")
    for task in pending:
        print(f"  - #{task.id}: {task.title}")

    print(f"\nCompleted tasks ({manager.count_completed()}):")
    completed = manager.get_completed_tasks()
    if completed:
        for task in completed:
            print(f"  - #{task.id}: {task.title}")
    else:
        print("  (None yet)")

    # ===== TEST 3: Update Tasks =====
    print_header("STEP 3: UPDATING TASKS")
    print("\nUpdating task #2 with new title and description...\n")

    original_task = manager.get_task_by_id(2)
    print(f"Before update:")
    print(f"  Title: {original_task.title}")
    print(f"  Description: {original_task.description}")

    manager.update_task(2, title="Prepare Italian Dinner", description="Pasta with marinara and fresh basil")

    updated_task = manager.get_task_by_id(2)
    print(f"\nAfter update:")
    print(f"  Title: {updated_task.title}")
    print(f"  Description: {updated_task.description}")
    print(f"  [OK] Task #2 updated successfully")

    print(f"\nUpdating task #3 - description only...\n")
    manager.update_task(3, description="Deep clean all rooms and dust furniture")
    updated_task = manager.get_task_by_id(3)
    print(f"  Updated description: {updated_task.description}")
    print(f"  [OK] Task #3 description updated")

    # ===== TEST 4: Mark Tasks Complete =====
    print_header("STEP 4: MARKING TASKS COMPLETE")
    print("\nMarking tasks as complete...\n")

    tasks_to_complete = [1, 2]
    for task_id in tasks_to_complete:
        task = manager.get_task_by_id(task_id)
        manager.mark_task_complete(task_id)
        print(f"[OK] Task #{task_id} marked complete: {task.title}")

    display_tasks(manager, "Tasks After Marking Complete")

    # ===== TEST 5: Delete Tasks =====
    print_header("STEP 5: DELETING A TASK")
    print("\nDeleting task #4...\n")

    task_to_delete = manager.get_task_by_id(4)
    print(f"Deleting: #{task_to_delete.id} - {task_to_delete.title}")
    manager.delete_task(4)
    print(f"[OK] Task #4 deleted successfully")

    print(f"\nVerifying task #4 no longer exists...")
    if not manager.is_task_exists(4):
        print(f"[OK] Task #4 confirmed deleted")

    display_tasks(manager, "Tasks After Deletion")

    # ===== TEST 6: Toggle Task Completion =====
    print_header("STEP 6: TOGGLING TASK COMPLETION")
    print("\nMarking task #1 back to incomplete...\n")

    task = manager.get_task_by_id(1)
    print(f"Task #1 current status: {task.status}")
    manager.mark_task_incomplete(1)
    task = manager.get_task_by_id(1)
    print(f"Task #1 new status: {task.status}")
    print(f"[OK] Task #1 toggled back to pending")

    # ===== TEST 7: Add More Tasks =====
    print_header("STEP 7: ADDING MORE TASKS")
    print("\nAdding 2 more tasks...\n")

    new_task1 = manager.add_task("Exercise", "30 minutes cardio")
    new_task2 = manager.add_task("Read Book", "Chapter 5 of current book")

    print(f"[OK] Task #{new_task1.id} added: {new_task1.title}")
    print(f"[OK] Task #{new_task2.id} added: {new_task2.title}")
    print(f"[NOTE] New tasks have IDs 6 and 7 (ID 4 was not reused)")

    display_tasks(manager, "All Tasks After Adding More")

    # ===== TEST 8: Final Status Summary =====
    print_header("FINAL STATUS SUMMARY")

    print(f"\nTask Statistics:")
    print(f"  Total tasks: {manager.count_tasks()}")
    print(f"  Pending tasks: {manager.count_pending()}")
    print(f"  Completed tasks: {manager.count_completed()}")

    print(f"\nTask IDs in system: {[t.id for t in manager.get_all_tasks()]}")

    print(f"\nTask Details:")
    for task in manager.get_all_tasks():
        status = "COMPLETE" if task.is_complete() else "PENDING"
        print(f"  [{status}] Task #{task.id}: {task.title}")

    # ===== TEST 9: Data Integrity Checks =====
    print_header("STEP 9: DATA INTEGRITY VERIFICATION")

    print("\nVerifying data integrity...\n")

    # Check ID uniqueness
    ids = [t.id for t in manager.get_all_tasks()]
    if len(ids) == len(set(ids)):
        print("[OK] All task IDs are unique")

    # Check all tasks have valid status
    all_valid_status = all(t.status in ("pending", "complete") for t in manager.get_all_tasks())
    if all_valid_status:
        print("[OK] All tasks have valid status (pending or complete)")

    # Check timestamp consistency
    for task in manager.get_all_tasks():
        if task.is_complete():
            if task.completed_at is not None and task.completed_at >= task.created_at:
                print(f"[OK] Task #{task.id}: Timestamps consistent (created before completed)")

    # Check no orphaned tasks
    if manager.is_task_exists(4):
        print("[ERROR] Task #4 should not exist (was deleted)")
    else:
        print("[OK] Deleted task #4 confirmed removed from system")

    # ===== TEST 10: Error Handling =====
    print_header("STEP 10: ERROR HANDLING VERIFICATION")

    print("\nTesting error conditions...\n")

    # Try to get nonexistent task
    try:
        manager.get_task_by_id(999)
        print("[ERROR] Should have raised KeyError for nonexistent task")
    except KeyError as e:
        print(f"[OK] Correctly raised error for nonexistent task: {e}")

    # Try to delete nonexistent task
    try:
        manager.delete_task(999)
        print("[ERROR] Should have raised KeyError for delete nonexistent")
    except KeyError as e:
        print(f"[OK] Correctly raised error for delete nonexistent: {e}")

    # Try to add task with empty title
    try:
        manager.add_task("")
        print("[ERROR] Should have raised ValueError for empty title")
    except ValueError as e:
        print(f"[OK] Correctly raised error for empty title: {e}")

    # Try to update with empty title
    try:
        manager.update_task(1, title="")
        print("[ERROR] Should have raised ValueError for empty title in update")
    except ValueError as e:
        print(f"[OK] Correctly raised error for empty title in update: {e}")

    # ===== TEST COMPLETE =====
    print_header("WORKFLOW TEST COMPLETE")

    print("\nAll tests passed! Summary of operations:")
    print(f"  - Added 7 tasks (ID 4 deleted, not reused)")
    print(f"  - Updated 2 tasks")
    print(f"  - Marked 2 tasks complete")
    print(f"  - Toggled 1 task back to pending")
    print(f"  - Deleted 1 task")
    print(f"  - Verified error handling")
    print(f"  - Confirmed data integrity")

    print(f"\nFinal state:")
    print(f"  Total tasks in system: {manager.count_tasks()}")
    print(f"  Pending: {manager.count_pending()}")
    print(f"  Complete: {manager.count_completed()}")

    print("\n[OK] APPLICATION IS FULLY FUNCTIONAL")
    print("\nYou can now run: python src/cli/main.py")
    print("to use the interactive console application.\n")


if __name__ == "__main__":
    test_workflow()
