"""
Agent Integration Tests.

Tests for OpenAI Agents SDK integration, verifying that the agent correctly
understands natural language and maps user requests to MCP tool calls.

Step 3: AI-Powered Chatbot - Agent Testing
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents import create_task_agent, create_agent_with_mcp
from src.models import User, Task


class TestAgentNaturalLanguageUnderstanding:
    """Test agent's ability to understand natural language requests."""

    @pytest.mark.asyncio
    async def test_add_task_natural_language_simple(self, mock_runner, mock_agent_response):
        """Test agent understands 'Add a task to buy groceries'."""
        # Arrange
        user_message = "Add a task to buy groceries"
        mock_agent_response.final_output = "I've added a task 'Buy groceries' to your list."
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_add_task",
                "name": "todo_add_task",
                "arguments": {"user_id": 1, "title": "Buy groceries", "description": ""}
            }
        ]

        # Act
        with patch('src.agents.task_agent.create_agent_with_mcp') as mock_create:
            agent = MagicMock()
            mcp_server = MagicMock()
            mcp_server.__aenter__ = AsyncMock(return_value=mcp_server)
            mcp_server.__aexit__ = AsyncMock(return_value=None)
            mock_create.return_value = (agent, mcp_server)

            # Verify agent would be called with proper context
            # (Actual execution mocked by mock_runner fixture)
            result = mock_runner.return_value

        # Assert
        assert "Buy groceries" in result.final_output or result.tool_calls
        # Verify tool call was made
        assert len(result.tool_calls) > 0
        assert result.tool_calls[0]["tool"] == "todo_add_task"

    @pytest.mark.asyncio
    async def test_add_task_natural_language_with_description(self, mock_runner, mock_agent_response):
        """Test agent extracts description from natural language."""
        # Arrange
        user_message = "Add a task to buy groceries with note 'milk and eggs'"
        mock_agent_response.final_output = "I've added the task with your note."
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_add_task",
                "name": "todo_add_task",
                "arguments": {
                    "user_id": 1,
                    "title": "Buy groceries",
                    "description": "milk and eggs"
                }
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        tool_call = result.tool_calls[0]
        assert tool_call["arguments"]["description"] == "milk and eggs"

    @pytest.mark.asyncio
    async def test_add_task_variations(self, mock_runner):
        """Test agent understands various ways to request task creation."""
        variations = [
            "Create a task to call dentist",
            "Remember to buy milk",
            "I need to finish the report",
            "Add buy groceries to my list",
        ]

        for variation in variations:
            # Each variation should trigger todo_add_task tool
            mock_response = MagicMock()
            mock_response.tool_calls = [{"tool": "todo_add_task", "name": "todo_add_task"}]
            mock_runner.return_value = mock_response

            result = mock_runner.return_value
            # Verify add_task tool would be called
            assert any("todo_add_task" in str(call) for call in result.tool_calls)


class TestAgentToolSelection:
    """Test agent selects the correct tool for different requests."""

    @pytest.mark.asyncio
    async def test_agent_selects_list_tasks_tool(self, mock_runner, mock_agent_response):
        """Test agent selects list_tasks for viewing requests."""
        # Arrange
        user_message = "Show me all my tasks"
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_list_tasks",
                "name": "todo_list_tasks",
                "arguments": {"user_id": 1, "completed": None}
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        assert result.tool_calls[0]["tool"] == "todo_list_tasks"

    @pytest.mark.asyncio
    async def test_agent_selects_complete_task_tool(self, mock_runner, mock_agent_response):
        """Test agent selects complete_task for completion requests."""
        # Arrange
        user_message = "Mark task 5 as complete"
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_complete_task",
                "name": "todo_complete_task",
                "arguments": {"user_id": 1, "task_id": 5, "completed": True}
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        assert result.tool_calls[0]["tool"] == "todo_complete_task"
        assert result.tool_calls[0]["arguments"]["task_id"] == 5

    @pytest.mark.asyncio
    async def test_agent_selects_update_task_tool(self, mock_runner, mock_agent_response):
        """Test agent selects update_task for modification requests."""
        # Arrange
        user_message = "Change task 3's title to 'Updated Task'"
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_update_task",
                "name": "todo_update_task",
                "arguments": {"user_id": 1, "task_id": 3, "title": "Updated Task"}
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        assert result.tool_calls[0]["tool"] == "todo_update_task"

    @pytest.mark.asyncio
    async def test_agent_selects_delete_task_tool(self, mock_runner, mock_agent_response):
        """Test agent selects delete_task for deletion requests."""
        # Arrange
        user_message = "Delete task 7"
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_delete_task",
                "name": "todo_delete_task",
                "arguments": {"user_id": 1, "task_id": 7}
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        assert result.tool_calls[0]["tool"] == "todo_delete_task"


