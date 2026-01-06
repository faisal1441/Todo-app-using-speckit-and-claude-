# Implementation Tasks: In-Memory Python Todo Console App

**Branch**: `1-todo-console-app` | **Date**: 2026-01-01
**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Quickstart**: [quickstart.md](./quickstart.md)

---

## Implementation Strategy

This task list follows a **Test-Driven Development (TDD)** approach with tasks organized by user story priority. Each user story is independently testable and can be completed in parallel where dependencies allow.

### MVP Scope (Phase 1-2)
- **Phase 1**: Project setup and foundational infrastructure
- **Phase 2**: Task model and TaskManager service (shared by all user stories)
- **User Stories 1-2 (P1)**: Add and View features (core MVP)

### Full Scope (Phase 3-5)
- **User Stories 3-5 (P2)**: Update, Delete, and Mark Complete features (secondary features)

### Parallel Execution Opportunities
- **Models & Services** (Phase 2) can be completed in parallel with **CLI setup** (early Phase 3)
- **Unit tests** for each module can be written in parallel as modules are implemented
- **User Stories 3-5** (Phase 4-5) can be worked on in parallel (independent operations)

---

## Phase 1: Project Setup

**Goal**: Initialize project structure, create base directories, and set up development environment

### Project Structure

- [ ] T001 Create project directory structure: `src/models/`, `src/services/`, `src/cli/`, `tests/unit/`, `tests/integration/`
- [ ] T002 Create `src/__init__.py` file
- [ ] T003 Create `src/models/__init__.py` file
- [ ] T004 Create `src/services/__init__.py` file
- [ ] T005 Create `src/cli/__init__.py` file
- [ ] T006 Create `tests/__init__.py` file
- [ ] T007 Create `tests/unit/__init__.py` file
- [ ] T008 Create `tests/integration/__init__.py` file
- [ ] T009 Create `README.md` with project overview and quick start instructions
- [ ] T010 Create `.gitignore` file with Python-specific exclusions

---

## Phase 2: Foundational Components (Blocking Prerequisites)

**Goal**: Build core models and services that all user stories depend on

### Task Model (src/models/task.py)

*Blocking for: All user stories*

- [ ] T011 [P] Implement Task class constructor with title validation in `src/models/task.py`
  - Required inputs: title (str), description (str, default="")
  - Validates: title is non-empty after stripping
  - Sets: id=None (will be set by TaskManager), status="pending", created_at=datetime.now(), completed_at=None
  - Raises: ValueError for empty title

- [ ] T012 [P] Implement Task status methods in `src/models/task.py`
  - mark_complete(): Sets status to "complete", sets completed_at to datetime.now()
  - mark_incomplete(): Sets status to "pending", clears completed_at (set to None)
  - is_complete(): Returns True if status == "complete"
  - is_pending(): Returns True if status == "pending"

- [ ] T013 [P] Implement Task property setters in `src/models/task.py`
  - set_title(new_title: str): Validates and updates title, raises ValueError if empty
  - set_description(new_description: str): Updates description (no validation needed)

- [ ] T014 [P] Implement Task string methods in `src/models/task.py`
  - __str__(): Returns human-readable format "[#id] title (status) - Created: timestamp"
  - __repr__(): Returns debug format "Task(id=..., title=..., status=...)"

### TaskManager Service (src/services/task_manager.py)

*Blocking for: All user stories*

- [ ] T015 [P] Implement TaskManager constructor in `src/services/task_manager.py`
  - Initialize empty tasks list
  - Initialize _next_id counter to 0

- [ ] T016 [P] Implement TaskManager.add_task() in `src/services/task_manager.py`
  - Input: title (str), description (str, default="")
  - Creates Task object (may raise ValueError if invalid)
  - Increments _next_id
  - Assigns task.id = _next_id
  - Appends to tasks list
  - Returns: Task object

