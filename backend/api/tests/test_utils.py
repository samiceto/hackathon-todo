"""
Test utilities for Step 3 AI chatbot testing.

Provides helper functions for:
- Creating test conversations and messages
- Mocking agent responses
- Mocking MCP tool calls
- Asserting conversation state

Step 3: AI-Powered Chatbot - Test Utilities
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session

from src.models import User, Task, Conversation, Message, MessageRole


# Conversation Creation Utilities

def create_test_conversation(
    session: Session,
    user: User,
    with_messages: bool = False,
    message_count: int = 3
) -> Conversation:
    """Create a test conversation with optional message history.

    Args:
        session (Session): Database session
        user (User): User who owns the conversation
        with_messages (bool): Whether to create sample messages
        message_count (int): Number of sample messages to create

    Returns:
        Conversation: Created conversation with messages

    Example:
        conversation = create_test_conversation(session, user, with_messages=True)
        assert len(conversation.messages) > 0
    """
    conversation = Conversation(
        user_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    if with_messages:
        for i in range(message_count):
            role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            content = f"Test message {i+1}"

            message = Message(
                user_id=user.id,
                conversation_id=conversation.id,
                role=role,
                content=content,
                created_at=datetime.utcnow()
            )
            session.add(message)

        session.commit()
        session.refresh(conversation)

    return conversation


def create_test_message(
    session: Session,
    user: User,
    conversation: Conversation,
    role: MessageRole,
    content: str
) -> Message:
    """Create a test message in a conversation.

    Args:
        session (Session): Database session
        user (User): User who owns the message
        conversation (Conversation): Conversation to add message to
        role (MessageRole): Message role (user or assistant)
        content (str): Message content

    Returns:
        Message: Created message

    Example:
        message = create_test_message(
            session, user, conversation,
            MessageRole.USER, "Add a task"
        )
    """
    message = Message(
        user_id=user.id,
        conversation_id=conversation.id,
        role=role,
        content=content,
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


# Agent Response Mocking Utilities

def mock_agent_result(
    output: str,
    tool_calls: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Create a mock agent result for testing.

    Args:
        output (str): Agent's text response
        tool_calls (Optional[List[Dict]]): List of tool calls made

    Returns:
        Dict[str, Any]: Mock agent result

    Example:
        result = mock_agent_result(
            output="Task added",
            tool_calls=[{"tool": "todo_add_task", "params": {...}}]
        )
    """
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.final_output = output
    mock_result.tool_calls = tool_calls or []

    return mock_result


