# Phase 1: Quick Start Implementation Guide

**Date**: 2026-01-01
**Purpose**: Quick reference for implementing the Todo Console App from spec and design

---

## Implementation Overview

This guide provides a quick reference for implementing the In-Memory Python Todo Console App based on the specification and design documents.

### Implementation Order (Recommended)

1. **Models Layer** (src/models/task.py)
   - Define Task class
   - Implement validation
   - Add status management methods

2. **Services Layer** (src/services/task_manager.py)
   - Define TaskManager class
   - Implement CRUD operations
   - Implement query methods

3. **CLI Layer** (src/cli/main.py)
   - Define menu display
   - Implement input handlers
   - Create main loop

4. **Tests** (tests/)
   - Unit tests for Task
   - Unit tests for TaskManager
   - Integration tests for workflows

5. **Documentation** (README, code comments)
   - Add docstrings to classes/methods
   - Document edge cases
   - Provide usage examples

---

## Project Structure Setup

```bash
# Create directories
mkdir -p src/models
mkdir -p src/services
mkdir -p src/cli
mkdir -p tests/unit
mkdir -p tests/integration

# Create files (use templates below)
touch src/__init__.py
touch src/models/__init__.py
touch src/models/task.py
touch src/services/__init__.py
touch src/services/task_manager.py
touch src/cli/__init__.py
touch src/cli/main.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

---

## Module 1: Task Model (src/models/task.py)

### Key Implementation Details

**Imports**:
```python
from datetime import datetime
```

**Class Structure**:
- Constructor: `__init__(title: str, description: str = "")`
- Status methods: `mark_complete()`, `mark_incomplete()`, `is_complete()`, `is_pending()`
- Property setters: `set_title(new_title: str)`, `set_description(new_description: str)`
- String methods: `__str__()`, `__repr__()`

**Validation Rules**:
- Title: Strip whitespace, non-empty
- Description: Optional, can be empty
- Status: Only "pending" or "complete"
- Timestamps: Auto-generated, read-only from outside class

**Key Attributes**:
```python
self.id = None  # Set by TaskManager
self.title = title.strip()  # Stripped title
self.description = description  # As-is
self.status = "pending"  # Default
self.created_at = datetime.now()  # Auto
self.completed_at = None  # Until marked complete
```

**Validation in Constructor**:
```python
if not title.strip():
    raise ValueError("Task title cannot be empty")
```

### Quick Test Example

```python
# Should pass
task = Task("Buy groceries")
assert task.title == "Buy groceries"
assert task.status == "pending"
assert task.created_at is not None
assert task.completed_at is None

# Should fail
task = Task("")  # ValueError
task = Task("   ")  # ValueError
```

---

## Module 2: TaskManager Service (src/services/task_manager.py)

### Key Implementation Details

**Imports**:
```python
from src.models.task import Task
```

**Class Structure**:
- Constructor: `__init__()`
- CRUD: `add_task()`, `get_task_by_id()`, `update_task()`, `delete_task()`
- Query: `get_all_tasks()`, `get_pending_tasks()`, `get_completed_tasks()`
- Check: `is_task_exists()`, `is_empty()`
- Count: `count_tasks()`, `count_pending()`, `count_completed()`

**Key Attributes**:
```python
self.tasks = []  # List of Task objects
self._next_id = 0  # ID counter
```

**ID Management**:
```python
def add_task(self, title: str, description: str = "") -> Task:
    task = Task(title, description)
    self._next_id += 1
    task.id = self._next_id
    self.tasks.append(task)
    return task
```

**Finding Tasks**:
```python
def get_task_by_id(self, task_id: int) -> Task:
    for task in self.tasks:
        if task.id == task_id:
            return task
    raise KeyError(f"Task with ID {task_id} not found")
```

**Error Handling**:
- Raise `KeyError` for missing tasks
- Let Task class handle ValueError for validation
- Never corrupt internal state on error

### Quick Test Example

```python
manager = TaskManager()

# Add tasks
task1 = manager.add_task("Task 1")
task2 = manager.add_task("Task 2", "Description")
assert task1.id == 1
assert task2.id == 2

# Query
assert manager.count_tasks() == 2
assert manager.count_pending() == 2

# Update
manager.mark_task_complete(1)
assert manager.count_pending() == 1
assert manager.count_completed() == 1

# Delete
manager.delete_task(1)
assert manager.count_tasks() == 1
assert not manager.is_task_exists(1)
```

---

## Module 3: CLI Interface (src/cli/main.py)

### Key Implementation Details

**Imports**:
```python
from src.services.task_manager import TaskManager
```

**Main Functions**:
1. `display_menu()` - Print menu options
2. `get_menu_choice()` - Get and validate user choice
3. `handle_add_task(manager)` - Add task
4. `handle_view_tasks(manager)` - Display tasks
5. `handle_update_task(manager)` - Update task
6. `handle_delete_task(manager)` - Delete task
7. `handle_mark_complete(manager)` - Toggle completion
8. `run_main_loop(manager)` - Main event loop
9. `main()` - Entry point

**Menu Loop Structure**:
```python
def run_main_loop(manager: TaskManager) -> None:
    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_task(manager)
        elif choice == 2:
            handle_view_tasks(manager)
        elif choice == 3:
            handle_update_task(manager)
        elif choice == 4:
            handle_delete_task(manager)
        elif choice == 5:
            handle_mark_complete(manager)
        elif choice == 6:
            exit_application()
            break

        input("\nPress Enter to continue...")
