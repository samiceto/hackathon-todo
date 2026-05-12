"""Tests for ReminderProcessor service."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel import Session, select

from src.services import ReminderProcessor
from src.models import Reminder


class TestReminderProcessor:
    """Tests for ReminderProcessor service."""

    @pytest.mark.asyncio
    async def test_process_due_reminders_success(self, session: Session, due_reminder):
        """Test processing due reminders successfully."""
        processor = ReminderProcessor()

        # Mock Dapr client
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Process reminders
            count = await processor.process_due_reminders(session)

            # Verify result
            assert count == 1

            # Verify Dapr publish called
            mock_client.publish_event.assert_called_once()

            # Verify reminder marked as sent
            session.refresh(due_reminder)
            assert due_reminder.sent is True

    @pytest.mark.asyncio
    async def test_process_multiple_due_reminders(self, session: Session):
        """Test processing multiple due reminders."""
        # Create multiple due reminders
        now = datetime.now(timezone.utc)
        for i in range(5):
            reminder = Reminder(
                task_id=100 + i,
                user_id=1,
                reminder_at=now - timedelta(minutes=i + 1),
                sent=False
            )
            session.add(reminder)
        session.commit()

        processor = ReminderProcessor()

        # Mock Dapr client
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Process reminders
            count = await processor.process_due_reminders(session)

            # Verify result
            assert count == 5

            # Verify Dapr publish called 5 times
            assert mock_client.publish_event.call_count == 5

            # Verify all reminders marked as sent
            statement = select(Reminder).where(Reminder.sent == True)  # noqa: E712
            sent_reminders = session.exec(statement).all()
            assert len(sent_reminders) == 5

    @pytest.mark.asyncio
    async def test_skip_future_reminders(self, session: Session, sample_reminder):
        """Test skipping reminders that are not yet due."""
        processor = ReminderProcessor()

        # Mock Dapr client
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Process reminders
            count = await processor.process_due_reminders(session)

            # Verify no reminders processed
            assert count == 0

            # Verify Dapr publish not called
            mock_client.publish_event.assert_not_called()

            # Verify reminder not marked as sent
            session.refresh(sample_reminder)
            assert sample_reminder.sent is False

    @pytest.mark.asyncio
    async def test_skip_already_sent_reminders(self, session: Session, due_reminder):
        """Test skipping reminders that are already sent."""
        # Mark reminder as sent
        due_reminder.sent = True
        session.add(due_reminder)
        session.commit()

        processor = ReminderProcessor()

        # Mock Dapr client
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Process reminders
            count = await processor.process_due_reminders(session)

            # Verify no reminders processed
            assert count == 0

            # Verify Dapr publish not called
            mock_client.publish_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_batch_size_limit(self, session: Session):
        """Test respecting batch_size limit."""
        # Create more reminders than batch size
        batch_size = 10
        total_reminders = 15

        now = datetime.now(timezone.utc)
        for i in range(total_reminders):
            reminder = Reminder(
                task_id=200 + i,
                user_id=1,
                reminder_at=now - timedelta(minutes=i + 1),
                sent=False
            )
            session.add(reminder)
        session.commit()

        processor = ReminderProcessor(batch_size=batch_size)

        # Mock Dapr client
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Process reminders
            count = await processor.process_due_reminders(session)

            # Verify only batch_size processed
            assert count == batch_size

            # Verify Dapr publish called batch_size times
            assert mock_client.publish_event.call_count == batch_size

    @pytest.mark.asyncio
    async def test_idempotency_protection(self, session: Session, due_reminder):
        """Test idempotency protection prevents duplicate processing."""
        processor = ReminderProcessor()

        # Mock Dapr client
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Process reminders first time
            count1 = await processor.process_due_reminders(session)
            assert count1 == 1

            # Rollback to simulate DB commit not yet complete
            session.rollback()

            # Try processing again (idempotency cache should prevent duplicate)
            count2 = await processor.process_due_reminders(session)

            # Verify no duplicate processing
            assert count2 == 0  # Already in idempotency cache

            # Verify Dapr publish only called once
            assert mock_client.publish_event.call_count == 1

    @pytest.mark.asyncio
    async def test_error_handling_one_failure(self, session: Session):
        """Test error handling when one reminder fails."""
        # Create multiple due reminders
        now = datetime.now(timezone.utc)
        for i in range(3):
            reminder = Reminder(
                task_id=300 + i,
                user_id=1,
                reminder_at=now - timedelta(minutes=i + 1),
                sent=False
            )
            session.add(reminder)
        session.commit()

        processor = ReminderProcessor()

        # Mock Dapr client to fail on second reminder
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Make second call fail
            mock_client.publish_event.side_effect = [
                None,  # First succeeds
                Exception("Test error"),  # Second fails
                None  # Third succeeds
            ]

            # Process reminders
            count = await processor.process_due_reminders(session)

            # Verify 2 succeeded, 1 failed
            assert count == 2

            # Verify publish called 3 times (all attempted)
            assert mock_client.publish_event.call_count == 3

            # Verify 2 reminders marked as sent
            statement = select(Reminder).where(Reminder.sent == True)  # noqa: E712
            sent_reminders = session.exec(statement).all()
            assert len(sent_reminders) == 2

    @pytest.mark.asyncio
    async def test_publish_reminder_event_content(self, session: Session, due_reminder):
        """Test reminder.due event content is correct."""
        processor = ReminderProcessor()

        # Mock Dapr client
        with patch("src.services.reminder_processor.DaprClient") as mock_dapr:
            mock_client = MagicMock()
            mock_dapr.return_value.__enter__.return_value = mock_client

            # Process reminders
            await processor.process_due_reminders(session)

            # Verify publish called with correct parameters
            call_args = mock_client.publish_event.call_args

            assert call_args[1]["pubsub_name"] == processor.pubsub_name
            assert call_args[1]["topic_name"] == "reminders.due"
            assert call_args[1]["data_content_type"] == "application/json"

            # Verify event data structure
            event_data = call_args[1]["data"]
            assert event_data["event_type"] == "reminder.due"
            assert event_data["user_id"] == due_reminder.user_id
            assert event_data["payload"]["task_id"] == due_reminder.task_id
