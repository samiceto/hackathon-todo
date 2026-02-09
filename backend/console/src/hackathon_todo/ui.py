"""
User interface functions for hackathon-todo application.

This module handles all user interaction including input validation,
display formatting, and interactive operation flows.
"""

from hackathon_todo.storage import TaskStorage


def display_menu() -> None:
    """
    Display the main menu options to the user.

    Shows all available operations in a numbered list format.

    Side Effects:
        - Prints menu options to stdout

    Examples:
        >>> display_menu()
        === Hackathon Todo Menu ===
        1. Add Task
        2. View Tasks
        3. Mark Complete/Incomplete
        4. Update Task
        5. Delete Task
        6. Exit
    """
    print("\n" + "=" * 30)
    print("=== Hackathon Todo Menu ===")
    print("=" * 30)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Complete/Incomplete")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Exit")
    print("=" * 30)


def get_non_empty_input(prompt: str) -> str:
    """
    Get non-empty input from user with retry loop.

    Continuously prompts the user until valid non-empty input is received.
    Input is stripped of leading/trailing whitespace.

    Args:
        prompt: Message to display to user

    Returns:
        Non-empty, whitespace-stripped string

    Examples:
        >>> # User enters "  Hello  "
        >>> result = get_non_empty_input("Enter text: ")
        >>> result
        'Hello'
    """
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        print("Error: Input cannot be empty. Please try again.")


def add_task_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for adding a new task.

    Prompts user for task title (required) and description (optional),
    creates the task in storage, and displays a success message with
    the assigned task ID.

    Args:
        storage: TaskStorage instance to add task to

    Side Effects:
        - Prompts user for title and description via stdin
        - Creates task in storage
        - Prints success message to stdout

    Examples:
        >>> storage = TaskStorage()
        >>> # User enters: "Buy groceries" and "Milk, eggs, bread"
        >>> add_task_ui(storage)
        Task added successfully! (ID: 1)
    """
    print("\n--- Add New Task ---")
    
    # Get required title
    title = get_non_empty_input("Enter task title: ")
    
    # Get optional description
    description_input = input("Enter task description (optional, press Enter to skip): ").strip()
    
    # Create task in storage
    task = storage.add(title, description_input)
    
    # Display success message
    print(f"\nTask added successfully! (ID: {task.id})")
    print(f"Title: {task.title}")
    if task.description:
        print(f"Description: {task.description}")


def view_tasks_ui(storage: TaskStorage) -> None:
    """
    Display all tasks in a formatted, readable list.

    Shows all tasks with their ID, status, title, and description in a
    visually organized format. Displays a friendly message if no tasks exist.

    Args:
        storage: TaskStorage instance to read from

    Side Effects:
        - Prints formatted task list to stdout
        - Prints friendly message if no tasks exist

    Examples:
        >>> storage = TaskStorage()
        >>> storage.add("Buy groceries", "Milk, eggs")
        >>> view_tasks_ui(storage)
        --- All Tasks ---
        [1] ○ Buy groceries
            Milk, eggs
    """
    print("\n--- All Tasks ---")

    tasks = storage.get_all()

    if not tasks:
        print("\nNo tasks found. Add your first task to get started!")
        return

    print()  # Blank line for spacing

    for task in tasks:
        # Format status indicator
        status_icon = "✓" if task.completed else "○"

        # Display task header with ID, status, and title
        print(f"[{task.id}] {status_icon} {task.title}")

        # Display description if present (indented)
        if task.description:
            print(f"    {task.description}")

    # Show task count summary
    print(f"\nTotal tasks: {storage.count()}")


def get_task_id(storage: TaskStorage, prompt: str) -> int:
    """
    Get valid task ID from user with retry loop.

    Continuously prompts the user until a valid task ID is entered.
    Validates that the input is numeric and that the task exists in storage.

    Args:
        storage: TaskStorage instance to validate ID against
        prompt: Message to display to user

    Returns:
        Valid task ID that exists in storage

    Examples:
        >>> storage = TaskStorage()
        >>> storage.add("Test task")
        >>> # User enters "1"
        >>> task_id = get_task_id(storage, "Enter task ID: ")
        >>> task_id
        1
    """
    while True:
        user_input = input(prompt).strip()

        # Check if input is numeric
        if not user_input.isdigit():
            print("Error: Please enter a valid task ID (number).")
            continue

        task_id = int(user_input)

        # Check if task exists
        if storage.get(task_id) is None:
            print(f"Error: Task ID {task_id} not found.")
            continue

        return task_id


def mark_complete_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for marking a task as complete or incomplete.

    Prompts user for task ID and toggles the completion status of that task.
    Displays the updated status after toggling.

    Args:
        storage: TaskStorage instance containing tasks

    Side Effects:
        - Prompts user for task ID via stdin
        - Toggles task completion status in storage
        - Prints success message with updated status to stdout

    Examples:
        >>> storage = TaskStorage()
        >>> task = storage.add("Test task")
        >>> # User enters "1"
        >>> mark_complete_ui(storage)
        Task 1 marked as complete!
    """
    print("\n--- Mark Task Complete/Incomplete ---")

    # Check if there are any tasks
    if storage.count() == 0:
        print("\nNo tasks available. Add a task first!")
        return

    # Get valid task ID from user
    task_id = get_task_id(storage, "Enter task ID to toggle completion: ")

    # Toggle the task completion status
    task = storage.toggle_complete(task_id)

    # Display success message with new status
    status_text = "complete" if task.completed else "incomplete"
    print(f"\nTask {task_id} marked as {status_text}!")
    print(f"[{task.id}] {'✓' if task.completed else '○'} {task.title}")


