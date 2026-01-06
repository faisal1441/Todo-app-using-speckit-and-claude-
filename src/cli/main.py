"""
Command-Line Interface for the Todo Application.

This module provides the interactive console interface for the todo application.
It handles menu display, user input, and dispatches to appropriate handlers for
each operation (add, view, update, delete, mark complete).

Example:
    Running the application:
        >>> python src/cli/main.py

    The menu will display and users can select from 6 options to manage tasks.
"""

from src.services.task_manager import TaskManager


# ============================================================================
# Menu Display Functions
# ============================================================================


def display_menu() -> None:
    """
    Display the main menu with available options.

    Prints a formatted menu showing all available operations:
    1. Add a new task
    2. View all tasks
    3. Update a task
    4. Delete a task
    5. Mark task complete/incomplete
    6. Exit application

    Example:
        >>> display_menu()
        =====================================
          TODO CONSOLE APPLICATION
        =====================================
        Choose an option:
        1. Add a new task
        ...
    """
    print("\n" + "=" * 40)
    print("  TODO CONSOLE APPLICATION")
    print("=" * 40)
    print("Choose an option:")
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. Update a task")
    print("4. Delete a task")
    print("5. Mark task complete/incomplete")
    print("6. Exit application")
    print("-" * 40)


def get_menu_choice() -> int:
    """
    Get and validate the user's menu choice.

    Prompts the user to enter a number between 1-6. If the input is invalid
    (non-numeric, out of range), displays an error and loops until valid input
    is provided.

    Returns:
        int: Valid menu choice (1-6)

    Example:
        >>> choice = get_menu_choice()
        Enter your choice (1-6): 1
        >>> choice
        1
    """
    while True:
        try:
            choice = int(input("Enter your choice (1-6): "))
            if 1 <= choice <= 6:
                return choice
            print("Invalid choice. Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# ============================================================================
# Operation Handlers
# ============================================================================


def handle_add_task(manager: TaskManager) -> None:
    """
    Handle adding a new task via user input.

    Prompts the user for a task title (required) and description (optional),
    then adds the task to the task manager. Displays confirmation with the
    task ID or an error message if validation fails.

    Args:
        manager (TaskManager): The task manager instance

    Side Effects:
        - Adds task to manager if successful
        - Prints user feedback (success or error message)

    Example:
        >>> manager = TaskManager()
        >>> handle_add_task(manager)
        --- Add New Task ---
        Enter task title: Buy groceries
        Enter description (optional, press Enter to skip): For Sunday dinner
        ✓ Task added successfully! (ID: 1)
    """
    print("\n--- Add New Task ---")
    title = input("Enter task title: ").strip()

    if not title:
        print("Error: Task title cannot be empty")
        return

    description = input("Enter description (optional, press Enter to skip): ").strip()

    try:
        task = manager.add_task(title, description)
        print(f"✓ Task added successfully! (ID: {task.id})")
    except ValueError as e:
        print(f"Error: {e}")


def handle_view_tasks(manager: TaskManager) -> None:
    """
    Display all tasks with their details and status.

    Shows a formatted list of all tasks including ID, title, status, creation
    date, and completion date (if completed). Displays a summary count of
    pending and completed tasks. Shows a message if the list is empty.

    Args:
        manager (TaskManager): The task manager instance

    Side Effects:
        - Prints tasks and summary to console

    Example:
        >>> manager = TaskManager()
        >>> manager.add_task("Task 1")
        >>> manager.add_task("Task 2")
        >>> handle_view_tasks(manager)
        --- All Tasks (2 total) ---
        [#1] Task 1
            Status: pending
            Created: 2026-01-01 10:00:00
        ...
        Summary: 2 pending, 0 complete
    """
    print("\n--- All Tasks ---")

    if manager.is_empty():
        print("No tasks yet. Add one to get started!")
        return

    all_tasks = manager.get_all_tasks()
    print(f"--- All Tasks ({manager.count_tasks()} total) ---")

    for task in all_tasks:
        print(f"\n[#{task.id}] {task.title}")
        print(f"    Status: {task.status}")
        created_str = task.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"    Created: {created_str}")

        if task.is_complete() and task.completed_at:
            completed_str = task.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"    Completed: {completed_str}")

        if task.description:
            print(f"    Description: {task.description}")

    print()
    pending_count = manager.count_pending()
    completed_count = manager.count_completed()
    print(f"Summary: {pending_count} pending, {completed_count} complete")


def handle_update_task(manager: TaskManager) -> None:
    """
    Handle updating an existing task.

    Shows current tasks, prompts for task ID, then prompts for new title
    and/or description. Updates only the fields that are provided (pressing
    Enter skips that field). Displays confirmation or error message.

    Args:
        manager (TaskManager): The task manager instance

    Side Effects:
        - Updates task in manager if successful
        - Prints user feedback (success or error message)

    Example:
        >>> manager = TaskManager()
        >>> manager.add_task("Buy groceries")
        >>> handle_update_task(manager)
        [Shows tasks...]
        --- Update Task ---
        Enter task ID to update: 1
        Enter new title (or press Enter to keep current): Buy groceries and cook
        Enter new description (or press Enter to keep current): For Sunday party
        ✓ Task updated successfully!
    """
    print("\n--- Update Task ---")

    # Show current tasks
    handle_view_tasks(manager)

    try:
        task_id_str = input("Enter task ID to update: ").strip()
        task_id = int(task_id_str)
    except ValueError:
        print("Error: Please enter a valid number")
        return

    if not manager.is_task_exists(task_id):
        print("Error: Task not found")
        return

    # Get current task for reference
    task = manager.get_task_by_id(task_id)

    # Prompt for updates
    new_title_input = input("Enter new title (or press Enter to keep current): ").strip()
    new_description_input = input(
        "Enter new description (or press Enter to keep current): "
    ).strip()

    try:
        # Only update fields that were provided
        title = new_title_input if new_title_input else None
        description = new_description_input if new_description_input else None
        manager.update_task(task_id, title=title, description=description)
        print("✓ Task updated successfully!")
    except ValueError as e:
        print(f"Error: {e}")


