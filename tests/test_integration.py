"""
Integration tests for the hackathon-todo application.

Tests cover complete workflows combining multiple operations to ensure
all components work together correctly.
"""

import pytest
from hackathon_todo.storage import TaskStorage
from hackathon_todo.main import main
from hackathon_todo.ui import (
    display_menu,
    add_task_ui,
    view_tasks_ui,
    mark_complete_ui,
    update_task_ui,
    delete_task_ui,
)


class TestDisplayMenu:
    """Test menu display function."""

    def test_display_menu_shows_all_options(self, capsys):
        """Should display all 6 menu options."""
        display_menu()

        captured = capsys.readouterr()
        assert "=== Hackathon Todo Menu ===" in captured.out
        assert "1. Add Task" in captured.out
        assert "2. View Tasks" in captured.out
        assert "3. Mark Complete/Incomplete" in captured.out
        assert "4. Update Task" in captured.out
        assert "5. Delete Task" in captured.out
        assert "6. Exit" in captured.out


class TestFullCRUDWorkflow:
    """Test complete CRUD workflow integrating all operations."""

    def test_full_crud_workflow(self, storage, monkeypatch, capsys):
        """Should complete full CRUD cycle: Create, Read, Update, Delete."""
        # CREATE: Add a task
        inputs_add = iter(["Buy groceries", "Milk, eggs, bread"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_add))
        add_task_ui(storage)

        # Verify task was created
        assert storage.count() == 1
        task = storage.get(1)
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False

        # READ: View tasks
        capsys.readouterr()  # Clear previous output
        view_tasks_ui(storage)
        captured = capsys.readouterr()
        assert "Buy groceries" in captured.out
        assert "Milk, eggs, bread" in captured.out

        # UPDATE: Mark as complete
        monkeypatch.setattr('builtins.input', lambda _: "1")
        mark_complete_ui(storage)
        task = storage.get(1)
        assert task.completed is True

        # UPDATE: Modify task details
        inputs_update = iter(["1", "Buy groceries and supplies", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_update))
        update_task_ui(storage)
        task = storage.get(1)
        assert task.title == "Buy groceries and supplies"

        # DELETE: Remove task
        monkeypatch.setattr('builtins.input', lambda _: "1")
        delete_task_ui(storage)
        assert storage.count() == 0
        assert storage.get(1) is None

    def test_multiple_tasks_workflow(self, storage, monkeypatch, capsys):
        """Should handle multiple tasks through various operations."""
        # Add 3 tasks
        for i in range(1, 4):
            inputs = iter([f"Task {i}", f"Description {i}"])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
            add_task_ui(storage)

        assert storage.count() == 3

        # Mark task 2 as complete
        monkeypatch.setattr('builtins.input', lambda _: "2")
        mark_complete_ui(storage)

        # Verify only task 2 is complete
        assert storage.get(1).completed is False
        assert storage.get(2).completed is True
        assert storage.get(3).completed is False

        # Update task 1
        inputs_update = iter(["1", "Updated Task 1", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_update))
        update_task_ui(storage)
        assert storage.get(1).title == "Updated Task 1"

        # Delete task 2
        monkeypatch.setattr('builtins.input', lambda _: "2")
        delete_task_ui(storage)
        assert storage.count() == 2
        assert storage.get(2) is None

        # View remaining tasks
        capsys.readouterr()  # Clear
        view_tasks_ui(storage)
        captured = capsys.readouterr()
        assert "Updated Task 1" in captured.out
        assert "Task 3" in captured.out
        assert "Total tasks: 2" in captured.out