def get_optional_input(prompt: str, current_value: str) -> str | None:
    """
    Get optional input from user, allowing them to skip by pressing Enter.

    Shows the current value and allows the user to either enter a new value
    or press Enter to keep the existing value unchanged.

    Args:
        prompt: Message to display to user
        current_value: Current value to display and keep if user skips

    Returns:
        New input value if provided, None if user pressed Enter to skip

    Examples:
        >>> # User presses Enter (skip)
        >>> result = get_optional_input("New title: ", "Old title")
        >>> result is None
        True

        >>> # User enters "New title"
        >>> result = get_optional_input("New title: ", "Old title")
        >>> result
        'New title'
    """
    display_value = current_value if current_value else "(empty)"
    full_prompt = f"{prompt} [current: {display_value}] (press Enter to skip): "
    user_input = input(full_prompt).strip()

    # Return None if user pressed Enter (skip), otherwise return the input
    return user_input if user_input else None


def update_task_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for updating task title and/or description.

    Prompts user for task ID, then allows updating title and/or description.
    User can press Enter to skip updating a field. At least one field must
    be updated for the operation to proceed.

    Args:
        storage: TaskStorage instance containing tasks

    Side Effects:
        - Prompts user for task ID and new values via stdin
        - Updates task in storage
        - Prints success message with updated values to stdout

    Examples:
        >>> storage = TaskStorage()
        >>> task = storage.add("Old title", "Old description")
        >>> # User enters "1", "New title", presses Enter to skip description
        >>> update_task_ui(storage)
        Task 1 updated successfully!
    """
    print("\n--- Update Task ---")

    # Check if there are any tasks
    if storage.count() == 0:
        print("\nNo tasks available. Add a task first!")
        return

    # Get valid task ID from user
    task_id = get_task_id(storage, "Enter task ID to update: ")

    # Get current task to show current values
    task = storage.get(task_id)

    print(f"\nUpdating task: {task.title}")
    print("Press Enter to skip a field and keep its current value.\n")

    # Get optional new title
    new_title = get_optional_input("New title", task.title)

    # Get optional new description
    new_description = get_optional_input("New description", task.description)

    # Check if at least one field is being updated
    if new_title is None and new_description is None:
        print("\nNo changes made. Both fields skipped.")
        return

    # Update the task with new values (None means keep current value)
    try:
        updated_task = storage.update(task_id, new_title, new_description)

        # Display success message
        print(f"\nTask {task_id} updated successfully!")
        print(f"[{updated_task.id}] {'✓' if updated_task.completed else '○'} {updated_task.title}")
        if updated_task.description:
            print(f"    {updated_task.description}")

    except ValueError as e:
        # Handle validation errors (e.g., empty title)
        print(f"\nError: {e}")
        print("Task was not updated.")


def delete_task_ui(storage: TaskStorage) -> None:
    """
    Interactive flow for deleting a task by ID.

    Prompts user for task ID, shows the task to be deleted,
    and removes it from storage.

    Args:
        storage: TaskStorage instance containing tasks

    Side Effects:
        - Prompts user for task ID via stdin
        - Deletes task from storage
        - Prints success message to stdout

    Examples:
        >>> storage = TaskStorage()
        >>> task = storage.add("Task to delete", "Description")
        >>> # User enters "1"
        >>> delete_task_ui(storage)
        Task 1 deleted successfully!
    """
    print("\n--- Delete Task ---")

    # Check if there are any tasks
    if storage.count() == 0:
        print("\nNo tasks available. Add a task first!")
        return

    # Get valid task ID from user
    task_id = get_task_id(storage, "Enter task ID to delete: ")

    # Get task details before deletion to show in confirmation
    task = storage.get(task_id)

    # Delete the task
    success = storage.delete(task_id)

    if success:
        # Display success message
        print(f"\nTask {task_id} deleted successfully!")
        print(f"Deleted: [{task.id}] {task.title}")

        # Show remaining task count
        remaining = storage.count()
        if remaining == 0:
            print("\nNo tasks remaining. The list is now empty.")
        else:
            print(f"\nRemaining tasks: {remaining}")
    else:
        # This should not happen since get_task_id validates existence
        print(f"\nError: Failed to delete task {task_id}.")
