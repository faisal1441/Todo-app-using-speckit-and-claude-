# Python Todo Console Application

A beginner-friendly todo application built with Python that allows users to manage tasks through a simple command-line interface. Tasks are automatically saved to a JSON file for persistence across sessions.

## Features

- **Add Tasks**: Create new tasks with titles and optional descriptions
- **View Tasks**: Display all tasks with status, creation date, and completion information
- **Update Tasks**: Modify task titles and descriptions
- **Delete Tasks**: Remove tasks from the list with confirmation
- **Mark Complete**: Track task progress by marking tasks as complete or incomplete
- **File Persistence**: Tasks are automatically saved to `tasks.json` after each operation

## Quick Start

### Prerequisites

- Python 3.8 or higher
- No external dependencies required (uses Python standard library only)

### Installation

1. Clone or download the project:
```bash
cd Todoapp
```

2. Ensure the project structure is created:
```bash
# Already set up, but the structure should be:
src/
├── models/
├── services/
└── cli/
tests/
├── unit/
└── integration/
```

### Running the Application

```bash
python src/cli/main.py
```

The application will start with a menu interface:

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

## Usage Guide

### Adding a Task

1. Select option 1 from the menu
2. Enter the task title (required)
3. Enter a description (optional, press Enter to skip)
4. Task is created with a unique ID

Example:
```
--- Add New Task ---
Enter task title: Buy groceries
Enter description (optional, press Enter to skip): For Sunday dinner
✓ Task added successfully! (ID: 1)
```

### Viewing Tasks

1. Select option 2 from the menu
2. All tasks are displayed with:
   - Task ID and title
   - Current status (pending/complete)
   - Creation date and time
   - Completion date/time (if completed)

Example:
```
--- All Tasks (2 total) ---
[#1] Buy groceries
    Status: pending
    Created: 2026-01-01 10:00:00

[#2] Cook dinner
    Status: complete
    Created: 2026-01-01 10:15:00
    Completed: 2026-01-01 10:30:45

Summary: 1 pending, 1 complete
```

### Updating a Task

1. Select option 3 from the menu
2. View current tasks
3. Enter the task ID to update
4. Enter new title (or press Enter to keep current)
5. Enter new description (or press Enter to keep current)
6. Task is updated successfully

### Deleting a Task

1. Select option 4 from the menu
2. View current tasks
3. Enter the task ID to delete
4. Confirm deletion (yes/no prompt)
5. Task is removed from the list

### Marking Tasks Complete

1. Select option 5 from the menu
2. View current tasks
3. Enter the task ID
4. If pending: marks as complete (sets completion date)
5. If complete: prompts to mark as incomplete

## Project Structure

```
Todoapp/
├── src/                          # Source code
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Task data model
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_manager.py      # Task storage and CRUD
│   └── cli/
│       ├── __init__.py
│       └── main.py              # Command-line interface
├── tests/                        # Test suite
│   ├── unit/                    # Component tests
│   │   ├── test_task.py
│   │   └── test_task_manager.py
│   └── integration/             # Workflow tests
│       ├── test_add_task.py
│       ├── test_view_tasks.py
│       ├── test_update_task.py
│       ├── test_delete_task.py
│       ├── test_mark_complete.py
│       └── test_complete_workflow.py
├── specs/                        # Specification documents
│   └── 1-todo-console-app/
│       ├── spec.md              # Feature specification
│       ├── plan.md              # Implementation plan
│       ├── research.md          # Design decisions
│       ├── data-model.md        # Data structure design
│       ├── quickstart.md        # Implementation guide
│       ├── tasks.md             # Task breakdown
│       └── contracts/           # Component contracts
├── README.md                     # This file
└── .gitignore                    # Git ignore rules
```

## Architecture

### Models Layer (src/models/)

**Task Class**: Represents a single todo item with:
- Unique ID (auto-assigned)
- Title (required)
- Description (optional)
- Status (pending or complete)
- Created timestamp
- Completed timestamp (when marked complete)

Methods:
- `mark_complete()`: Change status to complete
- `mark_incomplete()`: Change status to pending
- `is_complete()`: Check if complete
- `is_pending()`: Check if pending
- `set_title()`: Update title
- `set_description()`: Update description

### Services Layer (src/services/)

**TaskManager Class**: Manages in-memory task storage with:
- CRUD operations (create, read, update, delete)
- Query methods (get all, filter by status)
- ID management (unique, never reused)
- Data integrity validation

Methods:
- `add_task(title, description)`: Create new task
- `get_task_by_id(id)`: Retrieve specific task
- `update_task(id, title, description)`: Modify task
- `delete_task(id)`: Remove task
- `get_all_tasks()`: Get all tasks
- `get_pending_tasks()`: Filter pending tasks
- `get_completed_tasks()`: Filter completed tasks
- `mark_task_complete(id)`: Mark as done
- `mark_task_incomplete(id)`: Mark as pending