- [ ] T017 [P] Implement TaskManager.get_task_by_id() in `src/services/task_manager.py`
  - Input: task_id (int)
  - Returns: Task object matching ID
  - Raises: KeyError if not found

- [ ] T018 [P] Implement TaskManager query methods in `src/services/task_manager.py`
  - get_all_tasks(): Returns list of all tasks
  - get_pending_tasks(): Returns list of pending tasks
  - get_completed_tasks(): Returns list of completed tasks
  - count_tasks(): Returns total count
  - count_pending(): Returns pending count
  - count_completed(): Returns completed count

- [ ] T019 [P] Implement TaskManager.update_task() in `src/services/task_manager.py`
  - Input: task_id (int), title (str, optional), description (str, optional)
  - Finds task by ID (raises KeyError if not found)
  - Calls set_title() and/or set_description() on task
  - Returns: Updated Task object

- [ ] T020 [P] Implement TaskManager.delete_task() in `src/services/task_manager.py`
  - Input: task_id (int)
  - Removes task from list
  - Does NOT reuse IDs (next_id continues incrementing)
  - Returns: True
  - Raises: KeyError if not found

- [ ] T021 [P] Implement TaskManager.mark_task_complete() in `src/services/task_manager.py`
  - Input: task_id (int)
  - Calls task.mark_complete()
  - Returns: Updated Task object
  - Raises: KeyError if not found

- [ ] T022 [P] Implement TaskManager.mark_task_incomplete() in `src/services/task_manager.py`
  - Input: task_id (int)
  - Calls task.mark_incomplete()
  - Returns: Updated Task object
  - Raises: KeyError if not found

- [ ] T023 [P] Implement TaskManager utility methods in `src/services/task_manager.py`
  - is_task_exists(task_id): Returns bool
  - is_empty(): Returns bool

### Unit Tests for Task Model

*Blocking for: Phase 3 (validates foundational layer)*

- [ ] T024 [P] Create unit tests for Task constructor in `tests/unit/test_task.py`
  - Test: Task created with valid title
  - Test: Task created with title and description
  - Test: Task creation fails with empty title
  - Test: Task creation fails with whitespace-only title
  - Test: Task status defaults to "pending"
  - Test: Task created_at is set to current datetime
  - Test: Task completed_at is initially None

- [ ] T025 [P] Create unit tests for Task status methods in `tests/unit/test_task.py`
  - Test: mark_complete() sets status to "complete" and sets completed_at
  - Test: mark_incomplete() sets status to "pending" and clears completed_at
  - Test: is_complete() returns True when complete
  - Test: is_pending() returns True when pending
  - Test: Idempotence - marking complete twice is safe

- [ ] T026 [P] Create unit tests for Task setters in `tests/unit/test_task.py`
  - Test: set_title() updates title
  - Test: set_title() fails with empty title
  - Test: set_title() does not modify created_at
  - Test: set_description() updates description
  - Test: set_description() can clear description (empty string)

### Unit Tests for TaskManager

*Blocking for: Phase 3 (validates foundational layer)*

- [ ] T027 [P] Create unit tests for TaskManager CRUD in `tests/unit/test_task_manager.py`
  - Test: add_task() creates task with unique ID
  - Test: add_task() rejects empty title
  - Test: get_task_by_id() returns correct task
  - Test: get_task_by_id() raises KeyError for missing task
  - Test: delete_task() removes task
  - Test: delete_task() does not reuse IDs
  - Test: IDs are never reused after deletion

- [ ] T028 [P] Create unit tests for TaskManager query methods in `tests/unit/test_task_manager.py`
  - Test: get_all_tasks() returns all tasks
  - Test: get_pending_tasks() returns only pending tasks
  - Test: get_completed_tasks() returns only completed tasks
  - Test: count methods return accurate counts
  - Test: Query methods return empty lists when no tasks exist

