# Phase 1: Data Model & Entities

**Date**: 2026-01-01
**Purpose**: Define data structures, validation rules, and relationships for the Todo application

---

## Entity: Task

### Overview
A Task represents a single todo item in the application. It contains all information needed to manage a user's work items.

### Attributes

| Attribute | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `id` | int | Yes | Unique, auto-generated, never reused | Unique identifier for the task, starting at 1 |
| `title` | str | Yes | Non-empty, max 500 chars | Name/heading of the task; what the user wants to do |
| `description` | str | No | Max 1000 chars | Additional details about the task; defaults to empty string |
| `status` | str | Yes | Must be "pending" or "complete" | Current state of the task |
| `created_at` | datetime | Yes | Auto-generated, read-only | Timestamp when task was created (local time) |
| `completed_at` | datetime | No | Set when status → "complete", null if pending | Timestamp when task was marked complete |

### Validation Rules

#### Title Validation
```
Rule: Title must not be empty after trimming whitespace
Input: "   " (spaces only)
Result: ValueError("Task title cannot be empty")
Example Valid: "Buy groceries", "Schedule meeting"
```

#### Description Validation
```
Rule: Description can be empty; if provided, must be string
Input: "" (empty)
Result: Valid (description = "")
Input: "Optional additional details"
Result: Valid (stored as-is)
```

#### Status Validation
```
Rule: Status must be exactly "pending" or "complete"
Input: "Pending" (wrong case)
Result: ValueError("Status must be 'pending' or 'complete'")
Input: "pending"
Result: Valid
```

#### Timestamp Handling
```
Rule: created_at is set automatically at Task creation
Rule: completed_at is only set when marking complete
Rule: completed_at is cleared when marking incomplete
Example:
  Task created: created_at = 2026-01-01 10:00:00, completed_at = None
  After marking complete: completed_at = 2026-01-01 10:05:30
  After marking incomplete: completed_at = None
```

### State Transitions

```
Task State Machine:

Initial State: "pending" (all new tasks start pending)

Transitions:
  pending → complete (when user marks complete)
  complete → pending (when user marks incomplete)

State Permanence:
  - Status cannot be null
  - Status can only be one of two values
  - No other states exist (in Phase I)
```

### Operations & Methods

#### Creation
```
Task(title: str, description: str = "")
  - Validates title (non-empty)
  - Validates description (if provided)
  - Sets created_at to current datetime
  - Sets status to "pending"
  - completed_at = None
  - Raises ValueError if validation fails
```

#### Status Updates
```
mark_complete()
  - Changes status to "complete"
  - Sets completed_at to current datetime
  - Returns self (for chaining)

mark_incomplete()
  - Changes status to "pending"
  - Clears completed_at (set to None)
  - Returns self (for chaining)

is_complete() -> bool
  - Returns True if status == "complete"
  - Returns False otherwise

is_pending() -> bool
  - Returns True if status == "pending"
  - Returns False otherwise
```

#### Property Updates
```
set_title(new_title: str)
  - Validates new title (non-empty)
  - Updates self.title
  - Does NOT change created_at
  - Raises ValueError if validation fails

set_description(new_description: str)
  - Validates new description (if provided)
  - Updates self.description
  - Does NOT change timestamps
  - Raises ValueError if validation fails
```

#### String Representation
```
__str__()
  - Returns human-readable format for display
  - Example: "[#3] Buy groceries (pending) - Created: 2026-01-01 10:00"

__repr__()
  - Returns debug format
  - Example: "Task(id=3, title='Buy groceries', status='pending')"
```

### Example Instances

```python
# Example 1: Newly created task
task1 = Task("Buy groceries")
# Output:
# {
#   id: 1,
#   title: "Buy groceries",
#   description: "",
#   status: "pending",
#   created_at: 2026-01-01 10:00:00,
#   completed_at: None
# }

# Example 2: Task with description
task2 = Task("Schedule meeting", "with John and Sarah about Q1 plans")
# Output:
# {
#   id: 2,
#   title: "Schedule meeting",
#   description: "with John and Sarah about Q1 plans",
#   status: "pending",
#   created_at: 2026-01-01 10:01:00,
#   completed_at: None
# }

# Example 3: After marking complete
task1.mark_complete()
# Output:
# {
#   id: 1,
#   title: "Buy groceries",
#   description: "",
#   status: "complete",
#   created_at: 2026-01-01 10:00:00,
#   completed_at: 2026-01-01 10:15:30
# }

# Example 4: After updating
task2.set_title("Schedule meeting with team")
# Output:
# {
#   id: 2,
#   title: "Schedule meeting with team",  # Updated
#   description: "with John and Sarah about Q1 plans",
#   status: "pending",  # Unchanged
#   created_at: 2026-01-01 10:01:00,  # Unchanged
#   completed_at: None  # Unchanged
# }
```

---

## Entity: TaskList (Storage)