```

**Input Validation Pattern**:
```python
def get_menu_choice() -> int:
    while True:
        try:
            choice = int(input("Enter your choice (1-6): "))
            if 1 <= choice <= 6:
                return choice
            print("Invalid choice. Please enter 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
```

**Output Formatting**:
```python
def display_menu() -> None:
    print("\n" + "="*40)
    print("  TODO CONSOLE APPLICATION")
    print("="*40)
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. Update a task")
    print("4. Delete a task")
    print("5. Mark task complete/incomplete")
    print("6. Exit application")
    print("-"*40)
```

**Task Display Format**:
```python
def display_task(task: Task) -> str:
    result = f"[#{task.id}] {task.title}\n"
    result += f"    Status: {task.status}\n"
    result += f"    Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    if task.completed_at:
        result += f"    Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    if task.description:
        result += f"    Description: {task.description}\n"
    return result
```

### Quick Start: Running the App

```python
if __name__ == "__main__":
    main()
```

Then run:
```bash
python src/cli/main.py
```

---

## Testing Strategy

### Unit Tests: Task Model (tests/unit/test_task.py)

```python
import unittest
from src.models.task import Task

class TestTask(unittest.TestCase):
    def test_create_task_with_title(self):
        task = Task("Buy groceries")
        self.assertEqual(task.title, "Buy groceries")
        self.assertEqual(task.status, "pending")
        self.assertIsNone(task.completed_at)

    def test_create_task_empty_title_fails(self):
        with self.assertRaises(ValueError):
            Task("")
        with self.assertRaises(ValueError):
            Task("   ")

    def test_mark_complete(self):
        task = Task("Test task")
        task.mark_complete()
        self.assertEqual(task.status, "complete")
        self.assertIsNotNone(task.completed_at)

    def test_set_title(self):
        task = Task("Original")
        task.set_title("Updated")
        self.assertEqual(task.title, "Updated")

    def test_set_title_empty_fails(self):
        task = Task("Original")
        with self.assertRaises(ValueError):
            task.set_title("")
```

### Unit Tests: TaskManager (tests/unit/test_task_manager.py)

```python
import unittest
from src.services.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()

    def test_add_task(self):
        task = self.manager.add_task("Test")
        self.assertEqual(task.id, 1)
        self.assertEqual(self.manager.count_tasks(), 1)

    def test_get_task_by_id(self):
        task = self.manager.add_task("Test")
        retrieved = self.manager.get_task_by_id(1)
        self.assertEqual(retrieved.id, task.id)

    def test_get_task_not_found(self):
        with self.assertRaises(KeyError):
            self.manager.get_task_by_id(999)

    def test_delete_task(self):
        self.manager.add_task("Test")
        self.manager.delete_task(1)
        self.assertEqual(self.manager.count_tasks(), 0)

    def test_id_never_reused(self):
        t1 = self.manager.add_task("Task 1")
        self.manager.delete_task(1)
        t2 = self.manager.add_task("Task 2")
        self.assertEqual(t2.id, 2)  # Not 1
```

### Integration Tests (tests/integration/test_workflows.py)

```python
import unittest
from src.services.task_manager import TaskManager

class TestWorkflows(unittest.TestCase):
    def test_add_view_update_complete_delete(self):
        manager = TaskManager()

        # Add
        task = manager.add_task("Buy groceries")
        self.assertEqual(manager.count_tasks(), 1)

        # Update
        manager.update_task(1, title="Buy groceries and cook")

        # Mark complete
        manager.mark_task_complete(1)
        self.assertEqual(manager.count_completed(), 1)

        # Delete
        manager.delete_task(1)
        self.assertEqual(manager.count_tasks(), 0)
```

---

## Run Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.unit.test_task

# Run specific test class
python -m unittest tests.unit.test_task.TestTask

# Run specific test method
python -m unittest tests.unit.test_task.TestTask.test_create_task_with_title

# Verbose output
python -m unittest discover tests -v
```

---

## Key Implementation Checklist

- [ ] Task model with validation
- [ ] TaskManager with CRUD operations
- [ ] CLI menu system
- [ ] CLI input handlers (all 5 operations)
- [ ] Error handling and messages
- [ ] Unit tests for Task
- [ ] Unit tests for TaskManager
- [ ] Integration tests
- [ ] All tests passing
- [ ] Code documented with docstrings
- [ ] Edge cases handled
- [ ] User-friendly error messages

---

## Common Pitfalls to Avoid

1. **Task IDs**: Don't reuse IDs after deletion; increment counter continuously
2. **Empty titles**: Always validate in Task constructor
3. **Status validation**: Enforce "pending" or "complete" only
4. **Timestamp handling**: Don't modify created_at; only set completed_at when marking complete
5. **Error messages**: Make them user-friendly, not technical
6. **Input validation**: Validate at every CLI input point
7. **State consistency**: Ensure no operation can corrupt manager state
8. **Tests**: Write tests before implementation (TDD)

---

## Next Steps After Implementation

1. Run full test suite and fix any failures
2. Run the application and verify user experience
3. Test edge cases manually
4. Get feedback from users
5. Document any non-obvious behaviors
6. Consider Phase II enhancements (file persistence, better UI, etc.)