- [ ] T029 [P] Create unit tests for TaskManager state methods in `tests/unit/test_task_manager.py`
  - Test: is_task_exists() returns correct boolean
  - Test: is_empty() returns correct boolean

---

## Phase 3: User Story 1 - Add a New Task (P1)

**Goal**: Users can add new tasks with titles and optional descriptions

**Independent Test Criteria**:
- Create a task with title only
- Create a task with title and description
- Verify task appears in list with unique ID
- Verify empty title is rejected with error message

### CLI Add Handler

- [ ] T030 [US1] Implement display_menu() function in `src/cli/main.py`
  - Print formatted menu with 6 options (1-6)
  - Options: Add, View, Update, Delete, Mark Complete, Exit
  - Uses separators for readability

- [ ] T031 [US1] Implement get_menu_choice() function in `src/cli/main.py`
  - Prompts user for menu choice
  - Validates input is integer 1-6
  - Loops on invalid input with error message
  - Returns: integer choice

- [ ] T032 [US1] Implement handle_add_task(manager) in `src/cli/main.py`
  - Print "--- Add New Task ---" header
  - Prompt: "Enter task title: "
  - Prompt: "Enter description (optional, press Enter to skip): "
  - Call manager.add_task(title, description)
  - If successful: Print "✓ Task added successfully! (ID: {id})"
  - If error (ValueError): Print "Error: Task title cannot be empty"
  - Handle KeyboardInterrupt gracefully

### Integration Tests for User Story 1

- [ ] T033 [US1] Create integration test for add task workflow in `tests/integration/test_add_task.py`
  - Test: Add single task with title only
  - Test: Add task with title and description
  - Test: Add multiple tasks get sequential IDs
  - Test: Added tasks appear in get_all_tasks()
  - Test: Empty title raises ValueError

---

## Phase 3: User Story 2 - View All Tasks (P1)

**Goal**: Users can view all tasks with status and creation information

**Independent Test Criteria**:
- View empty task list (shows "No tasks yet" message)
- View list with multiple tasks (shows all details)
- Tasks display ID, title, status, and created timestamp
- Completed tasks show completion timestamp

### CLI View Handler

- [ ] T034 [US2] Implement handle_view_tasks(manager) in `src/cli/main.py`
  - Print "--- All Tasks (count) ---" header
  - If no tasks: Print "No tasks yet. Add one to get started!"
  - If tasks exist:
    - For each task, print: "[#id] title\n    Status: status\n    Created: timestamp"
    - If completed, also print: "    Completed: timestamp"
    - Print summary: "Summary: X pending, Y complete"
  - Format dates as YYYY-MM-DD HH:MM:SS

### Integration Tests for User Story 2

- [ ] T035 [US2] Create integration test for view task workflow in `tests/integration/test_view_tasks.py`
  - Test: View empty list
  - Test: View list with multiple tasks
  - Test: View shows pending and completed tasks with different formatting
  - Test: View shows all task details (ID, title, status, dates)

---

## Phase 4: User Story 3 - Update a Task (P2)

**Goal**: Users can modify existing task titles and descriptions

**Independent Test Criteria**:
- Update task title only (description unchanged)
- Update description only (title unchanged)
- Update both title and description
- Attempt to update non-existent task shows error
- Empty title is rejected with error

### CLI Update Handler

- [ ] T036 [US3] Implement handle_update_task(manager) in `src/cli/main.py`
  - Call handle_view_tasks(manager) to show current list
  - Prompt: "Enter task ID to update: "
  - Validate ID exists (use is_task_exists()), show error if not
  - Prompt: "Enter new title (or press Enter to keep current): "
  - Prompt: "Enter new description (or press Enter to keep current): "
  - Call manager.update_task(id, title, description) (only pass non-empty values)
  - If successful: Print "✓ Task updated successfully!"
  - If error (KeyError): Print "Error: Task not found"
  - If error (ValueError): Print "Error: Task title cannot be empty"

### Integration Tests for User Story 3

