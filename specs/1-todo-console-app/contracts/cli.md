# Component Contract: CLI (Command-Line Interface)

**Location**: `src/cli/main.py`
**Responsibility**: User interaction, menu navigation, input validation, and output formatting
**Dependencies**: TaskManager (src/services/task_manager.py)

---

## Module: CLI

### Purpose
Provides interactive console interface for todo management with menu-driven navigation and user-friendly prompts.

---

## Function: display_menu()

```python
def display_menu() -> None
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Clear screen (optional, for better UX)
  2. Print header/title
  3. Print numbered menu options (1-6)
  4. Print instructions

- **Outputs**: None (prints to console)

- **Output Format**:
```
=====================================
       TODO CONSOLE APPLICATION
=====================================
Choose an option:
1. Add a new task
2. View all tasks
3. Update a task
4. Delete a task
5. Mark task complete/incomplete
6. Exit application
-------------------------------------
Enter your choice (1-6):
```

---

## Function: get_menu_choice() -> int

```python
def get_menu_choice() -> int
```

**Contract**:
- **Inputs**: User input from console

- **Processing**:
  1. Prompt user: "Enter your choice (1-6): "
  2. Read user input
  3. Try to convert to integer
  4. Validate choice is in range 1-6
  5. If invalid, show error and loop
  6. If valid, return choice

- **Outputs**: int
  - Valid menu choice (1-6)

- **Success Behavior**:
  - Returns valid integer

- **Error Cases**:
  - **Non-numeric input**: Show "Invalid input. Please enter a number (1-6)."
  - **Out of range**: Show "Invalid choice. Please enter a number between 1 and 6."
  - **Loops until valid**: Keep prompting until user provides valid input

**Example**:
```
User enters: "abc"
Output: "Invalid input. Please enter a number (1-6)."
Prompts again...

User enters: "7"
Output: "Invalid choice. Please enter a number between 1 and 6."
Prompts again...

User enters: "3"
Returns: 3
```

---

## Function: handle_add_task(manager: TaskManager) -> None

```python
def handle_add_task(manager: TaskManager) -> None
```

**Contract**:
- **Inputs**:
  - `manager` (TaskManager): Task storage service

- **Processing**:
  1. Print header: "--- Add New Task ---"
  2. Prompt: "Enter task title: "
  3. Read user input (title)
  4. Prompt: "Enter description (optional, press Enter to skip): "
  5. Read user input (description)
  6. Try to create task via manager.add_task(title, description)
  7. If successful, show confirmation with task ID
  8. If error (invalid title), show error message and return

- **Outputs**: None (prints to console, modifies manager)

- **Success Output**:
```
--- Add New Task ---
Enter task title: Buy groceries
Enter description (optional, press Enter to skip): For Sunday dinner
✓ Task added successfully! (ID: 1)
```

- **Error Output**:
```
--- Add New Task ---
Enter task title:
Error: Task title cannot be empty. Please try again.
```

- **Error Cases**:
  - **Empty title**: Catch ValueError, show user-friendly message

---

## Function: handle_view_tasks(manager: TaskManager) -> None

```python
def handle_view_tasks(manager: TaskManager) -> None
```

**Contract**:
- **Inputs**:
  - `manager` (TaskManager): Task storage service

- **Processing**:
  1. Get all tasks from manager
  2. If no tasks, print "No tasks yet. Add one to get started!"
  3. If tasks exist:
     - Print header with task count
     - For each task, format and print:
       - ID, title, status, dates
     - Print summary (pending count, completed count)

- **Outputs**: None (prints to console)

- **Success Output (with tasks)**:
```
--- All Tasks (3 total) ---
[1] Buy groceries
    Status: pending
    Created: 2026-01-01 10:00:00

[2] Cook dinner
    Status: complete
    Created: 2026-01-01 10:15:00
    Completed: 2026-01-01 10:30:45

[3] Clean house
    Status: pending
    Created: 2026-01-01 10:45:00

Summary: 2 pending, 1 complete
```

- **Empty Output**:
```
--- All Tasks ---
No tasks yet. Add one to get started!
```

**Formatting Rules**:
- Task ID in brackets: [1]
- Indented details (4 spaces)
- Status clearly visible
- Dates in format: YYYY-MM-DD HH:MM:SS
- Completed timestamp shown only if complete
- Summary line shows pending/complete counts

---

## Function: handle_update_task(manager: TaskManager) -> None

```python
def handle_update_task(manager: TaskManager) -> None
```

**Contract**:
- **Inputs**:
  - `manager` (TaskManager): Task storage service

- **Processing**:
  1. Show all tasks (call handle_view_tasks)
  2. Prompt: "Enter task ID to update: "
  3. Validate ID exists (is_task_exists)
  4. If not found, show error and return
  5. Get task details
  6. Prompt: "Enter new title (or press Enter to keep current): "
  7. Read title (allow empty for no change)
  8. Prompt: "Enter new description (or press Enter to keep current): "
  9. Read description
  10. Call manager.update_task() with provided values
  11. Show confirmation

- **Outputs**: None (prints to console, modifies manager)

- **Success Output**:
```
--- All Tasks (2 total) ---
[1] Buy groceries
    Status: pending
    Created: 2026-01-01 10:00:00

[2] Cook dinner
    Status: pending
    Created: 2026-01-01 10:15:00

