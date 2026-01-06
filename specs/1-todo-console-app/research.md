# Phase 0: Research & Findings

**Date**: 2026-01-01
**Purpose**: Resolve technical unknowns and establish best practices for implementation

---

## Research Topic 1: Python Console Application Architecture

### Decision
Use modular layered architecture with three distinct layers:
1. **Models Layer** - Data structures and validation (task.py)
2. **Services Layer** - Business logic and storage (task_manager.py)
3. **CLI Layer** - User interface and menu navigation (main.py)

### Rationale
- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Layers can be tested independently
- **Maintainability**: Changes to one layer don't break others
- **Beginner Learning**: Clear structure teaches best practices

### Alternatives Considered
- **Monolithic (everything in one file)**: Rejected because it makes testing and debugging harder for learning purposes
- **Over-engineered design patterns**: Rejected because complexity violates beginner-friendly constraint

### Best Practices Applied
- Import models at the top of services
- Import services at the top of CLI
- No circular dependencies between layers
- Clear public interfaces (functions/methods that are intended to be called)

---

## Research Topic 2: In-Memory Data Structures & ID Management

### Decision
- Use a Python **list of dictionaries** or **list of Task objects** to store tasks
- Use an **auto-incrementing integer counter** for task IDs
- Never reuse deleted task IDs (maintain sequential counter)

