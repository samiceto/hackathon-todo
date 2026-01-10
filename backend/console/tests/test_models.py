"""
Unit tests for Task dataclass.

Tests cover:
- Task creation with valid and invalid data
- Title validation (empty, whitespace)
- Task state changes (toggle completion)
- Task updates with validation
"""

import pytest
from datetime import datetime

from hackathon_todo.models import Task


class TestTaskCreation:
    """Test Task instantiation and validation."""

    def test_task_creation_with_valid_data(self):
        """Task should be created successfully with valid title and description."""
        task = Task(id=1, title="Test Task", description="Test Description")
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_task_creation_with_minimal_data(self):
        """Task should be created with only required fields (id and title)."""
        task = Task(id=1, title="Minimal Task")
        assert task.id == 1
        assert task.title == "Minimal Task"
        assert task.description == ""
        assert task.completed is False

    def test_task_creation_strips_whitespace(self):
        """Task should strip leading/trailing whitespace from title and description."""
        task = Task(id=1, title="  Padded Title  ", description="  Padded Desc  ")
        assert task.title == "Padded Title"
        assert task.description == "Padded Desc"

    def test_task_creation_with_empty_title_raises_error(self):
        """Task creation should fail with empty title."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task(id=1, title="", description="Test")

    def test_task_creation_with_whitespace_title_raises_error(self):
        """Task creation should fail with whitespace-only title."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task(id=1, title="   ", description="Test")


class TestTaskToggleCompleted:
    """Test task completion status toggling."""

    def test_task_toggle_completed(self):
        """Task completion status should toggle correctly."""
        task = Task(id=1, title="Test")
        assert task.completed is False
        task.toggle_completed()
        assert task.completed is True
        task.toggle_completed()
        assert task.completed is False

    def test_task_toggle_completed_multiple_times(self):
        """Task should handle multiple toggles correctly."""
        task = Task(id=1, title="Test")
        for _ in range(5):
            task.toggle_completed()
        assert task.completed is True  # Odd number of toggles


class TestTaskUpdate:
    """Test task attribute updates."""

    def test_task_update_title(self):
        """Task title should be updated correctly."""
        task = Task(id=1, title="Original")
        task.update(title="Updated")
        assert task.title == "Updated"

    def test_task_update_description(self):
        """Task description should be updated correctly."""
        task = Task(id=1, title="Test", description="Original")
        task.update(description="Updated")
        assert task.description == "Updated"

    def test_task_update_both_fields(self):
        """Both title and description should be updated together."""
        task = Task(id=1, title="Original Title", description="Original Desc")
        task.update(title="New Title", description="New Desc")
        assert task.title == "New Title"
        assert task.description == "New Desc"

    def test_task_update_title_only(self):
        """Updating only title should preserve description."""
        task = Task(id=1, title="Original", description="Keep this")
        task.update(title="Updated")
        assert task.title == "Updated"
        assert task.description == "Keep this"

    def test_task_update_description_only(self):
        """Updating only description should preserve title."""
        task = Task(id=1, title="Keep this", description="Original")
        task.update(description="Updated")
        assert task.title == "Keep this"
        assert task.description == "Updated"

    def test_task_update_with_empty_title_raises_error(self):
        """Updating to empty title should fail."""
        task = Task(id=1, title="Original")
        with pytest.raises(ValueError, match="title cannot be empty"):
            task.update(title="")

    def test_task_update_with_whitespace_title_raises_error(self):
        """Updating to whitespace-only title should fail."""
        task = Task(id=1, title="Original")
        with pytest.raises(ValueError, match="title cannot be empty"):
            task.update(title="   ")

    def test_task_update_strips_whitespace(self):
        """Update should strip whitespace from new values."""
        task = Task(id=1, title="Original", description="Original")
        task.update(title="  New Title  ", description="  New Desc  ")
        assert task.title == "New Title"
        assert task.description == "New Desc"

    def test_task_update_empty_description_allowed(self):
        """Empty description should be allowed in updates."""
        task = Task(id=1, title="Test", description="Original")
        task.update(description="")
        assert task.description == ""