- [ ] T037 [US3] Create integration test for update task workflow in `tests/integration/test_update_task.py`
  - Test: Update title only
  - Test: Update description only
  - Test: Update both title and description
  - Test: Update preserves created_at timestamp
  - Test: Update non-existent task shows error
  - Test: Empty title update is rejected

---

## Phase 4: User Story 4 - Delete a Task (P2)

**Goal**: Users can remove tasks from the list with confirmation

**Independent Test Criteria**:
- Delete task removes it from list
- Delete shows confirmation prompt
- Confirm delete removes task
- Cancel delete keeps task
- Delete non-existent task shows error
- Remaining tasks keep original IDs (no renumbering)

### CLI Delete Handler

- [ ] T038 [US4] Implement handle_delete_task(manager) in `src/cli/main.py`
  - Call handle_view_tasks(manager) to show current list
  - Prompt: "Enter task ID to delete: "
  - Validate ID exists, show error if not
  - Get task and display: "Are you sure you want to delete '[title]'? (yes/no): "
  - If user confirms (yes/y case-insensitive):
    - Call manager.delete_task(id)
    - Print "✓ Task deleted successfully!"
  - If user cancels (anything else):
    - Print "Deletion cancelled"
  - If error (KeyError): Print "Error: Task not found"

### Integration Tests for User Story 4

- [ ] T039 [US4] Create integration test for delete task workflow in `tests/integration/test_delete_task.py`
  - Test: Delete task removes it from list
  - Test: Delete preserves other tasks and their IDs
  - Test: Deleted task ID is not reused
  - Test: Delete non-existent task shows error
  - Test: Confirmation prompt cancels deletion

---

## Phase 5: User Story 5 - Mark Task as Complete (P2)

**Goal**: Users can mark tasks complete/incomplete to track progress

**Independent Test Criteria**:
- Mark pending task as complete (status changes, completed_at set)
- Mark complete task as incomplete (status changes, completed_at cleared)
- Complete task shows completion timestamp
- Toggle completion multiple times works correctly
- Mark non-existent task shows error

### CLI Mark Complete Handler

- [ ] T040 [US5] Implement handle_mark_complete(manager) in `src/cli/main.py`
  - Call handle_view_tasks(manager) to show current list
  - Prompt: "Enter task ID: "
  - Validate ID exists, show error if not
  - Get task to check current status
  - If already complete:
    - Prompt: "Task is already complete. Mark as incomplete? (yes/no): "
    - If yes: Call manager.mark_task_incomplete(id), print "✓ Task marked as incomplete!"
    - If no: Return without change
  - If pending:
    - Call manager.mark_task_complete(id)
    - Print "✓ Task marked as complete!"
  - If error (KeyError): Print "Error: Task not found"

### Integration Tests for User Story 5

- [ ] T041 [US5] Create integration test for mark complete workflow in `tests/integration/test_mark_complete.py`
  - Test: Mark pending task complete
  - Test: Mark complete task incomplete
  - Test: Toggling completion multiple times works
  - Test: Completed task shows completion timestamp
  - Test: Mark non-existent task shows error

---

## Phase 6: CLI Integration & Main Loop

**Goal**: Connect all handlers and create working application

- [ ] T042 [P] Implement run_main_loop(manager) in `src/cli/main.py`
  - Infinite loop until user exits:
    - Call display_menu()
    - Call get_menu_choice()
    - Route to appropriate handler based on choice:
      - 1 → handle_add_task()
      - 2 → handle_view_tasks()
      - 3 → handle_update_task()
      - 4 → handle_delete_task()
      - 5 → handle_mark_complete()
      - 6 → exit_application()
    - After operation, print separator and "Press Enter to continue..."
    - Clear screen (optional)

- [ ] T043 [P] Implement exit_application() in `src/cli/main.py`
  - Print goodbye message with separator
  - Print note: "Note: Your tasks are not saved (in-memory application)"
  - Exit program