### Overview
The TaskList manages the collection of all Task objects in memory. It provides CRUD operations and maintains data integrity.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tasks` | list[Task] | Ordered collection of all Task objects |
| `next_id` | int | Counter for generating unique IDs; always increments, never resets |

### Operations

#### Create
```
add_task(title: str, description: str = "") -> Task
  - Creates new Task with validated title
  - Assigns next available ID (from next_id counter)
  - Increments next_id
  - Appends Task to tasks list
  - Returns the created Task
  - Raises ValueError if title validation fails
```

#### Read
```
get_all_tasks() -> list[Task]
  - Returns a copy of all tasks in order of creation
  - If empty, return empty list

get_task_by_id(task_id: int) -> Task
  - Returns Task with matching ID
  - Raises KeyError/ValueError if task_id not found

get_pending_tasks() -> list[Task]
  - Returns all tasks with status="pending"
  - In creation order

get_completed_tasks() -> list[Task]
  - Returns all tasks with status="complete"
  - In completion order (or creation order)

count_tasks() -> int
  - Returns total number of tasks

count_pending() -> int
  - Returns number of pending tasks

count_completed() -> int
  - Returns number of completed tasks
```

#### Update
```
update_task(task_id: int, title: str = None, description: str = None) -> Task
  - Finds Task by ID
  - Updates title if provided (validates before update)
  - Updates description if provided (validates before update)
  - Does NOT modify status or timestamps
  - Returns updated Task
  - Raises KeyError if task not found
  - Raises ValueError if validation fails

mark_task_complete(task_id: int) -> Task
  - Finds Task by ID
  - Calls task.mark_complete()
  - Returns updated Task
  - Raises KeyError if task not found

mark_task_incomplete(task_id: int) -> Task
  - Finds Task by ID
  - Calls task.mark_incomplete()
  - Returns updated Task
  - Raises KeyError if task not found
```

#### Delete
```
delete_task(task_id: int) -> bool
  - Finds and removes Task with given ID
  - Does NOT reuse the ID (next_id continues incrementing)
  - Returns True if deletion successful
  - Returns False or raises KeyError if task not found
  - Does NOT reset IDs for remaining tasks
```

#### Integrity Methods
```
is_task_exists(task_id: int) -> bool
  - Returns True if task with ID exists
  - Returns False otherwise

is_empty() -> bool
  - Returns True if no tasks in list
  - Returns False if any tasks exist
```

### Example Operations

```python
# Example: Complete workflow
task_list = TaskList()

# Add tasks
t1 = task_list.add_task("Buy groceries")           # ID: 1
t2 = task_list.add_task("Cook dinner", "Italian food")  # ID: 2
t3 = task_list.add_task("Clean house")             # ID: 3

# Query
print(task_list.count_tasks())      # Output: 3
print(task_list.count_pending())    # Output: 3

# Update
task_list.update_task(1, title="Buy groceries and cook")

# Status change
task_list.mark_task_complete(1)
print(task_list.count_pending())    # Output: 2
print(task_list.count_completed())  # Output: 1

# Delete
task_list.delete_task(2)
print(task_list.count_tasks())      # Output: 2
print(task_list.get_all_tasks())    # [Task#1, Task#3]  (ID 2 removed)

# Try to add after deletion
t4 = task_list.add_task("New task")
print(t4.id)                        # Output: 4 (not reused 2)
```

---

## Error Handling & Edge Cases

### Validation Errors

| Scenario | Exception | Message |
|----------|-----------|---------|
| Empty title | `ValueError` | "Task title cannot be empty" |
| Title only whitespace | `ValueError` | "Task title cannot be empty" |
| Invalid status | `ValueError` | "Status must be 'pending' or 'complete'" |
| Task ID not found | `KeyError` | "Task with ID {id} not found" |
| Duplicate operation | N/A | None (idempotent - marking complete twice is safe) |

### Special Cases

```
Case 1: Empty task list
  get_all_tasks() → returns [] (empty list)

Case 2: Delete then add
  Task 1 created (ID=1) → Deleted → Task 2 created (ID=2) → Task 3 created (ID=3)
  get_all_tasks() → [Task#2, Task#3]

Case 3: Mark complete then incomplete
  task.mark_complete() → status="complete", completed_at=timestamp
  task.mark_incomplete() → status="pending", completed_at=None

Case 4: Very long title
  Task("x" * 500) → Valid (at 500 char limit)
  Task("x" * 501) → ValueError ("Title exceeds maximum length")
```

---

## Data Integrity Guarantees

- **ID Uniqueness**: Each task has unique ID; IDs never reused
- **Status Validity**: Task status always one of: pending, complete
- **Timestamp Consistency**: created_at never changes; completed_at only set when complete
- **No Orphans**: Deleted tasks completely removed; no dangling references
- **Validation at Creation**: Invalid data never enters storage (fail-fast)

---

## Relationships & Dependencies

```
TaskList (container)
  └─ Task (many)
     ├─ attributes (id, title, description, status, timestamps)
     └─ methods (mark_complete, mark_incomplete, is_complete, is_pending)

No circular dependencies.
No external entity references.
Self-contained data model.
```

---

## Ready for Phase 1: Contracts

The data model is complete and ready for detailed function/method contracts in the `/contracts/` directory.

