"""
Unit tests for TaskStorage class.

Tests cover:
- Task creation and ID assignment
- CRUD operations (Create, Read, Update, Delete)
- Edge cases (non-existent IDs, empty storage)
- Data integrity and sorting
"""

import pytest

from hackathon_todo.models import Task
from hackathon_todo.storage import TaskStorage


class TestTaskStorageAdd:
    """Test task creation and storage."""

    def test_add_task_increments_id(self, storage):
        """Task IDs should increment sequentially starting from 1."""
        task1 = storage.add("Task 1")
        task2 = storage.add("Task 2")
        assert task1.id == 1
        assert task2.id == 2

    def test_add_task_with_description(self, storage):
        """Task should be created with title and description."""
        task = storage.add("Test Task", "Test Description")
        assert task.title == "Test Task"
        assert task.description == "Test Description"

    def test_add_task_without_description(self, storage):
        """Task should be created with title only (empty description)."""
        task = storage.add("Test Task")
        assert task.title == "Test Task"
        assert task.description == ""

    def test_add_task_returns_task_instance(self, storage):
        """add() should return the created Task instance."""
        task = storage.add("Test")
        assert isinstance(task, Task)
        assert task.completed is False

    def test_add_task_with_empty_title_raises_error(self, storage):
        """Adding task with empty title should fail."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            storage.add("")

    def test_add_multiple_tasks(self, storage):
        """Multiple tasks should be stored independently."""
        task1 = storage.add("Task 1", "Description 1")
        task2 = storage.add("Task 2", "Description 2")
        task3 = storage.add("Task 3", "Description 3")
        assert storage.count() == 3
        assert task1.id != task2.id != task3.id


class TestTaskStorageGet:
    """Test task retrieval operations."""

    def test_get_existing_task(self, storage):
        """get() should return the task if it exists."""
        task = storage.add("Test Task")
        retrieved = storage.get(task.id)
        assert retrieved == task
        assert retrieved.title == "Test Task"

    def test_get_nonexistent_task_returns_none(self, storage):
        """get() should return None for non-existent task ID."""
        assert storage.get(999) is None

    def test_get_from_empty_storage_returns_none(self, storage):
        """get() should return None when storage is empty."""
        assert storage.get(1) is None

    def test_get_returns_same_instance(self, storage):
        """get() should return the same instance (not a copy)."""
        task = storage.add("Test")
        retrieved1 = storage.get(task.id)
        retrieved2 = storage.get(task.id)
        assert retrieved1 is retrieved2
        assert retrieved1 is task


class TestTaskStorageGetAll:
    """Test retrieving all tasks."""

    def test_get_all_returns_sorted_list(self, storage):
        """get_all() should return tasks sorted by ID."""
        task1 = storage.add("Task 1")
        task2 = storage.add("Task 2")
        task3 = storage.add("Task 3")
        all_tasks = storage.get_all()
        assert len(all_tasks) == 3
        assert all_tasks[0].id < all_tasks[1].id < all_tasks[2].id

    def test_get_all_empty_storage(self, storage):
        """get_all() should return empty list when storage is empty."""
        all_tasks = storage.get_all()
        assert all_tasks == []
        assert len(all_tasks) == 0

    def test_get_all_single_task(self, storage):
        """get_all() should work with single task."""
        task = storage.add("Solo Task")
        all_tasks = storage.get_all()
        assert len(all_tasks) == 1
        assert all_tasks[0] == task

    def test_get_all_preserves_order_after_delete(self, storage):
        """get_all() should maintain sort order even after deletions."""
        task1 = storage.add("Task 1")
        task2 = storage.add("Task 2")
        task3 = storage.add("Task 3")
        storage.delete(task2.id)
        all_tasks = storage.get_all()
        assert len(all_tasks) == 2
        assert all_tasks[0].id == 1
        assert all_tasks[1].id == 3


class TestTaskStorageUpdate:
    """Test task update operations."""

    def test_update_existing_task(self, storage):
        """update() should modify task title and description."""
        task = storage.add("Original")
        updated = storage.update(task.id, title="Updated")
        assert updated is not None
        assert updated.title == "Updated"
        assert storage.get(task.id).title == "Updated"

    def test_update_nonexistent_task_returns_none(self, storage):
        """update() should return None for non-existent task."""
        result = storage.update(999, title="Test")
        assert result is None

    def test_update_title_only(self, storage):
        """Updating only title should preserve description."""
        task = storage.add("Original", "Keep this")
        storage.update(task.id, title="New Title")
        retrieved = storage.get(task.id)
        assert retrieved.title == "New Title"
        assert retrieved.description == "Keep this"

    def test_update_description_only(self, storage):
        """Updating only description should preserve title."""
        task = storage.add("Keep this", "Original")
        storage.update(task.id, description="New Desc")
        retrieved = storage.get(task.id)
        assert retrieved.title == "Keep this"
        assert retrieved.description == "New Desc"

    def test_update_both_fields(self, storage):
        """Both title and description can be updated together."""
        task = storage.add("Old Title", "Old Desc")
        storage.update(task.id, title="New Title", description="New Desc")
        retrieved = storage.get(task.id)
        assert retrieved.title == "New Title"
        assert retrieved.description == "New Desc"

    def test_update_with_empty_title_raises_error(self, storage):
        """Updating to empty title should fail."""
        task = storage.add("Original")
        with pytest.raises(ValueError, match="title cannot be empty"):
            storage.update(task.id, title="")


class TestTaskStorageToggleComplete:
    """Test task completion toggling."""

    def test_toggle_complete_existing_task(self, storage):
        """toggle_complete() should toggle completion status."""
        task = storage.add("Test")
        assert task.completed is False
        storage.toggle_complete(task.id)
        assert storage.get(task.id).completed is True

    def test_toggle_complete_nonexistent_task_returns_none(self, storage):
        """toggle_complete() should return None for non-existent task."""
        result = storage.toggle_complete(999)
        assert result is None

    def test_toggle_complete_multiple_times(self, storage):
        """toggle_complete() should flip status on each call."""
        task = storage.add("Test")
        storage.toggle_complete(task.id)
        assert storage.get(task.id).completed is True
        storage.toggle_complete(task.id)
        assert storage.get(task.id).completed is False
        storage.toggle_complete(task.id)
        assert storage.get(task.id).completed is True

    def test_toggle_complete_returns_updated_task(self, storage):
        """toggle_complete() should return the updated Task instance."""
        task = storage.add("Test")
        result = storage.toggle_complete(task.id)
        assert result is not None
        assert result.completed is True
        assert result == task


class TestTaskStorageDelete:
    """Test task deletion operations."""

    def test_delete_existing_task(self, storage):
        """delete() should remove task and return True."""
        task = storage.add("Test")
        assert storage.delete(task.id) is True
        assert storage.get(task.id) is None

    def test_delete_nonexistent_task_returns_false(self, storage):
        """delete() should return False for non-existent task."""
        assert storage.delete(999) is False

    def test_delete_reduces_count(self, storage):
        """Deleting task should reduce total count."""
        storage.add("Task 1")
        task2 = storage.add("Task 2")
        storage.add("Task 3")
        assert storage.count() == 3
        storage.delete(task2.id)
        assert storage.count() == 2

    def test_delete_is_idempotent(self, storage):
        """Deleting same task multiple times should be safe."""
        task = storage.add("Test")
        assert storage.delete(task.id) is True
        assert storage.delete(task.id) is False
        assert storage.delete(task.id) is False

    def test_delete_from_multiple_tasks(self, storage):
        """Deleting one task should not affect others."""
        task1 = storage.add("Task 1")
        task2 = storage.add("Task 2")
        task3 = storage.add("Task 3")
        storage.delete(task2.id)
        assert storage.get(task1.id) is not None
        assert storage.get(task2.id) is None
        assert storage.get(task3.id) is not None


class TestTaskStorageCount:
    """Test task counting."""

    def test_count_empty_storage(self, storage):
        """count() should return 0 for empty storage."""
        assert storage.count() == 0

    def test_count_after_adding_tasks(self, storage):
        """count() should reflect number of tasks added."""
        storage.add("Task 1")
        assert storage.count() == 1
        storage.add("Task 2")
        assert storage.count() == 2
        storage.add("Task 3")
        assert storage.count() == 3

    def test_count_after_deleting_tasks(self, storage):
        """count() should decrease when tasks are deleted."""
        task1 = storage.add("Task 1")
        task2 = storage.add("Task 2")
        assert storage.count() == 2
        storage.delete(task1.id)
        assert storage.count() == 1
        storage.delete(task2.id)
        assert storage.count() == 0


class TestTaskStorageIntegration:
    """Integration tests for complex scenarios."""

    def test_full_crud_workflow(self, storage):
        """Test complete CRUD workflow on a single task."""
        # Create
        task = storage.add("Original Task", "Original Description")
        assert task.id == 1
        assert storage.count() == 1

        # Read
        retrieved = storage.get(task.id)
        assert retrieved.title == "Original Task"

        # Update
        storage.update(task.id, title="Updated Task")
        assert storage.get(task.id).title == "Updated Task"

        # Toggle completion
        storage.toggle_complete(task.id)
        assert storage.get(task.id).completed is True

        # Delete
        storage.delete(task.id)
        assert storage.get(task.id) is None
        assert storage.count() == 0

    def test_multiple_tasks_independent(self, storage):
        """Multiple tasks should operate independently."""
        task1 = storage.add("Task 1")
        task2 = storage.add("Task 2")
        
        # Modify task1
        storage.update(task1.id, title="Modified 1")
        storage.toggle_complete(task1.id)
        
        # Task2 should be unaffected
        assert storage.get(task2.id).title == "Task 2"
        assert storage.get(task2.id).completed is False

    def test_storage_with_tasks_fixture(self, storage_with_tasks):
        """Test using pre-populated storage fixture."""
        assert storage_with_tasks.count() == 3
        all_tasks = storage_with_tasks.get_all()
        assert len(all_tasks) == 3
        # Third task should be completed (from fixture)
        assert all_tasks[2].completed is True
