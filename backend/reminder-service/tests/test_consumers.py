"""Tests for event consumers."""

import pytest
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select

from src.consumers import (
    get_task_created_consumer,
    get_task_updated_consumer,
    get_task_completed_consumer,
    get_task_deleted_consumer,
)
from src.models import Reminder


class TestTaskCreatedConsumer:
    """Tests for TaskCreatedConsumer."""

    @pytest.mark.asyncio
    async def test_create_reminder_success(self, session: Session, task_created_event):
        """Test successful reminder creation from task.created event."""
        consumer = get_task_created_consumer()

        # Process event
        result = await consumer.handle_event(task_created_event, session)

        # Verify result
        assert result["status"] == "success"
        assert result["task_id"] == 42

        # Verify reminder created in DB
        statement = select(Reminder).where(Reminder.task_id == 42)
        reminder = session.exec(statement).first()

        assert reminder is not None
        assert reminder.task_id == 42
        assert reminder.user_id == 1
        assert reminder.sent is False

    @pytest.mark.asyncio
    async def test_skip_no_due_date(self, session: Session, task_created_event):
        """Test skipping reminder when task has no due_date."""
        # Remove due_date
        task_created_event["data"]["payload"]["due_date"] = None

        consumer = get_task_created_consumer()
        result = await consumer.handle_event(task_created_event, session)

        # Verify skipped
        assert result["status"] == "skipped"
        assert result["reason"] == "no_due_date_or_reminder"

        # Verify no reminder created
        statement = select(Reminder).where(Reminder.task_id == 42)
        reminder = session.exec(statement).first()
        assert reminder is None

    @pytest.mark.asyncio
    async def test_skip_no_reminder_offset(self, session: Session, task_created_event):
        """Test skipping reminder when task has no reminder_offset."""
        # Remove reminder_offset
        task_created_event["data"]["payload"]["reminder_offset"] = None

        consumer = get_task_created_consumer()
        result = await consumer.handle_event(task_created_event, session)

        # Verify skipped
        assert result["status"] == "skipped"
        assert result["reason"] == "no_due_date_or_reminder"

    @pytest.mark.asyncio
    async def test_skip_reminder_in_past(self, session: Session, task_created_event):
        """Test skipping reminder when reminder_at is in the past."""
        # Set due_date in the past
        now = datetime.now(timezone.utc)
        past_due_date = now - timedelta(hours=1)
        task_created_event["data"]["payload"]["due_date"] = past_due_date.isoformat()

        consumer = get_task_created_consumer()
        result = await consumer.handle_event(task_created_event, session)

        # Verify skipped
        assert result["status"] == "skipped"
        assert result["reason"] == "reminder_in_past"

    @pytest.mark.asyncio
    async def test_idempotency(self, session: Session, task_created_event):
        """Test idempotency - duplicate event_id is skipped."""
        consumer = get_task_created_consumer()

        # Process event first time
        result1 = await consumer.handle_event(task_created_event, session)
        assert result1["status"] == "success"

        # Process same event again (duplicate)
        result2 = await consumer.handle_event(task_created_event, session)
        assert result2["status"] == "duplicate"

        # Verify only one reminder created
        statement = select(Reminder).where(Reminder.task_id == 42)
        reminders = session.exec(statement).all()
        assert len(reminders) == 1


class TestTaskUpdatedConsumer:
    """Tests for TaskUpdatedConsumer."""

    @pytest.mark.asyncio
    async def test_update_reminder_success(self, session: Session, sample_reminder, task_updated_event):
        """Test successful reminder update from task.updated event."""
        # Use existing reminder's task_id
        task_updated_event["data"]["payload"]["task_id"] = sample_reminder.task_id

        consumer = get_task_updated_consumer()
        result = await consumer.handle_event(task_updated_event, session)

        # Verify result
        assert result["status"] == "updated"
        assert result["reminder_id"] == sample_reminder.id

        # Verify reminder updated in DB
        session.refresh(sample_reminder)
        assert sample_reminder.sent is False  # Reset sent flag

    @pytest.mark.asyncio
    async def test_create_reminder_if_not_exists(self, session: Session, task_updated_event):
        """Test creating reminder when task.updated but no reminder exists."""
        consumer = get_task_updated_consumer()
        result = await consumer.handle_event(task_updated_event, session)

        # Verify result
        assert result["status"] == "created"

        # Verify reminder created
        statement = select(Reminder).where(Reminder.task_id == 42)
        reminder = session.exec(statement).first()
        assert reminder is not None

    @pytest.mark.asyncio
    async def test_delete_reminder_no_due_date(self, session: Session, sample_reminder, task_updated_event):
        """Test deleting reminder when due_date is removed."""
        # Use existing reminder's task_id
        task_updated_event["data"]["payload"]["task_id"] = sample_reminder.task_id
        # Remove due_date
        task_updated_event["data"]["payload"]["due_date"] = None

        consumer = get_task_updated_consumer()
        result = await consumer.handle_event(task_updated_event, session)

        # Verify result
        assert result["status"] == "deleted"

        # Verify reminder deleted
        statement = select(Reminder).where(Reminder.id == sample_reminder.id)
        reminder = session.exec(statement).first()
        assert reminder is None

    @pytest.mark.asyncio
    async def test_skip_unchanged(self, session: Session, sample_reminder, task_updated_event):
        """Test skipping update when reminder_at unchanged."""
        # Set same reminder_at as existing reminder
        task_updated_event["data"]["payload"]["task_id"] = sample_reminder.task_id
        task_updated_event["data"]["payload"]["due_date"] = (
            sample_reminder.reminder_at + timedelta(minutes=30)
        ).isoformat()
        task_updated_event["data"]["payload"]["reminder_offset"] = 30

        consumer = get_task_updated_consumer()
        result = await consumer.handle_event(task_updated_event, session)

        # Verify unchanged
        assert result["status"] == "unchanged"