def handle_delete_task(manager: TaskManager) -> None:
    """
    Handle deleting a task with confirmation.

    Shows current tasks, prompts for task ID, displays the task title for
    confirmation, then prompts for yes/no confirmation. Only deletes if user
    confirms with "yes" or "y" (case-insensitive).

    Args:
        manager (TaskManager): The task manager instance

    Side Effects:
        - Deletes task from manager if user confirms
        - Prints user feedback and confirmation status

    Example:
        >>> manager = TaskManager()
        >>> manager.add_task("Buy groceries")
        >>> handle_delete_task(manager)
        [Shows tasks...]
        --- Delete Task ---
        Enter task ID to delete: 1
        Are you sure you want to delete 'Buy groceries'? (yes/no): yes
        ✓ Task deleted successfully!
    """
    print("\n--- Delete Task ---")

    # Show current tasks
    handle_view_tasks(manager)

    try:
        task_id_str = input("Enter task ID to delete: ").strip()
        task_id = int(task_id_str)
    except ValueError:
        print("Error: Please enter a valid number")
        return

    if not manager.is_task_exists(task_id):
        print("Error: Task not found")
        return

    # Get task for confirmation
    task = manager.get_task_by_id(task_id)

    # Confirm deletion
    confirmation = input(
        f"Are you sure you want to delete '{task.title}'? (yes/no): "
    ).strip().lower()

    if confirmation in ("yes", "y"):
        try:
            manager.delete_task(task_id)
            print("✓ Task deleted successfully!")
        except KeyError:
            print("Error: Task not found")
    else:
        print("Deletion cancelled")


def handle_mark_complete(manager: TaskManager) -> None:
    """
    Handle marking a task complete or incomplete.

    Shows current tasks, prompts for task ID. If the task is pending, marks
    it as complete. If the task is already complete, prompts to confirm
    marking it as incomplete.

    Args:
        manager (TaskManager): The task manager instance

    Side Effects:
        - Updates task status in manager
        - Prints user feedback and status change confirmation

    Example:
        >>> manager = TaskManager()
        >>> manager.add_task("Task")
        >>> handle_mark_complete(manager)
        [Shows tasks...]
        --- Mark Task Complete/Incomplete ---
        Enter task ID: 1
        ✓ Task marked as complete!
    """
    print("\n--- Mark Task Complete/Incomplete ---")

    # Show current tasks
    handle_view_tasks(manager)

    try:
        task_id_str = input("Enter task ID: ").strip()
        task_id = int(task_id_str)
    except ValueError:
        print("Error: Please enter a valid number")
        return

    if not manager.is_task_exists(task_id):
        print("Error: Task not found")
        return

    task = manager.get_task_by_id(task_id)

    try:
        if task.is_complete():
            # Task is already complete, ask to mark incomplete
            confirmation = input(
                "Task is already complete. Mark as incomplete? (yes/no): "
            ).strip().lower()
            if confirmation in ("yes", "y"):
                manager.mark_task_incomplete(task_id)
                print("✓ Task marked as incomplete!")
            else:
                print("No change made")
        else:
            # Task is pending, mark as complete
            manager.mark_task_complete(task_id)
            print("✓ Task marked as complete!")
    except KeyError:
        print("Error: Task not found")


# ============================================================================
# Main Loop and Entry Point
# ============================================================================


def run_main_loop(manager: TaskManager) -> None:
    """
    Run the main interactive menu loop.

    Displays the menu repeatedly and dispatches user choices to appropriate
    handlers. Continues until the user chooses to exit (option 6).

    Args:
        manager (TaskManager): The task manager instance

    Side Effects:
        - Displays menu and prompts for input
        - Calls handlers based on user choice
        - Runs indefinitely until user exits

    Example:
        >>> manager = TaskManager()
        >>> run_main_loop(manager)
        # Shows menu, prompts for choice, handles operation, repeats
    """
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


def exit_application() -> None:
    """
    Display exit message and prepare to exit the application.

    Prints a goodbye message confirming that tasks have been saved.

    Side Effects:
        - Prints goodbye message to console

    Example:
        >>> exit_application()
        =====================================
        Thank you for using Todo App!
        Your tasks have been saved.
        =====================================
    """
    print("\n" + "=" * 40)
    print("Thank you for using Todo App!")
    print("Your tasks have been saved.")
    print("=" * 40)


def main() -> None:
    """
    Entry point for the todo application.

    Creates a TaskManager instance with file persistence enabled,
    displays a welcome message, and starts the main event loop.

    Tasks are automatically saved to tasks.json in the project directory
    after each operation.

    Side Effects:
        - Prints welcome message
        - Creates TaskManager instance with persistence
        - Loads existing tasks from tasks.json if it exists
        - Creates tasks.json if it doesn't exist
        - Runs the main loop (blocking until user exits)

    Example:
        >>> main()
        # Application starts and runs until user exits
    """
    print("\n" + "=" * 40)
    print("Welcome to Todo Console Application!")
    print("=" * 40)

    tasks_file = "tasks.json"
    manager = TaskManager(persistence_file=tasks_file)
    print(f"Tasks will be saved to: {tasks_file}\n")

    run_main_loop(manager)


# ============================================================================
# Script Execution
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        exit_application()
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please try again or contact support")
