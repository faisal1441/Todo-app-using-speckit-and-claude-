#!/usr/bin/env python3
"""
Manual persistence test - simulates user workflow to verify persistence.

Tests:
1. Create new manager with persistence (creates tasks.json)
2. Add tasks
3. Verify tasks.json contains the tasks
4. Create new manager from same file
5. Verify tasks are loaded correctly
"""

import json
import os
from src.services.task_manager import TaskManager

print("\n" + "=" * 60)
print("PERSISTENCE MANUAL TEST")
print("=" * 60)

# Clean up any existing file
tasks_file = "tasks.json"
if os.path.exists(tasks_file):
    os.remove(tasks_file)
    print(f"[OK] Cleaned up existing {tasks_file}")

print("\n--- Session 1: Create and save tasks ---\n")

# Session 1: Create manager with persistence
manager1 = TaskManager(persistence_file=tasks_file)
print(f"[OK] Created TaskManager with persistence to: {tasks_file}")

# Add some tasks
task1 = manager1.add_task("Buy groceries", "For Sunday dinner")
print(f"[OK] Added task {task1.id}: {task1.title}")

task2 = manager1.add_task("Cook pasta", "Italian pasta with fresh basil")
print(f"[OK] Added task {task2.id}: {task2.title}")

task3 = manager1.add_task("Clean house")
print(f"[OK] Added task {task3.id}: {task3.title}")

# Mark one complete
manager1.mark_task_complete(1)
print(f"[OK] Marked task 1 as complete")

# Verify file exists
if os.path.exists(tasks_file):
    print(f"[OK] File '{tasks_file}' created successfully")

    # Check file contents
    with open(tasks_file, 'r') as f:
        data = json.load(f)

    print(f"[OK] File contains {len(data['tasks'])} tasks")
    print(f"[OK] next_id counter is: {data['next_id']}")

    # Display file contents
    print(f"\n--- File Contents ({tasks_file}) ---\n")
    print(json.dumps(data, indent=2)[:500] + "...\n")
else:
    print(f"[ERROR] File '{tasks_file}' was not created!")
    exit(1)

print("\n--- Session 2: Load from file ---\n")

# Session 2: Create new manager and load from file
manager2 = TaskManager(persistence_file=tasks_file)
print(f"[OK] Created new TaskManager and loaded from: {tasks_file}")

# Verify tasks loaded
loaded_count = manager2.count_tasks()
print(f"[OK] Loaded {loaded_count} tasks from file")

if loaded_count != 3:
    print(f"[ERROR] Expected 3 tasks, but loaded {loaded_count}")
    exit(1)

# Verify task details
all_tasks = manager2.get_all_tasks()
print(f"\n--- Loaded Tasks ---\n")
for task in all_tasks:
    status = "COMPLETE" if task.is_complete() else "PENDING"
    print(f"  [{status}] #{task.id}: {task.title}")
    if task.description:
        print(f"           {task.description}")

# Verify counts
print(f"\n[OK] Task summary:")
print(f"  - Total: {manager2.count_tasks()}")
print(f"  - Pending: {manager2.count_pending()}")
print(f"  - Completed: {manager2.count_completed()}")

# Verify specific task details
task1_loaded = manager2.get_task_by_id(1)
if task1_loaded.status != "complete":
    print(f"[ERROR] Task 1 should be complete!")
    exit(1)

if task1_loaded.completed_at is None:
    print(f"[ERROR] Task 1 should have completed_at timestamp!")
    exit(1)

print(f"[OK] Task 1 completion timestamp preserved: {task1_loaded.completed_at}")

print("\n--- Session 3: Modify and verify update ---\n")

# Update a task
manager2.update_task(2, title="Cook delicious pasta")
print(f"[OK] Updated task 2 title")

# Add new task
task4 = manager2.add_task("Go shopping", "Buy new shoes")
print(f"[OK] Added task {task4.id}: {task4.title}")

# Verify file updated
with open(tasks_file, 'r') as f:
    data = json.load(f)

if data['next_id'] != 4:
    print(f"[ERROR] next_id should be 4, but is {data['next_id']}")
    exit(1)

print(f"[OK] File updated correctly (next_id = {data['next_id']})")

print("\n--- Session 4: Verify all data persists ---\n")

# Create one more manager to verify
manager3 = TaskManager(persistence_file=tasks_file)

# Verify all data
if manager3.count_tasks() != 4:
    print(f"[ERROR] Expected 4 tasks, got {manager3.count_tasks()}")
    exit(1)

task2_final = manager3.get_task_by_id(2)
if task2_final.title != "Cook delicious pasta":
    print(f"[ERROR] Task 2 title not updated!")
    exit(1)

task4_final = manager3.get_task_by_id(4)
if task4_final.title != "Go shopping":
    print(f"[ERROR] Task 4 not found!")
    exit(1)

print(f"[OK] All data persisted correctly across 3 sessions!")

print("\n" + "=" * 60)
print("SUCCESS: Persistence feature is working correctly!")
print("=" * 60 + "\n")

# Show final file
print("Final tasks.json content:\n")
with open(tasks_file, 'r') as f:
    content = f.read()
print(content)
