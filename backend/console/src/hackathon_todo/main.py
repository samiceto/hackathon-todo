"""
Main entry point for the hackathon-todo application.

This module contains the main application loop that integrates all user stories
into an interactive menu-driven interface.
"""

from hackathon_todo.storage import TaskStorage
from hackathon_todo.ui import (
    display_menu,
    add_task_ui,
    view_tasks_ui,
    mark_complete_ui,
    update_task_ui,
    delete_task_ui,
)


def main() -> None:
    """
    Main application entry point.

    Displays a welcome message, then enters an interactive menu loop where
    users can perform all CRUD operations on tasks. Handles user input,
    menu selection, and graceful exit (including Ctrl+C interruption).

    The application runs until the user selects Exit or presses Ctrl+C.

    Side Effects:
        - Creates TaskStorage instance (in-memory)
        - Displays welcome message
        - Enters interactive menu loop
        - Calls UI functions based on user selection
        - Displays goodbye message on exit
        - Handles KeyboardInterrupt gracefully

    Examples:
        >>> main()
        Welcome to Hackathon Todo!
        [Interactive menu loop...]
        Goodbye! Thanks for using Hackathon Todo.
    """
    # Display welcome message
    print("\n" + "=" * 50)
    print("Welcome to Hackathon Todo!")
    print("Your simple command-line task manager")
    print("=" * 50)

    # Initialize storage
    storage = TaskStorage()

    try:
        # Main application loop
        while True:
            # Display menu
            display_menu()

            # Get user choice
            choice = input("\nEnter your choice (1-6): ").strip()

            # Handle menu selection
            if choice == "1":
                add_task_ui(storage)
            elif choice == "2":
                view_tasks_ui(storage)
            elif choice == "3":
                mark_complete_ui(storage)
            elif choice == "4":
                update_task_ui(storage)
            elif choice == "5":
                delete_task_ui(storage)
            elif choice == "6":
                print("\n" + "=" * 50)
                print("Goodbye! Thanks for using Hackathon Todo.")
                print("=" * 50 + "\n")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 6.")

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n" + "=" * 50)
        print("Interrupted! Goodbye!")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
