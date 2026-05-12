"""
Tests for EventPublisher service

Tests event publishing, idempotency, retry logic, and dead letter queue functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from src.services.event_publisher import EventPublisher
from src.models.event import TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent, TaskDeletedEvent


class TestEventPublisher:
    """Test suite for EventPublisher service"""

    @pytest.fixture
    def mock_dapr_client(self):
        """Mock Dapr client for testing"""
        with patch('src.services.event_publisher.DaprClient') as mock:
            client_instance = MagicMock()
            mock.return_value.__enter__.return_value = client_instance
            yield client_instance

    @pytest.fixture
    def event_publisher(self):
        """Create EventPublisher instance for testing"""
        return EventPublisher(
            pubsub_name="test-pubsub",
            max_retries=3,
            initial_backoff_ms=100,  # Faster backoff for tests
            max_cache_size=100
        )

    @pytest.fixture
    def sample_task_created_event(self):
        """Sample task.created event for testing"""
        return TaskCreatedEvent.create(
            user_id=1,
            task_id=42,
            title="Test Task",
            description="Test Description",
            priority="high",
            due_date="2026-02-01T14:00:00Z",
            recurrence_rule=None
        )

    # =========================================================================
    # Successful Publishing Tests
    # =========================================================================

    def test_publish_success(self, event_publisher, mock_dapr_client, sample_task_created_event):
        """Test successful event publishing"""
        # Act
        result = event_publisher.publish(sample_task_created_event)

        # Assert
        assert result is True
        mock_dapr_client.publish_event.assert_called_once()

        # Verify event was marked as published (idempotency)
        assert event_publisher._is_duplicate(sample_task_created_event.event_id)

    def test_publish_multiple_events(self, event_publisher, mock_dapr_client):
        """Test publishing multiple different events"""
        # Arrange
        events = [
            TaskCreatedEvent.create(user_id=1, task_id=i, title=f"Task {i}")
            for i in range(5)
        ]

        # Act
        results = [event_publisher.publish(event) for event in events]

        # Assert
        assert all(results)
        assert mock_dapr_client.publish_event.call_count == 5

        # Verify all events marked as published
        for event in events:
            assert event_publisher._is_duplicate(event.event_id)

    def test_topic_mapping(self, event_publisher):
        """Test event type to topic name mapping"""
        # Test all event types
        assert event_publisher._get_topic_name("task.created") == "tasks.created"
        assert event_publisher._get_topic_name("task.updated") == "tasks.updated"
        assert event_publisher._get_topic_name("task.completed") == "tasks.completed"
        assert event_publisher._get_topic_name("task.deleted") == "tasks.deleted"
        assert event_publisher._get_topic_name("reminder.due") == "reminders.due"

    # =========================================================================
    # Idempotency Tests
    # =========================================================================

    def test_idempotency_prevents_duplicate_publish(self, event_publisher, mock_dapr_client, sample_task_created_event):
        """Test that duplicate event_ids are not published twice"""
        # Act
        result1 = event_publisher.publish(sample_task_created_event)
        result2 = event_publisher.publish(sample_task_created_event)  # Duplicate

        # Assert
        assert result1 is True
        assert result2 is True  # Returns True but doesn't actually publish
        mock_dapr_client.publish_event.assert_called_once()  # Only called once

    def test_idempotency_cache_eviction(self, event_publisher, mock_dapr_client):
        """Test that idempotency cache evicts old entries when full"""
        # Arrange: Create more events than cache size
        cache_size = event_publisher.max_cache_size
        events = [
            TaskCreatedEvent.create(user_id=1, task_id=i, title=f"Task {i}")
            for i in range(cache_size + 10)
        ]

        # Act: Publish all events
        for event in events:
            event_publisher.publish(event)

        # Assert: Oldest events should be evicted from cache
        # First event should no longer be in cache
        assert not event_publisher._is_duplicate(events[0].event_id)

        # Recent events should still be in cache
        assert event_publisher._is_duplicate(events[-1].event_id)
        assert event_publisher._is_duplicate(events[-10].event_id)

    def test_mark_as_published(self, event_publisher):
        """Test marking event as published"""
        event_id = "test-event-123"

        # Before marking
        assert not event_publisher._is_duplicate(event_id)

        # Mark as published
        event_publisher._mark_as_published(event_id)

        # After marking
        assert event_publisher._is_duplicate(event_id)

    # =========================================================================
    # Retry and Error Handling Tests
    # =========================================================================

    def test_retry_on_failure(self, event_publisher, mock_dapr_client, sample_task_created_event):
        """Test retry logic with exponential backoff on failure"""
        # Arrange: Make publish fail twice, then succeed
        mock_dapr_client.publish_event.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            None  # Success on 3rd try
        ]

        # Act
        start_time = time.time()
        result = event_publisher.publish(sample_task_created_event)
        elapsed_time = time.time() - start_time

        # Assert
        assert result is True
        assert mock_dapr_client.publish_event.call_count == 3

        # Verify backoff timing (100ms + 200ms = 300ms minimum)
        assert elapsed_time >= 0.3  # At least 300ms for 2 retries

    def test_max_retries_exceeded(self, event_publisher, mock_dapr_client, sample_task_created_event):
        """Test that event is added to DLQ after max retries"""
        # Arrange: Make all publish attempts fail
        mock_dapr_client.publish_event.side_effect = Exception("Persistent error")

        # Act
        result = event_publisher.publish(sample_task_created_event)

        # Assert
        assert result is False
        assert mock_dapr_client.publish_event.call_count == event_publisher.max_retries + 1  # Initial + 3 retries

        # Verify event added to DLQ
        assert event_publisher.get_dlq_size() == 1
        dlq_events = event_publisher.get_dlq_events()
        assert dlq_events[0]["event_id"] == sample_task_created_event.event_id
        assert "Persistent error" in dlq_events[0]["error_message"]

    def test_exponential_backoff_timing(self, event_publisher, mock_dapr_client, sample_task_created_event):
        """Test that backoff times follow exponential pattern"""
        # Arrange: Track call times
        call_times = []

        def track_time(*args, **kwargs):
            call_times.append(time.time())
            raise Exception("Test error")

        mock_dapr_client.publish_event.side_effect = track_time

        # Act
        event_publisher.publish(sample_task_created_event)

        # Assert: Verify exponential backoff (100ms, 200ms, 400ms)
        assert len(call_times) == 4  # Initial + 3 retries

        # Check delay between attempts (with some tolerance)
        delay1 = call_times[1] - call_times[0]  # Should be ~100ms
        delay2 = call_times[2] - call_times[1]  # Should be ~200ms
        delay3 = call_times[3] - call_times[2]  # Should be ~400ms

        assert 0.09 < delay1 < 0.15  # 100ms ± tolerance
        assert 0.18 < delay2 < 0.25  # 200ms ± tolerance
        assert 0.35 < delay3 < 0.50  # 400ms ± tolerance

    # =========================================================================
    # Dead Letter Queue Tests
    # =========================================================================

    def test_dlq_add_and_retrieve(self, event_publisher, mock_dapr_client, sample_task_created_event):
        """Test adding events to DLQ and retrieving them"""
        # Arrange: Force failure
        mock_dapr_client.publish_event.side_effect = Exception("Test error")

        # Act
        event_publisher.publish(sample_task_created_event)

        # Assert
        assert event_publisher.get_dlq_size() == 1

        dlq_events = event_publisher.get_dlq_events()
        assert len(dlq_events) == 1
        assert dlq_events[0]["event_id"] == sample_task_created_event.event_id
        assert dlq_events[0]["event_type"] == "task.created"
        assert "Test error" in dlq_events[0]["error_message"]
        assert dlq_events[0]["retry_count"] == 3

    def test_dlq_clear(self, event_publisher, mock_dapr_client):
        """Test clearing DLQ"""
        # Arrange: Add multiple events to DLQ
        mock_dapr_client.publish_event.side_effect = Exception("Test error")

        events = [
            TaskCreatedEvent.create(user_id=1, task_id=i, title=f"Task {i}")
            for i in range(5)
        ]

        for event in events:
            event_publisher.publish(event)

        assert event_publisher.get_dlq_size() == 5

        # Act
        cleared_count = event_publisher.clear_dlq()

        # Assert
        assert cleared_count == 5
        assert event_publisher.get_dlq_size() == 0

    def test_dlq_max_size(self, event_publisher, mock_dapr_client):
        """Test that DLQ has maximum size (FIFO eviction)"""
        # Arrange: Create more failed events than DLQ can hold
        mock_dapr_client.publish_event.side_effect = Exception("Test error")

        dlq_max_size = 1000  # From EventPublisher init
        events_count = dlq_max_size + 10

        events = [
            TaskCreatedEvent.create(user_id=1, task_id=i, title=f"Task {i}")
            for i in range(events_count)
        ]

        # Act
        for event in events:
            event_publisher.publish(event)

        # Assert: DLQ should not exceed max size
        assert event_publisher.get_dlq_size() == dlq_max_size

    # =========================================================================
    # Event Type Tests
    # =========================================================================

    def test_publish_task_updated_event(self, event_publisher, mock_dapr_client):
        """Test publishing task.updated event"""
        event = TaskUpdatedEvent.create(
            user_id=1,
            task_id=42,
            title="Updated Task",
            description="Updated Description",
            completed=False,
            priority="urgent",
            due_date="2026-02-01T15:00:00Z",
            recurrence_rule=None
        )

        result = event_publisher.publish(event)

        assert result is True
        mock_dapr_client.publish_event.assert_called_once()

        # Verify correct topic
        call_args = mock_dapr_client.publish_event.call_args
        assert call_args[1]["topic_name"] == "tasks.updated"

    def test_publish_task_completed_event(self, event_publisher, mock_dapr_client):
        """Test publishing task.completed event"""
        event = TaskCompletedEvent.create(
            user_id=1,
            task_id=42,
            title="Completed Task",
            completed_at="2026-01-30T12:00:00Z"
        )

        result = event_publisher.publish(event)

        assert result is True
        mock_dapr_client.publish_event.assert_called_once()

        # Verify correct topic
        call_args = mock_dapr_client.publish_event.call_args
        assert call_args[1]["topic_name"] == "tasks.completed"

    def test_publish_task_deleted_event(self, event_publisher, mock_dapr_client):
        """Test publishing task.deleted event"""
        event = TaskDeletedEvent.create(
            user_id=1,
            task_id=42,
            title="Deleted Task"
        )

        result = event_publisher.publish(event)

        assert result is True
        mock_dapr_client.publish_event.assert_called_once()

        # Verify correct topic
        call_args = mock_dapr_client.publish_event.call_args
        assert call_args[1]["topic_name"] == "tasks.deleted"

    # =========================================================================
    # Thread Safety Tests
    # =========================================================================

    def test_concurrent_publish(self, event_publisher, mock_dapr_client):
        """Test thread-safe concurrent event publishing"""
        import threading

        events = [
            TaskCreatedEvent.create(user_id=1, task_id=i, title=f"Task {i}")
            for i in range(20)
        ]

        def publish_event(event):
            event_publisher.publish(event)

        # Act: Publish events concurrently
        threads = [threading.Thread(target=publish_event, args=(event,)) for event in events]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Assert: All events should be published exactly once
        assert mock_dapr_client.publish_event.call_count == 20

        # Verify idempotency cache is thread-safe
        for event in events:
            assert event_publisher._is_duplicate(event.event_id)


class TestEventConsumerUtility:
    """Test utilities for consuming and verifying events (mock consumers)"""

    def test_mock_event_consumer_basic(self):
        """Test basic mock event consumer"""
        # Mock consumer that subscribes to a topic
        received_events = []

        def mock_consumer_handler(event):
            """Mock handler that processes incoming events"""
            received_events.append(event)

        # Simulate publishing and consuming
        event = TaskCreatedEvent.create(
            user_id=1,
            task_id=42,
            title="Test Task"
        )

        # Simulate event delivery to consumer
        event_data = event.model_dump(mode="json")
        mock_consumer_handler(event_data)

        # Verify event was received
        assert len(received_events) == 1
        assert received_events[0]["event_type"] == "task.created"
        assert received_events[0]["payload"]["task_id"] == 42

    def test_mock_event_consumer_idempotency(self):
        """Test consumer handling duplicate events (idempotency)"""
        processed_event_ids = set()

        def idempotent_consumer_handler(event):
            """Mock handler that deduplicates events by event_id"""
            event_id = event["event_id"]

            if event_id in processed_event_ids:
                # Skip duplicate
                return "DUPLICATE_SKIPPED"

            # Process event
            processed_event_ids.add(event_id)
            return "PROCESSED"

        # Create event
        event = TaskCreatedEvent.create(user_id=1, task_id=42, title="Test")
        event_data = event.model_dump(mode="json")

        # First delivery - should process
        result1 = idempotent_consumer_handler(event_data)
        assert result1 == "PROCESSED"

        # Second delivery (duplicate) - should skip
        result2 = idempotent_consumer_handler(event_data)
        assert result2 == "DUPLICATE_SKIPPED"

    def test_event_schema_validation(self):
        """Test validating event schema before consuming"""
        # Create valid event
        event = TaskCreatedEvent.create(user_id=1, task_id=42, title="Test")
        event_data = event.model_dump(mode="json")

        # Validate required fields
        assert "event_id" in event_data
        assert "event_type" in event_data
        assert "timestamp" in event_data
        assert "user_id" in event_data
        assert "payload" in event_data

        # Validate payload
        assert "task_id" in event_data["payload"]
        assert "title" in event_data["payload"]


# =========================================================================
# Integration Test Helper Functions
# =========================================================================

def verify_event_delivery(topic: str, expected_event_id: str, timeout_seconds: int = 5) -> bool:
    """
    Helper function to verify event was delivered to Kafka topic.

    In a real integration test, this would:
    1. Connect to Kafka broker
    2. Subscribe to topic
    3. Poll for events with matching event_id
    4. Return True if found within timeout

    Args:
        topic: Kafka topic name
        expected_event_id: Event ID to look for
        timeout_seconds: Max time to wait for event

    Returns:
        True if event found, False otherwise

    Example:
        >>> assert verify_event_delivery("tasks.created", "event-123", timeout_seconds=10)
    """
    # Mock implementation for now
    # TODO: Implement actual Kafka consumer for integration tests
    return True


def create_test_event_consumer(topics: list, handler_func):
    """
    Create a test event consumer for integration testing.

    Args:
        topics: List of topic names to subscribe to
        handler_func: Callback function to handle received events

    Returns:
        Consumer object (mock for now)

    Example:
        >>> def my_handler(event):
        ...     print(f"Received: {event['event_type']}")
        >>>
        >>> consumer = create_test_event_consumer(["tasks.created"], my_handler)
        >>> consumer.start()  # Starts consuming events
        >>> consumer.stop()   # Stops consuming
    """
    # Mock implementation for now
    # TODO: Implement actual Dapr subscriber or Kafka consumer
    return MockEventConsumer(topics, handler_func)


class MockEventConsumer:
    """Mock event consumer for testing"""

    def __init__(self, topics: list, handler_func):
        self.topics = topics
        self.handler_func = handler_func
        self.is_running = False

    def start(self):
        """Start consuming events"""
        self.is_running = True

    def stop(self):
        """Stop consuming events"""
        self.is_running = False

    def consume_event(self, event):
        """Manually trigger event consumption (for testing)"""
        if self.is_running:
            self.handler_func(event)