class TestEdgeCaseWorkflows:
    """Test edge cases and error handling in workflows."""

    def test_empty_storage_workflow(self, storage, capsys):
        """Should handle empty storage gracefully across operations."""
        # View empty storage
        view_tasks_ui(storage)
        captured = capsys.readouterr()
        assert "No tasks found" in captured.out

        # Mark complete with empty storage
        mark_complete_ui(storage)
        captured = capsys.readouterr()
        assert "No tasks available" in captured.out

        # Update with empty storage
        update_task_ui(storage)
        captured = capsys.readouterr()
        assert "No tasks available" in captured.out

        # Delete with empty storage
        delete_task_ui(storage)
        captured = capsys.readouterr()
        assert "No tasks available" in captured.out

    def test_single_task_lifecycle(self, storage, monkeypatch, capsys):
        """Should handle complete lifecycle of a single task."""
        # Add task
        inputs_add = iter(["Single task", "Description"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_add))
        add_task_ui(storage)

        # View it
        capsys.readouterr()
        view_tasks_ui(storage)
        captured = capsys.readouterr()
        assert "Single task" in captured.out
        assert "Total tasks: 1" in captured.out

        # Mark complete
        monkeypatch.setattr('builtins.input', lambda _: "1")
        mark_complete_ui(storage)

        # Update while complete
        inputs_update = iter(["1", "", "Updated description"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_update))
        update_task_ui(storage)
        task = storage.get(1)
        assert task.completed is True  # Status preserved
        assert task.description == "Updated description"

        # Delete last task
        capsys.readouterr()
        monkeypatch.setattr('builtins.input', lambda _: "1")
        delete_task_ui(storage)
        captured = capsys.readouterr()
        assert "The list is now empty" in captured.out

    def test_invalid_operations_workflow(self, storage, monkeypatch, capsys):
        """Should handle invalid inputs during workflow."""
        # Add a task
        inputs_add = iter(["Valid task", "Description"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_add))
        add_task_ui(storage)

        # Try to mark invalid ID complete (then valid)
        inputs_mark = iter(["99", "1"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_mark))
        mark_complete_ui(storage)
        captured = capsys.readouterr()
        assert "Error: Task ID 99 not found" in captured.out
        assert storage.get(1).completed is True  # Eventually succeeded

        # Try to update with invalid ID (then valid)
        inputs_update = iter(["abc", "1", "Updated", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_update))
        update_task_ui(storage)
        captured = capsys.readouterr()
        assert "Error: Please enter a valid task ID (number)" in captured.out
        assert storage.get(1).title == "Updated"  # Eventually succeeded