### CLI Layer (src/cli/)

**Main Module**: Provides user interface with:
- Menu-driven navigation
- Input validation
- Error handling
- User-friendly messages
- Operation handlers for each feature

## Running Tests

### Run All Tests

```bash
python -m unittest discover tests -v
```

### Run Unit Tests Only

```bash
python -m unittest discover tests/unit -v
```

### Run Integration Tests Only

```bash
python -m unittest discover tests/integration -v
```

### Run Specific Test File

```bash
python -m unittest tests.unit.test_task -v
```

### Run Specific Test

```bash
python -m unittest tests.unit.test_task.TestTask.test_create_task_with_title -v
```

## Error Handling

The application handles various error cases gracefully:

| Error | User Message | Recovery |
|-------|--------------|----------|
| Empty title | "Task title cannot be empty" | Prompt to enter valid title |
| Non-existent task ID | "Task not found" | Show current tasks and retry |
| Invalid menu choice | "Invalid choice. Please enter 1-6" | Reprompt for valid choice |
| Non-numeric ID input | "Please enter a valid number" | Reprompt for numeric input |

## Data Integrity

The application ensures:
- **Unique IDs**: Every task has a unique ID, never reused
- **Valid Status**: Tasks can only be "pending" or "complete"
- **Timestamp Consistency**: Creation dates never change; completion dates only set when complete
- **Fail-Fast Validation**: Invalid data is rejected at creation time
- **No Orphans**: Deleted tasks completely removed; no dangling references

## Data Persistence

Tasks are automatically saved to `tasks.json` in the project directory after each operation:

- **Auto-Save**: Changes are saved immediately after add, update, delete, or mark complete
- **File Format**: Human-readable JSON with clear structure
- **Error Recovery**: Corrupted files are backed up and a fresh file is created
- **Optional**: Application can run in pure in-memory mode (no file I/O)

### Backup and Recovery

If `tasks.json` becomes corrupted, the application will:
1. Create a backup file named `tasks.json.corrupt.TIMESTAMP`
2. Start fresh with an empty task list
3. Display a warning message

## Known Limitations

- **Single User**: Not designed for multi-user or concurrent access
- **No Networking**: Console-based, local execution only
- **Console UI Only**: Text-based interface, no graphical UI
- **No Authentication**: No user login or security features

## Implementation Notes

### For Developers

- **Language**: Python 3.8+
- **Testing**: unittest (standard library)
- **Code Style**: PEP 8 compliant
- **Documentation**: Docstrings for all public classes and methods

### Development Workflow

1. Write tests first (TDD approach)
2. Implement feature to pass tests
3. Refactor for clarity
4. Document any non-obvious behavior
5. Run full test suite before committing

### Code Quality

- All code is beginner-friendly and well-commented
- Each component has a single responsibility
- No circular dependencies
- Comprehensive error handling
- Extensive test coverage

## Future Enhancements (Phase II+)

Potential improvements for future versions:

- **Database Integration**: Use SQLite or PostgreSQL for advanced persistence
- **Enhanced CLI**: Color output, better formatting, progress indicators
- **Tags/Categories**: Organize tasks by tags or projects
- **Due Dates**: Add task deadlines and reminders
- **Priority Levels**: Task priority indicators
- **Search/Filter**: Find tasks by keyword or criteria
- **Undo/Redo**: Revert recent changes
- **Web Interface**: Browser-based UI
- **Multi-User**: Shared task lists with user accounts
- **CSV Export**: Export tasks to spreadsheet format
- **Cloud Sync**: Synchronize tasks across devices

## Contributing

To contribute to this project:

1. Follow the specification in `specs/1-todo-console-app/spec.md`
2. Write tests before implementing features
3. Ensure all tests pass
4. Follow PEP 8 code style
5. Document your changes

## License

This project is provided as-is for educational purposes.

## Support

For issues, questions, or suggestions:

1. Check the specification: `specs/1-todo-console-app/spec.md`
2. Review the implementation plan: `specs/1-todo-console-app/plan.md`
3. Consult the quickstart guide: `specs/1-todo-console-app/quickstart.md`

## Changelog

### Version 1.1.0 (Current)

- **NEW**: File persistence - tasks automatically saved to `tasks.json`
- **NEW**: 86 new tests for persistence layer (serialization, file I/O, workflows)
- Improved error recovery (backup corrupt files, graceful fallbacks)
- Updated CLI messages to reflect persistence
- Total test coverage: 225 tests (139 existing + 86 new)
- Backward compatible: in-memory mode still available

### Version 1.0.0

- Initial release
- Implements 5 core features (Add, View, Update, Delete, Mark Complete)
- In-memory storage
- Console-based UI
- Comprehensive test coverage (139 tests)
- Full specification and documentation

---

**Happy task managing!** 🚀
