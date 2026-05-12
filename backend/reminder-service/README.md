# Reminder Service

**Part of**: Step 5 - Advanced Cloud Deployment
**Purpose**: Asynchronous reminder processing microservice for the Todo Application

## Overview

The Reminder Service is a dedicated microservice that:
- Consumes task events (task.created, task.updated, task.completed, task.deleted) from Kafka via Dapr Pub/Sub
- Calculates reminder times based on task due dates and reminder offsets
- Stores reminder records in the database
- Processes scheduled reminders every minute via Dapr Cron Binding
- Publishes reminder.due events when reminders are due

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Reminder Service (FastAPI + Dapr)             │
│                                                 │
│  ┌──────────────┐  ┌─────────────────────┐    │
│  │ Event        │  │ Reminder            │    │
│  │ Consumers    │  │ Processor           │    │
│  │              │  │                     │    │
│  │ - task.*     │  │ - Query due         │    │
│  │ - Via Dapr   │  │ - Publish events    │    │
│  └──────┬───────┘  └──────▲──────────────┘    │
│         │                  │                    │
│         │        ┌─────────┴──────────┐        │
│         └────────► Database           │        │
│                  │ (Reminder records) │        │
│                  └────────────────────┘        │
└─────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
   Dapr Pub/Sub             Dapr Cron Binding
   (Kafka topics)           (every 1 minute)
```

## Dependencies

- **FastAPI**: Web framework for HTTP endpoints
- **Dapr SDK**: Distributed application runtime integration
- **SQLModel**: Database ORM (shared models with backend)
- **python-dateutil**: Date/time calculations
- **uvicorn**: ASGI server

## Development

```bash
# Install dependencies
cd backend/reminder-service
uv sync

# Run tests
uv run pytest

# Run service locally (requires Dapr sidecar)
dapr run --app-id reminder-service --app-port 8001 --dapr-http-port 3501 -- uv run uvicorn src.main:app --host 0.0.0.0 --port 8001
```

## API Endpoints

- `GET /health`: Health check endpoint
- `POST /cron`: Dapr Cron Binding endpoint (triggered every 1 minute)
- `POST /events/task-created`: Dapr subscription endpoint for task.created events
- `POST /events/task-updated`: Dapr subscription endpoint for task.updated events
- `POST /events/task-completed`: Dapr subscription endpoint for task.completed events
- `POST /events/task-deleted`: Dapr subscription endpoint for task.deleted events

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (shared with backend)
- `DAPR_HTTP_PORT`: Dapr sidecar HTTP port (default: 3500)
- `DAPR_GRPC_PORT`: Dapr sidecar gRPC port (default: 50001)
- `LOG_LEVEL`: Logging level (default: INFO)

## Deployment

The reminder service is deployed as a Kubernetes Deployment with a Dapr sidecar:
- Helm chart: `helm/todo-app/templates/reminder-deployment.yaml`
- Service: `helm/todo-app/templates/reminder-service.yaml`
- Dapr annotations: `dapr.io/enabled=true`, `dapr.io/app-id=reminder-service`, `dapr.io/app-port=8001`

## Event Schemas

See `specs/005-step-5-cloud-deployment/design/event-schemas.md` for complete event schemas.

## License

MIT
