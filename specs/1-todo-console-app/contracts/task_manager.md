# Component Contract: TaskManager Service

**Location**: `src/services/task_manager.py`
**Responsibility**: In-memory storage, CRUD operations, and task list management
**Dependencies**: Task model (src/models/task.py)

---

## Class: TaskManager

### Purpose
Manages the collection of tasks, maintains ID uniqueness, and enforces data integrity through CRUD operations.

### Constructor

```python
def __init__(self) -> None
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Initialize empty task list (list)
  2. Initialize ID counter to 0

- **Outputs**: TaskManager instance
  - Empty, ready to add tasks

- **Example**:
```python
manager = TaskManager()
# manager.tasks = []
# manager._next_id = 0
```

---

## Method: add_task()

```python
def add_task(self, title: str, description: str = "") -> Task
```

**Contract**:
- **Inputs**:
  - `title` (str, required): Task title
  - `description` (str, optional): Task description

- **Processing**:
  1. Create new Task(title, description)
  2. If Task creation fails (ValueError), re-raise exception
  3. Increment _next_id
  4. Assign task.id = _next_id
  5. Append task to tasks list
  6. Return the task

- **Outputs**: Task
  - The newly created and stored task

- **Success Behavior**:
  - Task added to list with unique ID
  - Task is pending status
  - Timestamps recorded

- **Error Cases**:
  - **Empty title**: raise ValueError("Task title cannot be empty")
  - **Invalid description**: raise ValueError (from Task validation)

**Example**:
```python
manager = TaskManager()

task1 = manager.add_task("Buy groceries")
# task1.id = 1
# task1.title = "Buy groceries"
# task1.status = "pending"
# manager.tasks = [task1]

task2 = manager.add_task("Cook dinner", "Italian food")
# task2.id = 2
# manager.tasks = [task1, task2]

manager.add_task("")  # ValueError: Task title cannot be empty
```

---

## Method: get_all_tasks()

```python
def get_all_tasks(self) -> list[Task]
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Return copy of tasks list (or original; both acceptable)

- **Outputs**: list[Task]
  - All tasks in creation order

- **Success Behavior**:
  - Returns all tasks
  - Empty list if no tasks

- **Example**:
```python
manager = TaskManager()
manager.get_all_tasks()  # Returns []
manager.add_task("Task 1")
manager.add_task("Task 2")
manager.get_all_tasks()  # Returns [Task#1, Task#2]
```

---

## Method: get_task_by_id()

```python
def get_task_by_id(self, task_id: int) -> Task
```

**Contract**:
- **Inputs**:
  - `task_id` (int): ID of task to retrieve

- **Processing**:
  1. Search tasks list for task with matching ID
  2. If found, return task
  3. If not found, raise exception

- **Outputs**: Task
  - The task with matching ID

- **Success Behavior**:
  - Returns the task

- **Error Cases**:
  - **Task not found**: raise KeyError(f"Task with ID {task_id} not found")

**Example**:
```python
manager = TaskManager()
task = manager.add_task("Buy groceries")
manager.get_task_by_id(1)  # Returns task
manager.get_task_by_id(999)  # KeyError: Task with ID 999 not found
```

---

## Method: get_pending_tasks()

```python
def get_pending_tasks(self) -> list[Task]
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Filter tasks list for tasks with status="pending"
  2. Return filtered list in creation order

- **Outputs**: list[Task]
  - All pending tasks

- **Example**:
```python
manager = TaskManager()
t1 = manager.add_task("Task 1")
t2 = manager.add_task("Task 2")
t1.mark_complete()
manager.get_pending_tasks()  # Returns [t2]
manager.get_completed_tasks()  # Returns [t1]
```

---

## Method: get_completed_tasks()

```python
def get_completed_tasks(self) -> list[Task]
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Filter tasks list for tasks with status="complete"
  2. Return filtered list

- **Outputs**: list[Task]
  - All completed tasks

---

## Method: update_task()

```python
def update_task(
    self,
    task_id: int,
    title: str = None,
    description: str = None
) -> Task
```

**Contract**:
- **Inputs**:
  - `task_id` (int): ID of task to update
  - `title` (str, optional): New title; None means no change
  - `description` (str, optional): New description; None means no change

- **Processing**:
  1. Get task by ID (may raise KeyError)
  2. If title provided, call task.set_title(title)
  3. If description provided, call task.set_description(description)
  4. Return updated task

- **Outputs**: Task
  - The updated task

- **Success Behavior**:
  - Task properties updated
  - Status and timestamps unchanged (except if marked complete/incomplete)
  - Existing data preserved if not updated