- [ ] T044 [P] Implement main() entry point in `src/cli/main.py`
  - Print welcome message with header
  - Create TaskManager instance
  - Call run_main_loop(manager)

- [ ] T045 Implement `if __name__ == "__main__"` guard in `src/cli/main.py`
  - Call main()

### End-to-End Integration Test

- [ ] T046 [P] Create end-to-end integration test in `tests/integration/test_complete_workflow.py`
  - Test: Add task → View → Update → Mark Complete → Delete (full workflow)
  - Test: Add multiple tasks and verify list management
  - Test: All 5 user stories work together without interference
  - Test: Task IDs remain unique and preserved
  - Test: Error handling works throughout workflow

---

## Phase 7: Comprehensive Testing

**Goal**: Ensure all features work correctly and edge cases are handled

### Unit Tests

- [ ] T047 [P] Verify all Task model unit tests pass in `tests/unit/test_task.py`
  - Run: `python -m unittest tests.unit.test_task -v`

- [ ] T048 [P] Verify all TaskManager unit tests pass in `tests/unit/test_task_manager.py`
  - Run: `python -m unittest tests.unit.test_task_manager -v`

### Integration Tests

- [ ] T049 [P] Verify all integration tests pass
  - Run: `python -m unittest discover tests/integration -v`

### Full Test Suite

- [ ] T050 Run complete test suite and fix any failures
  - Run: `python -m unittest discover tests -v`
  - All tests must pass with 100% success rate

---

## Phase 8: Edge Case & Error Handling Testing

**Goal**: Validate behavior with edge cases and error conditions

- [ ] T051 Test empty input handling
  - Empty title submission
  - Whitespace-only title
  - Non-integer menu choices
  - Non-integer task ID input

- [ ] T052 Test error recovery
  - Invalid task ID → show error → menu returns to normal
  - Empty title → show error → can retry
  - Invalid menu choice → loop until valid

- [ ] T053 Test data integrity
  - Create 10 tasks, delete 3 in middle, verify remaining 7 have correct IDs
  - Update task doesn't affect others
  - Mark complete doesn't affect other tasks
  - No IDs are reused

- [ ] T054 Test large datasets (performance)
  - Add 100 tasks - should complete in < 5 seconds
  - View 100 tasks - should display in < 2 seconds
  - Delete from large list - should complete quickly

---

## Phase 9: Documentation & Polish

**Goal**: Complete documentation and finalize application

### Code Documentation

- [ ] T055 Add docstrings to Task class in `src/models/task.py`
  - Class docstring: Purpose and attributes
  - Method docstrings: Parameter types, return types, raises

- [ ] T056 Add docstrings to TaskManager class in `src/services/task_manager.py`
  - Class docstring: Purpose and responsibility
  - Method docstrings: Complete with examples

- [ ] T057 Add docstrings to CLI functions in `src/cli/main.py`
  - Function docstrings: Input, output, side effects

- [ ] T058 Add inline comments to complex logic
  - Validation logic in Task.__init__()
  - ID management in TaskManager.add_task()
  - Error handling in all handlers

### User Documentation

- [ ] T059 Complete README.md with:
  - Project overview
  - Features summary
  - Quick start instructions
  - Running the application
  - Running tests
  - Known limitations

- [ ] T060 Create FEATURES.md documenting:
  - Each feature with examples
  - Input/output for each operation
  - Error messages and recovery

### Final Validation

- [ ] T061 Run full application manually and verify:
  - All menu options work
  - All operations complete successfully
  - Error messages are clear
  - User experience is smooth
  - Beginner can use without documentation

- [ ] T062 Verify all success criteria from spec are met:
  - SC-001: All 5 features functional and independently testable
  - SC-002: Primary workflow completes in under 2 minutes
  - SC-003: All FR-001 through FR-015 have acceptance scenarios
  - SC-004: Edge cases handled without crashes
  - SC-005: Error messages are clear and actionable
  - SC-006: Task IDs are unique and preserved
  - SC-007: Beginner can use without external documentation

