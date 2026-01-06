# Component Contract: Task Model

**Location**: `src/models/task.py`
**Responsibility**: Data structure and validation for individual task objects
**Dependencies**: Python standard library (datetime)

---

## Class: Task

### Purpose
Represents a single todo item with validation, status tracking, and timestamp management.

### Constructor

```python
def __init__(self, title: str, description: str = "") -> None
```

**Contract**:
- **Inputs**:
  - `title` (str, required): The task title/heading
  - `description` (str, optional): Additional task details; defaults to ""

- **Processing**:
  1. Validate title is not empty after stripping whitespace
  2. If title is invalid, raise ValueError with message
  3. Set created_at to current datetime (using datetime.now())
  4. Initialize status to "pending"
  5. Initialize completed_at to None
  6. Store title (after stripping leading/trailing whitespace)
  7. Store description as-is

- **Outputs**:
  - Returns self (Task instance)
  - Side effect: Instance attributes set

- **Success Behavior**:
  - Task created with all attributes initialized
  - Task ready for immediate use

- **Error Cases**:
  - **Empty title**: raise ValueError("Task title cannot be empty")
  - **None title**: raise ValueError("Task title cannot be empty")
  - **Title is whitespace only**: raise ValueError("Task title cannot be empty")

**Example**:
```python
# Success case
task = Task("Buy groceries")
# task.id = None (will be set by TaskManager)
# task.title = "Buy groceries"
# task.description = ""
# task.status = "pending"
# task.created_at = datetime(2026, 1, 1, 10, 0, 0)
# task.completed_at = None

# Error case
task = Task("")  # ValueError: Task title cannot be empty
task = Task("   ")  # ValueError: Task title cannot be empty
```

---

## Method: mark_complete()

```python
def mark_complete(self) -> None
```

**Contract**:
- **Inputs**: None (operates on self)

- **Processing**:
  1. Set status to "complete"
  2. Set completed_at to current datetime

- **Outputs**: None
  - Side effect: Instance attributes modified

- **Success Behavior**:
  - Task status changes to "complete"
  - completed_at timestamp recorded

- **Error Cases**:
  - None (idempotent; safe to call multiple times)

**Example**:
```python
task = Task("Buy groceries")
# Before: status="pending", completed_at=None
task.mark_complete()
# After: status="complete", completed_at=datetime(2026, 1, 1, 10, 5, 30)
task.mark_complete()  # Safe to call again; no change
```

---

## Method: mark_incomplete()

```python
def mark_incomplete(self) -> None
```

**Contract**:
- **Inputs**: None (operates on self)

- **Processing**:
  1. Set status to "pending"
  2. Clear completed_at (set to None)

- **Outputs**: None
  - Side effect: Instance attributes modified

- **Success Behavior**:
  - Task status changes to "pending"
  - completed_at timestamp removed

- **Error Cases**:
  - None (idempotent; safe to call multiple times)

**Example**:
```python
task = Task("Buy groceries")
task.mark_complete()
# Before: status="complete", completed_at=datetime(...)
task.mark_incomplete()
# After: status="pending", completed_at=None
```

---

## Method: is_complete()

```python
def is_complete(self) -> bool
```

**Contract**:
- **Inputs**: None (operates on self)

- **Processing**:
  1. Check if status == "complete"

- **Outputs**: bool
  - True if complete, False otherwise

- **Success Behavior**:
  - Returns accurate status

- **Error Cases**:
  - None (always safe)

**Example**:
```python
task = Task("Buy groceries")
task.is_complete()  # Returns False
task.mark_complete()
task.is_complete()  # Returns True
```

---

## Method: is_pending()

```python
def is_pending(self) -> bool
```

**Contract**:
- **Inputs**: None (operates on self)

- **Processing**:
  1. Check if status == "pending"

- **Outputs**: bool
  - True if pending, False otherwise

- **Success Behavior**:
  - Returns accurate status

- **Error Cases**:
  - None (always safe)

**Example**:
```python
task = Task("Buy groceries")
task.is_pending()  # Returns True
task.mark_complete()
task.is_pending()  # Returns False
```

---

## Method: set_title()

```python
def set_title(self, new_title: str) -> None
```

**Contract**:
- **Inputs**:
  - `new_title` (str): New title for the task

- **Processing**:
  1. Validate new_title is not empty after stripping
  2. If invalid, raise ValueError
  3. Update self.title (after stripping)

- **Outputs**: None
  - Side effect: title attribute modified

- **Success Behavior**:
  - Title updated successfully
  - created_at and completed_at unchanged
  - status unchanged

- **Error Cases**:
  - **Empty title**: raise ValueError("Task title cannot be empty")
  - **Title is whitespace only**: raise ValueError("Task title cannot be empty")

**Example**:
```python
task = Task("Buy groceries")
original_created_at = task.created_at
task.set_title("Buy groceries and cook dinner")
# task.title changed
# task.created_at unchanged (still original_created_at)
task.set_title("")  # ValueError: Task title cannot be empty
```

---

## Method: set_description()

```python
def set_description(self, new_description: str) -> None
```

**Contract**:
- **Inputs**:
  - `new_description` (str): New description for the task

- **Processing**:
  1. Validate new_description (can be empty)
  2. Update self.description

- **Outputs**: None
  - Side effect: description attribute modified

- **Success Behavior**:
  - Description updated successfully
  - No timestamps modified

- **Error Cases**:
  - None (description can be empty)

**Example**:
```python
task = Task("Buy groceries")
task.set_description("tomatoes, lettuce, bread")
# task.description = "tomatoes, lettuce, bread"
task.set_description("")
# task.description = ""  (valid)
```

---

## Method: __str__()

```python
def __str__(self) -> str
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Format task as human-readable string
  2. Include ID, title, status, created_at
  3. Format dates as YYYY-MM-DD HH:MM:SS

- **Outputs**: str
  - Human-readable representation

- **Example Output**:
  ```
  [#1] Buy groceries (pending) - Created: 2026-01-01 10:00:00
  [#5] Schedule meeting (complete) - Created: 2026-01-01 10:15:00 - Completed: 2026-01-01 10:30:45
  ```

---

## Validation Rules Summary

| Rule | Input Example | Valid? | Reason |
|------|-------|--------|--------|
| Non-empty title | "Buy groceries" | ✅ | Contains text |
| Empty string title | "" | ❌ | Empty |
| Whitespace-only title | "   " | ❌ | No actual text |
| Valid with description | ("Task", "Details") | ✅ | Both valid |
| Empty description | ("Task", "") | ✅ | Description is optional |
| Title stripped | "  Task  " | ✅ | Stripped to "Task" |

---

## Implementation Notes

- Use `datetime.datetime.now()` for timestamps (local time, no timezone)
- Title should be stripped of leading/trailing whitespace in constructor and setter
- Description stored as-is (no automatic stripping)
- Status is set internally only (no public setter)
- ID is set externally by TaskManager (not in Task constructor)
- All methods should be fast (O(1) operations)

