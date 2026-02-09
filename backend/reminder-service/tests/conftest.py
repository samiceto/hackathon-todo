"""Pytest fixtures for reminder service tests."""

import pytest
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.models import Reminder


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session.

    Uses in-memory SQLite for fast, isolated tests.

    Yields:
        SQLModel Session for testing
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    with Session(engine) as session:
        yield session

    # Cleanup
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def sample_reminder(session: Session):
    """Create a sample reminder for testing.

    Args:
        session: Database session

    Returns:
        Sample Reminder record
    """
    now = datetime.now(timezone.utc)
    reminder_at = now + timedelta(minutes=30)

    reminder = Reminder(
        task_id=42,
        user_id=1,
        reminder_at=reminder_at,
        sent=False
    )

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return reminder


@pytest.fixture
def due_reminder(session: Session):
    """Create a due reminder (reminder_at in the past).

    Args:
        session: Database session

    Returns:
        Due Reminder record
    """
    now = datetime.now(timezone.utc)
    reminder_at = now - timedelta(minutes=5)  # 5 minutes ago

    reminder = Reminder(
        task_id=100,
        user_id=1,
        reminder_at=reminder_at,
        sent=False
    )

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return reminder


@pytest.fixture
def task_created_event():
    """Sample task.created event payload.

    Returns:
        Event dict matching Dapr CloudEvents format
    """
    now = datetime.now(timezone.utc)
    due_date = now + timedelta(hours=2)

    return {
        "data": {
            "event_id": "evt_test_123",
            "event_type": "task.created",
            "timestamp": now.isoformat(),
            "user_id": 1,
            "payload": {
                "task_id": 42,
                "title": "Test Task",
                "description": "Test description",
                "priority": "high",
                "due_date": due_date.isoformat(),
                "reminder_offset": 30  # 30 minutes before due
            }
        }
    }


@pytest.fixture
def task_updated_event():
    """Sample task.updated event payload.

    Returns:
        Event dict matching Dapr CloudEvents format
    """
    now = datetime.now(timezone.utc)
    due_date = now + timedelta(hours=3)  # Changed due date

    return {
        "data": {
            "event_id": "evt_test_456",
            "event_type": "task.updated",
            "timestamp": now.isoformat(),
            "user_id": 1,
            "payload": {
                "task_id": 42,
                "title": "Updated Task",
                "description": "Updated description",
                "completed": False,
                "priority": "urgent",
                "due_date": due_date.isoformat(),
                "reminder_offset": 60  # Changed to 60 minutes before
            }
        }
    }


@pytest.fixture
def task_completed_event():
    """Sample task.completed event payload.

    Returns:
        Event dict matching Dapr CloudEvents format
    """
    now = datetime.now(timezone.utc)

    return {
        "data": {
            "event_id": "evt_test_789",
            "event_type": "task.completed",
            "timestamp": now.isoformat(),
            "user_id": 1,
            "payload": {
                "task_id": 42,
                "title": "Completed Task",
                "completed_at": now.isoformat()
            }
        }
    }


@pytest.fixture
def task_deleted_event():
    """Sample task.deleted event payload.

    Returns:
        Event dict matching Dapr CloudEvents format
    """
    now = datetime.now(timezone.utc)

    return {
        "data": {
            "event_id": "evt_test_999",
            "event_type": "task.deleted",
            "timestamp": now.isoformat(),
            "user_id": 1,
            "payload": {
                "task_id": 42,
                "title": "Deleted Task"
            }
        }
    }
