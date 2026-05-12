"""
MCP Tools Contract Tests.

Tests for individual MCP tool behavior, ensuring tools correctly handle
inputs, validate parameters, and return expected outputs.

Step 3: AI-Powered Chatbot - MCP Tool Testing
"""

import pytest
import json
from datetime import datetime

from src.models import User, Task
from src.mcp.server import (
    AddTaskInput,
    ListTasksInput,
    CompleteTaskInput,
    UpdateTaskInput,
    DeleteTaskInput,
    todo_add_task,
    todo_list_tasks,
    todo_complete_task,
    todo_update_task,
    todo_delete_task,
    ResponseFormat
)


class TestAddTaskTool:
    """Test todo_add_task MCP tool."""

    @pytest.mark.asyncio
    async def test_add_task_tool_basic(self, session, test_user):
        """Test adding a basic task through MCP tool."""
        # Arrange
        params = AddTaskInput(
            user_id=test_user.id,
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        # Act
        result = await todo_add_task(params)

        # Assert
        assert result is not None
        result_data = json.loads(result)
        assert result_data["title"] == "Buy groceries"
        assert result_data["description"] == "Milk, eggs, bread"
        assert result_data["completed"] is False
        assert "id" in result_data
        assert "created_at" in result_data

    @pytest.mark.asyncio
    async def test_add_task_tool_title_only(self, session, test_user):
        """Test adding a task with title only (no description)."""
        # Arrange
        params = AddTaskInput(
            user_id=test_user.id,
            title="Quick task"
        )

        # Act
        result = await todo_add_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["title"] == "Quick task"
        assert result_data["description"] == ""

    @pytest.mark.asyncio
    async def test_add_task_tool_validation_empty_title(self, test_user):
        """Test that empty title is rejected."""
        # Arrange & Act & Assert
        with pytest.raises(Exception):  # Pydantic validation error
            params = AddTaskInput(
                user_id=test_user.id,
                title="   ",  # Whitespace only
                description="Test"
            )

    @pytest.mark.asyncio
    async def test_add_task_tool_long_title(self, session, test_user):
        """Test adding a task with maximum length title."""
        # Arrange
        long_title = "A" * 500  # Max length
        params = AddTaskInput(
            user_id=test_user.id,
            title=long_title
        )

        # Act
        result = await todo_add_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["title"] == long_title


class TestListTasksTool:
    """Test todo_list_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_tool_empty(self, session, test_user):
        """Test listing tasks when user has no tasks."""
        # Arrange
        params = ListTasksInput(
            user_id=test_user.id,
            response_format=ResponseFormat.JSON
        )

        # Act
        result = await todo_list_tasks(params)

        # Assert
        assert result == "No tasks found"

    @pytest.mark.asyncio
    async def test_list_tasks_tool_json_format(self, session, test_user, test_task):
        """Test listing tasks in JSON format."""
        # Arrange
        params = ListTasksInput(
            user_id=test_user.id,
            response_format=ResponseFormat.JSON
        )

        # Act
        result = await todo_list_tasks(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["total"] == 1
        assert result_data["count"] == 1
        assert len(result_data["tasks"]) == 1
        assert result_data["tasks"][0]["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_list_tasks_tool_markdown_format(self, session, test_user, test_task):
        """Test listing tasks in Markdown format."""
        # Arrange
        params = ListTasksInput(
            user_id=test_user.id,
            response_format=ResponseFormat.MARKDOWN
        )

        # Act
        result = await todo_list_tasks(params)

        # Assert
        assert "Tasks for User" in result
        assert "Test Task" in result
        assert "○" in result  # Incomplete task indicator

    @pytest.mark.asyncio
    async def test_list_tasks_tool_filter_completed(self, session, test_user, test_task, completed_task):
        """Test filtering for completed tasks only."""
        # Arrange
        params = ListTasksInput(
            user_id=test_user.id,
            completed=True,
            response_format=ResponseFormat.JSON
        )

        # Act
        result = await todo_list_tasks(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["total"] == 1
        assert result_data["tasks"][0]["completed"] is True
        assert result_data["tasks"][0]["title"] == "Completed Task"

    @pytest.mark.asyncio
    async def test_list_tasks_tool_pagination(self, session, test_user):
        """Test pagination with limit and offset."""
        # Create 5 tasks
        for i in range(5):
            task = Task(
                user_id=test_user.id,
                title=f"Task {i+1}",
                description="",
                completed=False
            )
            session.add(task)
        session.commit()

        # Arrange
        params = ListTasksInput(
            user_id=test_user.id,
            limit=2,
            offset=0,
            response_format=ResponseFormat.JSON
        )

        # Act
        result = await todo_list_tasks(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["total"] == 5
        assert result_data["count"] == 2
        assert result_data["has_more"] is True
        assert result_data["next_offset"] == 2


class TestCompleteTaskTool:
    """Test todo_complete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_complete_task_tool(self, session, test_user, test_task):
        """Test marking a task as complete."""
        # Arrange
        params = CompleteTaskInput(
            user_id=test_user.id,
            task_id=test_task.id,
            completed=True
        )

        # Act
        result = await todo_complete_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["id"] == test_task.id
        assert result_data["completed"] is True

    @pytest.mark.asyncio
    async def test_uncomplete_task_tool(self, session, test_user, completed_task):
        """Test marking a completed task as incomplete."""
        # Arrange
        params = CompleteTaskInput(
            user_id=test_user.id,
            task_id=completed_task.id,
            completed=False
        )

        # Act
        result = await todo_complete_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["completed"] is False

    @pytest.mark.asyncio
    async def test_complete_task_tool_not_found(self, session, test_user):
        """Test completing a non-existent task."""
        # Arrange
        params = CompleteTaskInput(
            user_id=test_user.id,
            task_id=99999,
            completed=True
        )

        # Act
        result = await todo_complete_task(params)

        # Assert
        assert "Error: Task not found" in result


class TestUpdateTaskTool:
    """Test todo_update_task MCP tool."""

    @pytest.mark.asyncio
    async def test_update_task_tool_title(self, session, test_user, test_task):
        """Test updating task title."""
        # Arrange
        params = UpdateTaskInput(
            user_id=test_user.id,
            task_id=test_task.id,
            title="Updated Title"
        )

        # Act
        result = await todo_update_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["title"] == "Updated Title"
        assert result_data["description"] == test_task.description  # Unchanged

    @pytest.mark.asyncio
    async def test_update_task_tool_description(self, session, test_user, test_task):
        """Test updating task description."""
        # Arrange
        params = UpdateTaskInput(
            user_id=test_user.id,
            task_id=test_task.id,
            description="New description"
        )

        # Act
        result = await todo_update_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["description"] == "New description"
        assert result_data["title"] == test_task.title  # Unchanged

    @pytest.mark.asyncio
    async def test_update_task_tool_both_fields(self, session, test_user, test_task):
        """Test updating both title and description."""
        # Arrange
        params = UpdateTaskInput(
            user_id=test_user.id,
            task_id=test_task.id,
            title="New Title",
            description="New Description"
        )

        # Act
        result = await todo_update_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["title"] == "New Title"
        assert result_data["description"] == "New Description"

    @pytest.mark.asyncio
    async def test_update_task_tool_no_fields(self, session, test_user, test_task):
        """Test updating with no fields specified."""
        # Arrange
        params = UpdateTaskInput(
            user_id=test_user.id,
            task_id=test_task.id
        )

        # Act
        result = await todo_update_task(params)

        # Assert
        assert "Error: No fields to update" in result


class TestDeleteTaskTool:
    """Test todo_delete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_task_tool(self, session, test_user, test_task):
        """Test deleting a task."""
        # Arrange
        task_id = test_task.id
        params = DeleteTaskInput(
            user_id=test_user.id,
            task_id=task_id
        )

        # Act
        result = await todo_delete_task(params)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["deleted_task_id"] == task_id

        # Verify task is deleted from database
        deleted_task = session.get(Task, task_id)
        assert deleted_task is None

    @pytest.mark.asyncio
    async def test_delete_task_tool_not_found(self, session, test_user):
        """Test deleting a non-existent task."""
        # Arrange
        params = DeleteTaskInput(
            user_id=test_user.id,
            task_id=99999
        )

        # Act
        result = await todo_delete_task(params)

        # Assert
        assert "Error: Task not found" in result


class TestAccessControl:
    """Test that MCP tools enforce user ownership."""

    @pytest.mark.asyncio
    async def test_list_tasks_isolation(self, session, test_user, second_user):
        """Test that users only see their own tasks."""
        # Create task for test_user
        task1 = Task(user_id=test_user.id, title="User 1 Task", description="", completed=False)
        # Create task for second_user
        task2 = Task(user_id=second_user.id, title="User 2 Task", description="", completed=False)
        session.add(task1)
        session.add(task2)
        session.commit()

        # List tasks for test_user
        params = ListTasksInput(
            user_id=test_user.id,
            response_format=ResponseFormat.JSON
        )
        result = await todo_list_tasks(params)

        # Assert only sees their own task
        result_data = json.loads(result)
        assert result_data["total"] == 1
        assert result_data["tasks"][0]["title"] == "User 1 Task"

    @pytest.mark.asyncio
    async def test_complete_task_access_control(self, session, test_user, second_user):
        """Test that users cannot modify other users' tasks."""
        # Create task for second_user
        task = Task(user_id=second_user.id, title="Other User Task", description="", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)

        # Try to complete task as test_user
        params = CompleteTaskInput(
            user_id=test_user.id,
            task_id=task.id,
            completed=True
        )
        result = await todo_complete_task(params)

        # Assert access denied
        assert "Error: Task not found" in result
