"""Event consumers for task events."""

from .task_created_consumer import TaskCreatedConsumer, get_task_created_consumer
from .task_updated_consumer import TaskUpdatedConsumer, get_task_updated_consumer
from .task_completed_consumer import TaskCompletedConsumer, get_task_completed_consumer
from .task_deleted_consumer import TaskDeletedConsumer, get_task_deleted_consumer

__all__ = [
    "TaskCreatedConsumer",
    "get_task_created_consumer",
    "TaskUpdatedConsumer",
    "get_task_updated_consumer",
    "TaskCompletedConsumer",
    "get_task_completed_consumer",
    "TaskDeletedConsumer",
    "get_task_deleted_consumer",
]