### Rationale
- **Python Lists**: Simple, familiar to beginners, supports all required operations
- **Integer IDs**: Easy to display and select from user prompts
- **Auto-incrementing**: Prevents ID collisions and simplifies management
- **No Reuse**: Maintains data integrity and prevents confusion (old references don't accidentally resolve)

### Alternatives Considered
- **Dictionary with UUID keys**: More robust but unnecessarily complex for Phase I
- **Object-Relational Mapping (ORM)**: Overkill without a database
- **Complex ID management (e.g., reusing gaps)**: Complicates the code and user experience

### Best Practices Applied
- Task ID counter starts at 1 (convention)
- Store tasks in a simple list accessed by index (O(n) but acceptable for <1000 tasks)
- Optional: Dictionary lookup by ID if performance becomes issue (O(1) lookup)

---

## Research Topic 3: Task Model Validation

### Decision
Implement validation directly in the Task class with:
- Non-empty title validation (strip whitespace)
- Optional description (default to empty string)
- Status limited to ["pending", "complete"]
- Automatic timestamp generation (created_at, completed_at)

### Rationale
- **Early Validation**: Catch errors at creation time, not later
- **Fail Fast**: Invalid tasks never enter storage
- **Clear Messages**: Validation errors guide user to correct input
- **Consistent State**: All tasks in storage are guaranteed valid

### Alternatives Considered
- **Validation in CLI layer**: Rejected because it mixes concerns; business rules belong in models
- **Validation in TaskManager**: Rejected because models should be self-validating
- **No validation**: Rejected because error handling requirement demands it

### Best Practices Applied
- Constructor validates all required fields
- Raise `ValueError` with clear messages for invalid input
- Boolean methods for state checks (is_complete(), is_pending())
- Immutable ID after creation (set once, never changed)

---

## Research Topic 4: Testing Strategy

### Decision
Implement **Test-Driven Development (TDD)** with three test levels:

1. **Unit Tests** (tests/unit/)
   - Test individual methods in isolation
   - Test Task validation
   - Test TaskManager CRUD operations
   - Test CLI input/output

2. **Integration Tests** (tests/integration/)
   - Test complete workflows (add → view → update → delete)
   - Test state consistency across operations
   - Test error recovery

3. **Test Framework**: Python `unittest` (standard library)

### Rationale
- **TDD Benefits**: Clarifies requirements, ensures comprehensive coverage, enables refactoring
- **unittest Choice**: Standard library (no external dependencies), supports fixtures, discovery
- **Three Levels**: Unit tests catch regressions, integration tests verify workflows
- **Beginner Learning**: Clear test patterns teach best practices

### Alternatives Considered
- **pytest**: More powerful but requires external dependency
- **No automated tests**: Violates requirement for comprehensive testing
- **Manual testing only**: Error-prone, doesn't scale

### Best Practices Applied
- Each test method tests one thing (single assertion principle where possible)
- Descriptive test names: `test_add_task_with_valid_title_succeeds()`
- Use setUp() for test fixtures (creating sample tasks)
- Test both happy paths and error cases
- Assertion messages explain what failed

---

## Research Topic 5: Error Handling & User Experience

### Decision
- Try-except blocks at each operation layer
- User-friendly error messages that specify:
  - What went wrong
  - Why it failed
  - How to fix it
- No exception stack traces shown to users (logged for debugging)

### Rationale
- **Graceful Failure**: App doesn't crash on invalid input
- **Clear Feedback**: Users understand what to correct
- **Professional Feel**: Expected behavior for CLI applications
- **Debugging**: Stack traces available for developers if needed

### Alternatives Considered
- **No error handling**: Violates user experience requirements
- **Technical error messages**: Confuses non-technical users
- **Logging only**: Users don't know what failed

### Best Practices Applied
- Specific exception types (ValueError, KeyError, etc.)
- Error messages in user's language (not technical jargon)
- Options for recovery (try again, see help, etc.)
- Logging for developers (optional, beyond Phase I)

---

## Research Topic 6: CLI Design Pattern

### Decision
- **Menu-driven interface** with numbered options
- **Input validation loop** for user selections
- **Clear prompts** asking what operation user wants
- **Confirmation for destructive operations** (delete, mark incomplete)

### Rationale
- **Beginner Friendly**: Clear menu eliminates guessing about valid commands
- **Navigability**: Users can see available options without memorizing commands
- **Discoverability**: New users can explore without documentation
- **Confirmation**: Prevents accidental data loss

### Alternatives Considered
- **Command-line arguments** (python main.py add "Title"): Less interactive, harder for beginners
- **Keyboard shortcuts** (Ctrl+A for add): Harder to discover, steeper learning curve
- **Natural language processing**: Overkill for Phase I

### Best Practices Applied
- Clear formatting with separators (dashes, blank lines)
- Numbered menu options (1-6)
- Input validation loop for menu selection
- Show current list after operations (provides feedback)
- Graceful exit (option to quit)

---

## Research Topic 7: Date/Time Handling

### Decision
- Use Python `datetime.datetime` for all timestamps
- Store in ISO 8601 format internally (datetime objects)
- Display in human-readable format: "2026-01-01 15:30:45"
- Optional: Support timezone-aware dates (defer to Phase II if needed)

### Rationale
- **Standard Library**: datetime is built-in, no dependencies
- **ISO Format**: Sortable, unambiguous, international standard
- **Readability**: ISO + human-readable balances both needs
- **Flexibility**: Easy to change display format later

### Alternatives Considered
- **Unix timestamps**: Less readable for users
- **String dates**: Ambiguous (MM/DD vs DD/MM), can't calculate durations
- **Third-party libraries (pendulum, arrow)**: Adds dependency, overkill for Phase I

### Best Practices Applied
- Use `datetime.now()` for current time
- Store in UTC internally (consider timezone handling in Phase II)
- Format for display: `strftime("%Y-%m-%d %H:%M:%S")`
- Compare using datetime objects, not strings

---

## Summary of Technical Decisions

| Aspect | Decision | Justification |
|--------|----------|---------------|
| Architecture | Layered (Models, Services, CLI) | Separation of concerns, testability |
| Storage | In-memory list with auto-ID | Simplicity, meets Phase I requirements |
| Validation | In Task model | Early validation, fail-fast |
| Testing | TDD with unittest | Coverage, best practices, standard library |
| Error Handling | Try-except with user-friendly messages | Graceful failure, good UX |
| CLI | Menu-driven with confirmations | Beginner-friendly, discoverable |
| Timestamps | datetime module, ISO format | Standard, readable, flexible |

---

## Ready for Phase 1: Design & Contracts

All technical unknowns have been resolved. Proceeding to:
1. Detailed data model specification
2. Function/method contracts for each component
3. Quick-start implementation guide