class TestTaskCompletedConsumer:
    """Tests for TaskCompletedConsumer."""

    @pytest.mark.asyncio
    async def test_cancel_reminder_success(self, session: Session, sample_reminder, task_completed_event):
        """Test canceling reminder when task is completed."""
        # Use existing reminder's task_id
        task_completed_event["data"]["payload"]["task_id"] = sample_reminder.task_id

        consumer = get_task_completed_consumer()
        result = await consumer.handle_event(task_completed_event, session)

        # Verify result
        assert result["status"] == "cancelled"
        assert result["reminder_id"] == sample_reminder.id

        # Verify reminder marked as sent
        session.refresh(sample_reminder)
        assert sample_reminder.sent is True

    @pytest.mark.asyncio
    async def test_no_reminder_to_cancel(self, session: Session, task_completed_event):
        """Test handling completion when no reminder exists."""
        consumer = get_task_completed_consumer()
        result = await consumer.handle_event(task_completed_event, session)

        # Verify result
        assert result["status"] == "no_reminder"

    @pytest.mark.asyncio
    async def test_already_sent(self, session: Session, sample_reminder, task_completed_event):
        """Test handling completion when reminder already sent."""
        # Mark reminder as sent
        sample_reminder.sent = True
        session.add(sample_reminder)
        session.commit()

        # Use existing reminder's task_id
        task_completed_event["data"]["payload"]["task_id"] = sample_reminder.task_id

        consumer = get_task_completed_consumer()
        result = await consumer.handle_event(task_completed_event, session)

        # Verify result
        assert result["status"] == "already_sent"


class TestTaskDeletedConsumer:
    """Tests for TaskDeletedConsumer."""

    @pytest.mark.asyncio
    async def test_delete_reminder_success(self, session: Session, sample_reminder, task_deleted_event):
        """Test deleting reminder when task is deleted."""
        # Use existing reminder's task_id
        task_deleted_event["data"]["payload"]["task_id"] = sample_reminder.task_id

        consumer = get_task_deleted_consumer()
        result = await consumer.handle_event(task_deleted_event, session)

        # Verify result
        assert result["status"] == "deleted"
        assert result["reminders_deleted"] == 1

        # Verify reminder deleted from DB
        statement = select(Reminder).where(Reminder.id == sample_reminder.id)
        reminder = session.exec(statement).first()
        assert reminder is None

    @pytest.mark.asyncio
    async def test_delete_multiple_reminders(self, session: Session, task_deleted_event):
        """Test deleting multiple reminders for a task."""
        # Create multiple reminders for same task
        now = datetime.now(timezone.utc)
        for i in range(3):
            reminder = Reminder(
                task_id=42,
                user_id=1,
                reminder_at=now + timedelta(minutes=30 * (i + 1)),
                sent=False
            )
            session.add(reminder)
        session.commit()

        consumer = get_task_deleted_consumer()
        result = await consumer.handle_event(task_deleted_event, session)

        # Verify result
        assert result["status"] == "deleted"
        assert result["reminders_deleted"] == 3

        # Verify all reminders deleted
        statement = select(Reminder).where(Reminder.task_id == 42)
        reminders = session.exec(statement).all()
        assert len(reminders) == 0

    @pytest.mark.asyncio
    async def test_no_reminders_to_delete(self, session: Session, task_deleted_event):
        """Test handling deletion when no reminders exist."""
        consumer = get_task_deleted_consumer()
        result = await consumer.handle_event(task_deleted_event, session)

        # Verify result
        assert result["status"] == "no_reminders"
