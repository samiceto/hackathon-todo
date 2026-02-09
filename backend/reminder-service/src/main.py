"""Reminder Service - Asynchronous reminder processing microservice.

This service:
1. Consumes task events (task.created, task.updated, task.completed, task.deleted) from Kafka via Dapr
2. Calculates reminder times based on task due dates and reminder offsets
3. Stores reminder records in the database
4. Processes scheduled reminders every minute via Dapr Cron Binding
5. Publishes reminder.due events when reminders are due
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from .config import settings
from .database import get_session
from .consumers import (
    get_task_created_consumer,
    get_task_updated_consumer,
    get_task_completed_consumer,
    get_task_deleted_consumer,
)
from .services import get_reminder_processor

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Reminder Service starting up...")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Dapr HTTP port: {settings.dapr_http_port}")
    logger.info(f"Dapr gRPC port: {settings.dapr_grpc_port}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Pub/Sub name: {settings.pubsub_name}")

    yield

    # Shutdown
    logger.info("Reminder Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Reminder Service",
    description="Asynchronous reminder processing microservice for Todo Application",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint.

    Returns:
        Health status and service information
    """
    return {
        "status": "healthy",
        "service": "reminder-service",
        "version": "1.0.0"
    }


@app.post("/cron", tags=["Cron"])
async def process_reminders_cron(session: Session = Depends(get_session)):
    """Dapr Cron Binding endpoint (T075).

    Triggered every 1 minute by Dapr Cron Binding to process due reminders.
    Queries the database for reminders with reminder_at <= now and sent = false,
    then publishes reminder.due events.

    Args:
        session: Database session (injected)

    Returns:
        Processing status and count of reminders processed
    """
    logger.info("Cron trigger received - processing reminders")

    try:
        # Get ReminderProcessor service
        processor = get_reminder_processor()

        # Process due reminders
        processed_count = await processor.process_due_reminders(session)

        logger.info(f"Cron processing completed: {processed_count} reminders processed")

        return {
            "status": "success",
            "reminders_processed": processed_count
        }

    except Exception as e:
        logger.error(f"Cron processing failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "reminders_processed": 0
            }
        )


@app.post("/events/task-created", tags=["Events"])
async def handle_task_created_event(event: Dict[str, Any], session: Session = Depends(get_session)):
    """Handle task.created event from Dapr subscription (T070).

    Creates a reminder record if the task has a due_date and reminder_offset.

    Args:
        event: Task created event payload
        session: Database session (injected)

    Returns:
        Processing status
    """
    task_id = event.get('data', {}).get('payload', {}).get('task_id')
    logger.info(f"Received task.created event: task_id={task_id}")

    try:
        # Get consumer
        consumer = get_task_created_consumer()

        # Handle event
        result = await consumer.handle_event(event, session)

        logger.info(f"task.created event processed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to handle task.created event: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@app.post("/events/task-updated", tags=["Events"])
async def handle_task_updated_event(event: Dict[str, Any], session: Session = Depends(get_session)):
    """Handle task.updated event from Dapr subscription (T071).

    Updates the reminder record if the due_date or reminder_offset changed.

    Args:
        event: Task updated event payload
        session: Database session (injected)

    Returns:
        Processing status
    """
    task_id = event.get('data', {}).get('payload', {}).get('task_id')
    logger.info(f"Received task.updated event: task_id={task_id}")

    try:
        # Get consumer
        consumer = get_task_updated_consumer()

        # Handle event
        result = await consumer.handle_event(event, session)

        logger.info(f"task.updated event processed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to handle task.updated event: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@app.post("/events/task-completed", tags=["Events"])
async def handle_task_completed_event(event: Dict[str, Any], session: Session = Depends(get_session)):
    """Handle task.completed event from Dapr subscription (T073).

    Marks the reminder as sent to prevent duplicate reminders.

    Args:
        event: Task completed event payload
        session: Database session (injected)

    Returns:
        Processing status
    """
    task_id = event.get('data', {}).get('payload', {}).get('task_id')
    logger.info(f"Received task.completed event: task_id={task_id}")

    try:
        # Get consumer
        consumer = get_task_completed_consumer()

        # Handle event
        result = await consumer.handle_event(event, session)

        logger.info(f"task.completed event processed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to handle task.completed event: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@app.post("/events/task-deleted", tags=["Events"])
async def handle_task_deleted_event(event: Dict[str, Any], session: Session = Depends(get_session)):
    """Handle task.deleted event from Dapr subscription (T072).

    Deletes associated reminder records.

    Args:
        event: Task deleted event payload
        session: Database session (injected)

    Returns:
        Processing status
    """
    task_id = event.get('data', {}).get('payload', {}).get('task_id')
    logger.info(f"Received task.deleted event: task_id={task_id}")

    try:
        # Get consumer
        consumer = get_task_deleted_consumer()

        # Handle event
        result = await consumer.handle_event(event, session)

        logger.info(f"task.deleted event processed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to handle task.deleted event: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@app.get("/dapr/subscribe", tags=["Dapr"])
async def dapr_subscribe():
    """Dapr subscription configuration endpoint.

    Tells Dapr which topics this service subscribes to and which endpoints to call.

    Returns:
        List of subscription configurations
    """
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "tasks.created",
            "route": "/events/task-created"
        },
        {
            "pubsubname": "pubsub-kafka",
            "topic": "tasks.updated",
            "route": "/events/task-updated"
        },
        {
            "pubsubname": "pubsub-kafka",
            "topic": "tasks.completed",
            "route": "/events/task-completed"
        },
        {
            "pubsubname": "pubsub-kafka",
            "topic": "tasks.deleted",
            "route": "/events/task-deleted"
        }
    ]


if __name__ == "__main__":
    import uvicorn

    # Run the service
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