---

## Task Dependencies & Critical Path

### Dependency Graph

```
Phase 1: Setup (T001-T010)
    ↓
Phase 2: Foundational (T011-T029)
    ├─ Task Model (T011-T014, T024-T026)
    ├─ TaskManager (T015-T023, T027-T029)
    └─ BLOCKS: All user story implementations

Phase 3: User Stories 1-2 (T030-T035)
    ├─ US1: Add Task (T030-T033)
    ├─ US2: View Tasks (T034-T035)
    └─ CAN RUN IN PARALLEL

Phase 4-5: User Stories 3-5 (T036-T041)
    ├─ US3: Update Task (T036-T037)
    ├─ US4: Delete Task (T038-T039)
    ├─ US5: Mark Complete (T040-T041)
    └─ CAN RUN IN PARALLEL (independent operations)

Phase 6: Integration (T042-T046)
    ├─ Main loop and handlers
    └─ REQUIRES: All user story handlers complete

Phase 7-9: Testing, Polish (T047-T062)
    └─ REQUIRES: All implementation complete
```

### Critical Path (MVP)

For **minimum viable product** (add + view tasks only):
1. Phase 1: Setup (T001-T010)
2. Phase 2: Foundational (T011-T029)
3. Phase 3: US1 + US2 (T030-T035)
4. Phase 6: Integration (T042-T045)
5. Phase 7: Testing (T047-T050)

**Estimated tasks for MVP**: ~30 tasks (vs 62 total for full feature)

---

## Parallel Execution Plan

### Phase 2 Parallel Work
All tasks in Phase 2 can be done in parallel:
- Developer A: Task model (T011-T014)
- Developer B: TaskManager service (T015-T023)
- Developer C: Unit tests (T024-T029)

### Phase 3 Parallel Work
- Developer A: US1 Add Task (T030-T033)
- Developer B: US2 View Tasks (T034-T035)

### Phase 4-5 Parallel Work
- Developer A: US3 Update Task (T036-T037)
- Developer B: US4 Delete Task (T038-T039)
- Developer C: US5 Mark Complete (T040-T041)

### Phase 6+ Sequential
Must complete in order as dependencies exist.

---

## Quality Gates

- [ ] **Before Phase 3**: All Phase 2 unit tests pass
- [ ] **Before Phase 6**: All Phase 3-5 integration tests pass
- [ ] **Before Phase 7**: All Phase 6 integration tests pass
- [ ] **Final Gate**: 100% test pass rate, all edge cases handled, user can run app successfully

---

## Success Criteria Mapping

| Success Criterion | Validated By | Task ID |
|------------------|--------------|---------|
| SC-001: All 5 features functional | US1-US5 integration tests | T033, T035, T037, T039, T041 |
| SC-002: Primary workflow under 2 min | Manual testing in T061 | T061 |
| SC-003: All FR have scenarios | Acceptance scenario tests | T033, T035, T037, T039, T041 |
| SC-004: Edge cases handled | Phase 8 testing | T051-T054 |
| SC-005: Clear error messages | Manual testing + handlers | T032, T036, T038, T040 |
| SC-006: IDs unique and preserved | T053 + unit tests | T027, T053 |
| SC-007: Beginner-friendly UI | T061 + documentation | T055-T062 |

---

## Notes

- All tasks are marked with IDs (T001-T062) for tracking
- [P] markers indicate parallelizable tasks (different files, no dependencies)
- [US#] markers indicate which user story each task belongs to
- Tests are integrated into each user story phase (not separate)
- Phase 2 MUST complete before Phase 3 begins (blocking dependencies)
- Phases 3-5 can be executed in parallel
- Total of 62 tasks covering setup, implementation, testing, and documentation