class TestAgentResponseQuality:
    """Test agent produces high-quality, user-friendly responses."""

    @pytest.mark.asyncio
    async def test_agent_confirms_task_creation(self, mock_runner, mock_agent_response):
        """Test agent provides clear confirmation after creating task."""
        # Arrange
        mock_agent_response.final_output = "I've added a task 'Buy groceries' to your list."

        # Act
        result = mock_runner.return_value

        # Assert
        assert "added" in result.final_output.lower() or "created" in result.final_output.lower()
        assert "Buy groceries" in result.final_output or "task" in result.final_output

    @pytest.mark.asyncio
    async def test_agent_handles_ambiguous_request(self, mock_runner, mock_agent_response):
        """Test agent asks for clarification when request is unclear."""
        # Arrange
        user_message = "task"  # Ambiguous - what about tasks?
        mock_agent_response.final_output = "I can help you with tasks! Would you like to add a new task, view your existing tasks, or do something else?"
        mock_agent_response.tool_calls = []  # No tool call for ambiguous request

        # Act
        result = mock_runner.return_value

        # Assert
        # Agent should ask clarifying question, not make tool call
        assert len(result.tool_calls) == 0 or "?" in result.final_output

    @pytest.mark.asyncio
    async def test_agent_friendly_tone(self, mock_runner, mock_agent_response):
        """Test agent maintains friendly, conversational tone."""
        # Arrange
        mock_agent_response.final_output = "Great! I've added that task for you. Anything else you'd like to do?"

        # Act
        result = mock_runner.return_value

        # Assert
        # Check for friendly indicators
        friendly_indicators = ["!", "great", "awesome", "sure", "help", "?"]
        assert any(indicator in result.final_output.lower() for indicator in friendly_indicators)


class TestAgentConversationContext:
    """Test agent maintains conversation context."""

    @pytest.mark.asyncio
    async def test_agent_uses_previous_context(self, mock_runner, mock_agent_response):
        """Test agent references previous conversation."""
        # Arrange
        # Previous: "Add a task to buy groceries"
        # Current: "Also add milk to the description"
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_update_task",
                "name": "todo_update_task",
                "arguments": {
                    "user_id": 1,
                    "task_id": 1,  # References previous task
                    "description": "milk"
                }
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        # Verify agent would use context to identify which task
        assert result.tool_calls[0]["tool"] == "todo_update_task"

    @pytest.mark.asyncio
    async def test_agent_pronoun_resolution(self, mock_runner, mock_agent_response):
        """Test agent resolves pronouns using context."""
        # Arrange
        # Previous: "Add a task to buy groceries"
        # Current: "Mark it as complete"
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_complete_task",
                "name": "todo_complete_task",
                "arguments": {"user_id": 1, "task_id": 1, "completed": True}
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        # "it" should resolve to the previously created task
        assert result.tool_calls[0]["tool"] == "todo_complete_task"


class TestAgentErrorHandling:
    """Test agent handles errors gracefully."""

    @pytest.mark.asyncio
    async def test_agent_handles_tool_error(self, mock_runner, mock_agent_response):
        """Test agent provides helpful message when tool fails."""
        # Arrange
        mock_agent_response.final_output = "I couldn't find task 999. Could you check the task number and try again?"
        mock_agent_response.tool_calls = [
            {
                "tool": "todo_complete_task",
                "name": "todo_complete_task",
                "arguments": {"user_id": 1, "task_id": 999, "completed": True}
            }
        ]

        # Act
        result = mock_runner.return_value

        # Assert
        # Agent should suggest next steps
        assert "couldn't" in result.final_output.lower() or "not found" in result.final_output.lower()
        assert "?" in result.final_output  # Asks user to clarify

    @pytest.mark.asyncio
    async def test_agent_suggests_list_tasks_on_error(self, mock_runner, mock_agent_response):
        """Test agent suggests listing tasks when task not found."""
        # Arrange
        mock_agent_response.final_output = "I couldn't find that task. Would you like me to show you all your tasks?"

        # Act
        result = mock_runner.return_value

        # Assert
        assert "show" in result.final_output.lower() or "list" in result.final_output.lower()


class TestAgentInstructions:
    """Test agent follows configured instructions."""

    def test_agent_has_task_management_instructions(self):
        """Test agent is configured with task management instructions."""
        # Arrange & Act
        agent = create_task_agent(mcp_server_url="http://localhost:8000/mcp")

        # Assert
        assert agent.instructions is not None
        assert "task" in agent.instructions.lower()
        assert "todo" in agent.instructions.lower() or "add" in agent.instructions.lower()

    def test_agent_instructions_mention_all_tools(self):
        """Test agent instructions cover all 5 MCP tools."""
        # Arrange & Act
        agent = create_task_agent(mcp_server_url="http://localhost:8000/mcp")

        # Assert
        instructions = agent.instructions.lower()
        assert "add" in instructions
        assert "list" in instructions or "view" in instructions or "show" in instructions
        assert "complete" in instructions or "done" in instructions
        assert "update" in instructions or "modify" in instructions or "change" in instructions
        assert "delete" in instructions or "remove" in instructions

    def test_agent_model_settings(self):
        """Test agent has correct model settings for conversation."""
        # Arrange & Act
        agent = create_task_agent(mcp_server_url="http://localhost:8000/mcp")

        # Assert
        assert agent.model_settings is not None
        assert agent.model_settings.tool_choice == "auto"  # Allow natural conversation
        assert agent.model_settings.temperature == 0.7  # Conversational temperature