--- Update Task ---
Enter task ID to update: 1
Enter new title (or press Enter to keep current): Buy groceries and cook
Enter new description (or press Enter to keep current): For Sunday party
✓ Task updated successfully!
```

- **Error Output**:
```
--- Update Task ---
Enter task ID to update: 999
Error: Task not found.
```

- **Error Cases**:
  - **Invalid ID**: Show "Task not found"
  - **Empty title provided**: Show error and don't update
  - **Invalid input**: Handle gracefully

---

## Function: handle_delete_task(manager: TaskManager) -> None

```python
def handle_delete_task(manager: TaskManager) -> None
```

**Contract**:
- **Inputs**:
  - `manager` (TaskManager): Task storage service

- **Processing**:
  1. Show all tasks
  2. Prompt: "Enter task ID to delete: "
  3. Validate ID exists
  4. If not found, show error and return
  5. Get task for display
  6. Show confirmation prompt: "Are you sure you want to delete '[title]'? (yes/no): "
  7. Read confirmation
  8. If user confirms (case-insensitive "yes" or "y"):
     - Call manager.delete_task()
     - Show success message
  9. If user cancels (anything else):
     - Show "Deletion cancelled"

- **Outputs**: None (prints to console, modifies manager)

- **Success Output**:
```
--- All Tasks (2 total) ---
[1] Buy groceries...
[2] Cook dinner...

--- Delete Task ---
Enter task ID to delete: 1
Are you sure you want to delete 'Buy groceries'? (yes/no): yes
✓ Task deleted successfully!
```

- **Cancelled Output**:
```
--- Delete Task ---
Enter task ID to delete: 1
Are you sure you want to delete 'Buy groceries'? (yes/no): no
Deletion cancelled.
```

- **Error Cases**:
  - **Invalid ID**: Show error and return
  - **Confirmation prompt**: Loop if invalid input

---

## Function: handle_mark_complete(manager: TaskManager) -> None

```python
def handle_mark_complete(manager: TaskManager) -> None
```

**Contract**:
- **Inputs**:
  - `manager` (TaskManager): Task storage service

- **Processing**:
  1. Show all tasks (to help user choose)
  2. Prompt: "Enter task ID: "
  3. Validate ID exists
  4. Get task to check current status
  5. If already complete:
     - Prompt: "Task is already complete. Mark as incomplete? (yes/no): "
     - If yes, call manager.mark_task_incomplete()
     - If no, return
  6. If pending:
     - Call manager.mark_task_complete()
     - Show success message

- **Outputs**: None (prints to console, modifies manager)

- **Success Output (pending → complete)**:
```
--- All Tasks (2 total) ---
[1] Buy groceries...
[2] Cook dinner...

--- Mark Task Complete/Incomplete ---
Enter task ID: 1
✓ Task marked as complete!
```

- **Success Output (complete → pending)**:
```
--- Mark Task Complete/Incomplete ---
Enter task ID: 1
Task is already complete. Mark as incomplete? (yes/no): yes
✓ Task marked as incomplete!
```

- **Error Cases**:
  - **Invalid ID**: Show error and return
  - **Confirmation prompt errors**: Re-prompt

---

## Function: run_main_loop(manager: TaskManager) -> None

```python
def run_main_loop(manager: TaskManager) -> None
```

**Contract**:
- **Inputs**:
  - `manager` (TaskManager): Task storage service

- **Processing**:
  1. Loop forever until user chooses exit:
     - Display menu
     - Get user choice
     - Call appropriate handler based on choice:
       - 1: handle_add_task()
       - 2: handle_view_tasks()
       - 3: handle_update_task()
       - 4: handle_delete_task()
       - 5: handle_mark_complete()
       - 6: exit_application()
     - After operation, show separator and pause ("Press Enter to continue...")
     - Clear screen and redisplay menu

- **Outputs**: None (prints to console, runs indefinitely until exit)

- **Flow**:
```
Show menu → Get choice → Handle operation → Show pause → Repeat (until exit)
```

---

## Function: exit_application() -> None

```python
def exit_application() -> None
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Print goodbye message
  2. Print note about data loss (in-memory)
  3. Exit program (raise SystemExit or return from main)

- **Outputs**: None (prints to console and exits)

- **Output**:
```
=====================================
Thank you for using Todo App!
(Note: Your tasks are not saved as this is an in-memory application)
=====================================
```

---

## Function: main()

```python
def main() -> None
```

**Contract**:
- **Inputs**: None

- **Processing**:
  1. Create TaskManager instance
  2. Print welcome message
  3. Call run_main_loop(manager)

- **Outputs**: None

- **Output**:
```
=====================================
Welcome to Todo Console Application!
=====================================
[Starting menu loop...]
```

---

## Error Handling Strategy

| Error Type | Location | Handling | User Message |
|-----------|----------|----------|-------------|
| Invalid menu choice | get_menu_choice() | Validation loop | "Invalid choice. Please enter 1-6." |
| Empty title | handle_add_task() | Catch ValueError | "Task title cannot be empty." |
| Task not found | handle_update_task(), handle_delete_task() | Catch KeyError | "Task not found." |
| Invalid input (non-numeric) | get_task_id_input() | Catch ValueError | "Please enter a valid number." |
| Confirmation prompt | Various handlers | Validation loop | "Please enter 'yes' or 'no'." |

---

## User Experience Guidelines

1. **Clear Prompts**: Every prompt should be obvious what input is expected
2. **Confirmation**: Destructive operations (delete) require confirmation
3. **Feedback**: Every operation shows success or error clearly
4. **Context**: Show related data when needed (tasks list before update/delete)
5. **Navigation**: Always show how to return to menu
6. **Spacing**: Use blank lines to separate sections
7. **Formatting**: Use consistent indentation and alignment

---

## Implementation Notes

- Use try-except for all user input operations
- Validate all numeric inputs before passing to manager
- Don't show stack traces to users; use friendly error messages
- Optional: Add colors for better readability (not required for Phase I)
- Support case-insensitive confirmation inputs ("yes", "YES", "y", "Y")
- Handle CTRL+C gracefully (exit with message, not crash)
- All string inputs should be stripped of leading/trailing whitespace