class TestDataPersistence:
    """Test that data persists correctly across operations."""

    def test_data_persists_across_operations(self, storage, monkeypatch, capsys):
        """Should maintain data consistency across multiple operations."""
        # Add task with specific data
        inputs_add = iter(["Important Task", "Critical data"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_add))
        add_task_ui(storage)

        original_id = storage.get(1).id
        original_created_at = storage.get(1).created_at

        # Mark complete
        monkeypatch.setattr('builtins.input', lambda _: "1")
        mark_complete_ui(storage)

        # Verify ID and creation time unchanged
        assert storage.get(1).id == original_id
        assert storage.get(1).created_at == original_created_at
        assert storage.get(1).completed is True

        # Update task
        inputs_update = iter(["1", "", "Updated critical data"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs_update))
        update_task_ui(storage)

        # Verify ID, creation time, and completion status unchanged
        task = storage.get(1)
        assert task.id == original_id
        assert task.created_at == original_created_at
        assert task.completed is True  # Preserved
        assert task.title == "Important Task"  # Unchanged (skipped)
        assert task.description == "Updated critical data"  # Updated

    def test_sequential_id_assignment(self, storage, monkeypatch, capsys):
        """Should assign IDs sequentially even after deletions."""
        # Add 3 tasks
        for i in range(1, 4):
            inputs = iter([f"Task {i}", ""])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
            add_task_ui(storage)

        # Delete task 2
        monkeypatch.setattr('builtins.input', lambda _: "2")
        delete_task_ui(storage)

        # Add new task - should get ID 4 (not 2)
        inputs = iter(["Task 4", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        add_task_ui(storage)

        # Verify ID assignment
        assert storage.get(1) is not None
        assert storage.get(2) is None  # Deleted
        assert storage.get(3) is not None
        assert storage.get(4) is not None
        assert storage.count() == 3


class TestMainFunction:
    """Test main application entry point."""

    def test_main_exit_immediately(self, monkeypatch, capsys):
        """Should exit cleanly when user selects Exit."""
        # Simulate user selecting Exit (6)
        monkeypatch.setattr('builtins.input', lambda _: "6")

        main()

        captured = capsys.readouterr()
        assert "Welcome to Hackathon Todo!" in captured.out
        assert "=== Hackathon Todo Menu ===" in captured.out
        assert "Goodbye! Thanks for using Hackathon Todo." in captured.out

    def test_main_add_task_then_exit(self, monkeypatch, capsys):
        """Should add task and exit."""
        # Simulate: Add task (1), then Exit (6)
        inputs = iter(["1", "Test task", "Test description", "6"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        main()

        captured = capsys.readouterr()
        assert "Task added successfully!" in captured.out
        assert "Goodbye!" in captured.out

    def test_main_view_tasks_then_exit(self, monkeypatch, capsys):
        """Should view tasks (empty) and exit."""
        # Simulate: View tasks (2), then Exit (6)
        inputs = iter(["2", "6"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        main()

        captured = capsys.readouterr()
        assert "No tasks found" in captured.out
        assert "Goodbye!" in captured.out

    def test_main_invalid_choice_then_exit(self, monkeypatch, capsys):
        """Should handle invalid menu choice."""
        # Simulate: Invalid choice (99), then Exit (6)
        inputs = iter(["99", "6"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        main()

        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out
        assert "Please enter a number between 1 and 6" in captured.out

    def test_main_multiple_operations(self, monkeypatch, capsys):
        """Should perform multiple operations before exit."""
        # Simulate: Add (1), View (2), Mark complete (3), Exit (6)
        inputs = iter([
            "1", "Task 1", "Description 1",  # Add task
            "2",  # View tasks
            "3", "1",  # Mark task 1 complete
            "6"  # Exit
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        main()

        captured = capsys.readouterr()
        assert "Task added successfully!" in captured.out
        assert "Task 1" in captured.out
        assert "marked as complete!" in captured.out
        assert "Goodbye!" in captured.out

    def test_main_keyboard_interrupt(self, monkeypatch, capsys):
        """Should handle KeyboardInterrupt (Ctrl+C) gracefully."""
        # Simulate KeyboardInterrupt when asking for choice
        def raise_keyboard_interrupt(_):
            raise KeyboardInterrupt()

        monkeypatch.setattr('builtins.input', raise_keyboard_interrupt)

        main()

        captured = capsys.readouterr()
        assert "Welcome to Hackathon Todo!" in captured.out
        assert "Interrupted! Goodbye!" in captured.out

    def test_main_complete_workflow(self, monkeypatch, capsys):
        """Should handle complete CRUD workflow through main menu."""
        # Simulate complete workflow
        inputs = iter([
            "1", "Buy groceries", "Milk, eggs",  # Add task
            "2",  # View tasks
            "3", "1",  # Mark complete
            "4", "1", "Buy groceries and bread", "",  # Update task
            "2",  # View updated tasks
            "5", "1",  # Delete task
            "2",  # View empty list
            "6"  # Exit
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        main()

        captured = capsys.readouterr()
        # Verify all operations occurred
        assert "Task added successfully!" in captured.out
        assert "Buy groceries" in captured.out
        assert "marked as complete!" in captured.out
        assert "Task 1 updated successfully!" in captured.out
        assert "Buy groceries and bread" in captured.out
        assert "Task 1 deleted successfully!" in captured.out
        assert "No tasks found" in captured.out
        assert "Goodbye!" in captured.out
