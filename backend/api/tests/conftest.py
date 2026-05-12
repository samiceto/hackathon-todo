"""
Pytest configuration and fixtures for Step 3 testing.

This module provides test fixtures for:
- Database sessions and test data
- Conversations and messages
- MCP tools and agents
- Test utilities

Step 3: AI-Powered Chatbot - Test Infrastructure
"""

import pytest
from typing import Generator
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from src.models import User, Task, Conversation, Message, MessageRole


# Database Fixtures

@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine with in-memory SQLite."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Provide a clean database session for each test."""
    with Session(engine) as session:
        yield session
        session.rollback()


# User Fixtures

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test.hash.placeholder",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="second_user")
def second_user_fixture(session: Session) -> User:
    """Create a second test user for access control tests."""
    user = User(
        email="user2@example.com",
        hashed_password="$2b$12$test.hash.placeholder2",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Task Fixtures

@pytest.fixture(name="test_task")
def test_task_fixture(session: Session, test_user: User) -> Task:
    """Create a test task."""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test description",
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="completed_task")
def completed_task_fixture(session: Session, test_user: User) -> Task:
    """Create a completed test task."""
    task = Task(
        user_id=test_user.id,
        title="Completed Task",
        description="Already done",
        completed=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# Step 3: Conversation Fixtures

@pytest.fixture(name="test_conversation")
def test_conversation_fixture(session: Session, test_user: User) -> Conversation:
    """Create a test conversation."""
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@pytest.fixture(name="conversation_with_history")
def conversation_with_history_fixture(
    session: Session,
    test_user: User,
    test_conversation: Conversation
) -> Conversation:
    """Create a conversation with message history."""
    messages = [
        Message(
            user_id=test_user.id,
            conversation_id=test_conversation.id,
            role=MessageRole.USER,
            content="Add a task to buy groceries",
            created_at=datetime.utcnow()
        ),
        Message(
            user_id=test_user.id,
            conversation_id=test_conversation.id,
            role=MessageRole.ASSISTANT,
            content="I've added a task 'Buy groceries' to your list.",
            created_at=datetime.utcnow()
        ),
        Message(
            user_id=test_user.id,
            conversation_id=test_conversation.id,
            role=MessageRole.USER,
            content="Show my tasks",
            created_at=datetime.utcnow()
        ),
    ]

    for msg in messages:
        session.add(msg)

    session.commit()

    for msg in messages:
        session.refresh(msg)

    return test_conversation


# Step 3: Message Fixtures

@pytest.fixture(name="user_message")
def user_message_fixture(
    session: Session,
    test_user: User,
    test_conversation: Conversation
) -> Message:
    """Create a test user message."""
    message = Message(
        user_id=test_user.id,
        conversation_id=test_conversation.id,
        role=MessageRole.USER,
        content="Test user message",
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@pytest.fixture(name="assistant_message")
def assistant_message_fixture(
    session: Session,
    test_user: User,
    test_conversation: Conversation
) -> Message:
    """Create a test assistant message."""
    message = Message(
        user_id=test_user.id,
        conversation_id=test_conversation.id,
        role=MessageRole.ASSISTANT,
        content="Test assistant response",
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


# Step 3: MCP and Agent Mocking Fixtures

@pytest.fixture(name="mock_mcp_server")
def mock_mcp_server_fixture():
    """Mock MCP server for testing without actual MCP connection."""
    from unittest.mock import AsyncMock, MagicMock

    mock_server = MagicMock()
    mock_server.__aenter__ = AsyncMock(return_value=mock_server)
    mock_server.__aexit__ = AsyncMock(return_value=None)

    return mock_server


@pytest.fixture(name="mock_agent_response")
def mock_agent_response_fixture():
    """Mock agent response for testing without actual OpenAI API calls."""
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.final_output = "Test agent response"
    mock_result.tool_calls = []

    return mock_result


@pytest.fixture(name="mock_runner")
def mock_runner_fixture(mock_agent_response):
    """Mock Runner.run() for testing without actual agent execution."""
    from unittest.mock import AsyncMock, patch

    with patch('agents.Runner.run', new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_agent_response
        yield mock_run


# Test Data Collections

@pytest.fixture(name="sample_task_data")
def sample_task_data_fixture():
    """Provide sample task data for testing."""
    return [
        {"title": "Buy groceries", "description": "Milk, eggs, bread"},
        {"title": "Call dentist", "description": "Schedule checkup"},
        {"title": "Write report", "description": ""},
        {"title": "Exercise", "description": "30 minutes cardio"},
    ]


@pytest.fixture(name="sample_conversations")
def sample_conversations_fixture():
    """Provide sample conversation data for testing."""
    return [
        {
            "user": "Add a task to buy groceries",
            "assistant": "I've added a task 'Buy groceries' to your list."
        },
        {
            "user": "Show my tasks",
            "assistant": "Here are your tasks:\n1. Buy groceries"
        },
        {
            "user": "Mark task 1 as complete",
            "assistant": "Task 'Buy groceries' marked as complete!"
        },
    ]