- **Error Cases**:
  - **Task not found**: raise KeyError(f"Task with ID {task_id} not found")
  - **Invalid title**: raise ValueError("Task title cannot be empty")

**Example**:
```python
manager = TaskManager()
task = manager.add_task("Buy groceries")

# Update title only
manager.update_task(1, title="Buy groceries and cook")
# task.title changed, description unchanged

# Update description only
manager.update_task(1, description="for Sunday dinner")
# task.description changed, title unchanged

# Update both
manager.update_task(1, title="Prepare food", description="for party")

# Invalid update
manager.update_task(1, title="")  # ValueError
manager.update_task(999, title="something")  # KeyError
```

---

## Method: mark_task_complete()

```python
def mark_task_complete(self, task_id: int) -> Task
```

**Contract**:
- **Inputs**:
  - `task_id` (int): ID of task to mark complete

- **Processing**:
  1. Get task by ID (may raise KeyError)
  2. Call task.mark_complete()
  3. Return task

- **Outputs**: Task
  - The updated task

- **Error Cases**:
  - **Task not found**: raise KeyError(f"Task with ID {task_id} not found")

**Example**:
```python
manager = TaskManager()
task = manager.add_task("Buy groceries")
# task.status = "pending"
manager.mark_task_complete(1)
# task.status = "complete"
# task.completed_at = datetime(...)
```

---

## Method: mark_task_incomplete()

```python
def mark_task_incomplete(self, task_id: int) -> Task
```

**Contract**:
- **Inputs**:
  - `task_id` (int): ID of task to mark incomplete

- **Processing**:
  1. Get task by ID (may raise KeyError)
  2. Call task.mark_incomplete()
  3. Return task

- **Outputs**: Task
  - The updated task

- **Error Cases**:
  - **Task not found**: raise KeyError(f"Task with ID {task_id} not found")

---

## Method: delete_task()

```python
def delete_task(self, task_id: int) -> bool
```

**Contract**:
- **Inputs**:
  - `task_id` (int): ID of task to delete

- **Processing**:
  1. Find task with matching ID
  2. If found, remove from tasks list
  3. Return True
  4. If not found, raise KeyError

- **Outputs**: bool
  - True if deletion successful

- **Success Behavior**:
  - Task removed from list
  - ID is NOT reused (next_id continues incrementing)
  - Other tasks unaffected

- **Error Cases**:
  - **Task not found**: raise KeyError(f"Task with ID {task_id} not found")

**Example**:
```python
manager = TaskManager()
t1 = manager.add_task("Task 1")  # ID=1
t2 = manager.add_task("Task 2")  # ID=2
t3 = manager.add_task("Task 3")  # ID=3

manager.delete_task(2)
# tasks = [t1, t3]
# IDs are [1, 3] (2 is not reused)

t4 = manager.add_task("Task 4")
# t4.id = 4 (not 2)

manager.delete_task(999)  # KeyError
```

---

## Method: is_task_exists()

```python
def is_task_exists(self, task_id: int) -> bool
```

**Contract**:
- **Inputs**:
  - `task_id` (int): ID to check

- **Processing**:
  1. Check if task with ID exists in list

- **Outputs**: bool
  - True if exists, False otherwise

**Example**:
```python
manager = TaskManager()
manager.add_task("Task")  # ID=1
manager.is_task_exists(1)  # True
manager.is_task_exists(2)  # False
```

---

## Method: is_empty()

```python
def is_empty(self) -> bool
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Check if tasks list is empty

- **Outputs**: bool
  - True if no tasks, False otherwise

---

## Query Methods

### count_tasks()
```python
def count_tasks(self) -> int
```
Returns total number of tasks.

### count_pending()
```python
def count_pending(self) -> int
```
Returns count of pending tasks.

### count_completed()
```python
def count_completed(self) -> int
```
Returns count of completed tasks.

---

## Data Integrity Guarantees

- **ID Uniqueness**: Every task has unique ID; IDs never reused
- **State Consistency**: Tasks always in valid state (valid status, timestamps)
- **CRUD Integrity**: Operations maintain list consistency
- **Fail-Fast**: Invalid operations raise exceptions, don't corrupt state

---

## Implementation Notes

- Use a simple list for storage (acceptable for Phase I; can optimize later)
- ID counter (_next_id) starts at 0, increments to 1 for first task
- IDs never reset or reused
- All operations should handle KeyError for missing tasks
- Task validation is delegated to Task class
- Consider optional optimization: dictionary lookup by ID for faster searches (Phase II)