def mock_mcp_tool_response(
    tool_name: str,
    success: bool = True,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> str:
    """Create a mock MCP tool response.

    Args:
        tool_name (str): Name of the MCP tool
        success (bool): Whether the tool call succeeded
        data (Optional[Dict]): Tool response data
        error (Optional[str]): Error message if failed

    Returns:
        str: JSON-formatted tool response

    Example:
        response = mock_mcp_tool_response(
            tool_name="todo_add_task",
            success=True,
            data={"id": 1, "title": "Buy groceries"}
        )
    """
    import json

    if success:
        return json.dumps(data or {}, indent=2)
    else:
        return f"Error: {error or 'Tool call failed'}"


# Assertion Utilities

def assert_conversation_state(
    session: Session,
    conversation_id: int,
    expected_message_count: int,
    expected_last_role: Optional[MessageRole] = None
) -> None:
    """Assert the state of a conversation.

    Args:
        session (Session): Database session
        conversation_id (int): Conversation ID to check
        expected_message_count (int): Expected number of messages
        expected_last_role (Optional[MessageRole]): Expected role of last message

    Raises:
        AssertionError: If conversation state doesn't match expectations

    Example:
        assert_conversation_state(
            session, conv_id,
            expected_message_count=4,
            expected_last_role=MessageRole.ASSISTANT
        )
    """
    from sqlmodel import select

    conversation = session.get(Conversation, conversation_id)
    assert conversation is not None, f"Conversation {conversation_id} not found"

    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    assert len(messages) == expected_message_count, (
        f"Expected {expected_message_count} messages, got {len(messages)}"
    )

    if expected_last_role and messages:
        assert messages[-1].role == expected_last_role, (
            f"Expected last message role {expected_last_role}, got {messages[-1].role}"
        )


def assert_message_content(
    session: Session,
    message_id: int,
    expected_role: MessageRole,
    expected_content: str
) -> None:
    """Assert the content of a message.

    Args:
        session (Session): Database session
        message_id (int): Message ID to check
        expected_role (MessageRole): Expected message role
        expected_content (str): Expected message content

    Raises:
        AssertionError: If message doesn't match expectations

    Example:
        assert_message_content(
            session, msg_id,
            MessageRole.USER,
            "Add a task"
        )
    """
    message = session.get(Message, message_id)
    assert message is not None, f"Message {message_id} not found"
    assert message.role == expected_role, f"Expected role {expected_role}, got {message.role}"
    assert message.content == expected_content, (
        f"Expected content '{expected_content}', got '{message.content}'"
    )


def assert_tool_call_made(
    result: Any,
    tool_name: str,
    expected_params: Optional[Dict[str, Any]] = None
) -> None:
    """Assert that a specific tool was called in the agent result.

    Args:
        result: Agent result object
        tool_name (str): Expected tool name
        expected_params (Optional[Dict]): Expected tool parameters

    Raises:
        AssertionError: If tool was not called or params don't match

    Example:
        assert_tool_call_made(
            result, "todo_add_task",
            expected_params={"title": "Buy groceries"}
        )
    """
    tool_calls = getattr(result, "tool_calls", [])

    matching_calls = [
        call for call in tool_calls
        if call.get("tool") == tool_name or call.get("name") == tool_name
    ]

    assert len(matching_calls) > 0, f"Tool {tool_name} was not called"

    if expected_params:
        for call in matching_calls:
            params = call.get("params") or call.get("arguments", {})
            for key, value in expected_params.items():
                assert params.get(key) == value, (
                    f"Expected {key}={value}, got {params.get(key)}"
                )


# Conversation History Utilities

def build_conversation_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Build a formatted conversation history for testing.

    Args:
        messages (List[Dict]): List of message dicts with 'role' and 'content'

    Returns:
        List[Dict]: Formatted conversation history

    Example:
        history = build_conversation_history([
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ])
    """
    return [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in messages
    ]


def get_conversation_messages(
    session: Session,
    conversation_id: int
) -> List[Message]:
    """Get all messages for a conversation in chronological order.

    Args:
        session (Session): Database session
        conversation_id (int): Conversation ID

    Returns:
        List[Message]: Messages in chronological order

    Example:
        messages = get_conversation_messages(session, conv_id)
        for msg in messages:
            print(f"{msg.role}: {msg.content}")
    """
    from sqlmodel import select

    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()


# MCP Tool Testing Utilities

class MockMCPTool:
    """Mock MCP tool for testing tool behavior without actual MCP server."""

    def __init__(self, name: str, default_response: str = "Success"):
        """Initialize mock MCP tool.

        Args:
            name (str): Tool name (e.g., "todo_add_task")
            default_response (str): Default response to return
        """
        self.name = name
        self.default_response = default_response
        self.calls: List[Dict[str, Any]] = []

    async def execute(self, **params) -> str:
        """Execute the mock tool and record the call.

        Args:
            **params: Tool parameters

        Returns:
            str: Mock tool response
        """
        self.calls.append({"params": params, "timestamp": datetime.utcnow()})
        return self.default_response

    def assert_called_with(self, **expected_params):
        """Assert the tool was called with specific parameters.

        Args:
            **expected_params: Expected parameter values

        Raises:
            AssertionError: If tool wasn't called with expected params
        """
        for call in self.calls:
            if all(call["params"].get(k) == v for k, v in expected_params.items()):
                return

        raise AssertionError(
            f"Tool {self.name} was not called with params {expected_params}. "
            f"Actual calls: {self.calls}"
        )

    def reset(self):
        """Reset call history."""
        self.calls = []
