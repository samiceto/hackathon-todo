# Event Schemas: Step 5 - Advanced Cloud Deployment

**Created**: 2026-01-30
**Purpose**: Define event schemas for event-driven architecture using Kafka and Dapr

## Overview

This document defines the event schemas for all task-related events published to Kafka topics via Dapr Pub/Sub. Events enable asynchronous processing, audit trails, and future integrations.

## Event Schema Standard

All events follow a consistent structure:

```json
{
  "event_id": "UUID (v4)",
  "event_type": "String (enum: task.created, task.updated, task.completed, task.deleted, reminder.due)",
  "timestamp": "ISO 8601 datetime (UTC)",
  "user_id": "Integer (user who triggered the event)",
  "payload": "Object (event-specific data)"
}
```

## Event Types

### 1. task.created

**Topic**: `tasks.created`
**Published When**: A new task is created
**Publisher**: Backend API

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "user_id", "payload"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this event"
    },
    "event_type": {
      "type": "string",
      "const": "task.created",
      "description": "Event type identifier"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the event was created (ISO 8601 UTC)"
    },
    "user_id": {
      "type": "integer",
      "description": "ID of the user who created the task"
    },
    "payload": {
      "type": "object",
      "required": ["task_id", "title"],
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "ID of the created task"
        },
        "title": {
          "type": "string",
          "description": "Task title"
        },
        "description": {
          "type": "string",
          "description": "Task description"
        },
        "priority": {
          "type": "string",
          "enum": ["low", "medium", "high", "urgent"],
          "description": "Task priority level"
        },
        "due_date": {
          "type": "string",
          "format": "date-time",
          "nullable": true,
          "description": "Task due date (ISO 8601 UTC)"
        },
        "recurrence_rule": {
          "type": "string",
          "nullable": true,
          "description": "iCal RRULE format recurrence rule"
        },
        "reminder_offset": {
          "type": "integer",
          "nullable": true,
          "description": "Minutes before due date to send reminder"
        }
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_type": "task.created",
  "timestamp": "2026-01-30T14:30:00Z",
  "user_id": 123,
  "payload": {
    "task_id": 456,
    "title": "Daily Standup",
    "description": "Review yesterday's progress and today's plan",
    "priority": "high",
    "due_date": "2026-01-31T09:00:00Z",
    "recurrence_rule": "FREQ=DAILY",
    "reminder_offset": 30
  }
}
```

---

### 2. task.updated

**Topic**: `tasks.updated`
**Published When**: An existing task is modified
**Publisher**: Backend API

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "user_id", "payload"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "event_type": {
      "type": "string",
      "const": "task.updated"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "user_id": {
      "type": "integer"
    },
    "payload": {
      "type": "object",
      "required": ["task_id", "changes"],
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "ID of the updated task"
        },
        "changes": {
          "type": "object",
          "description": "Fields that were changed (old_value -> new_value)",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "old": {},
              "new": {}
            }
          }
        }
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "c9d48a12-8b3e-4f91-9c21-5a7e2d3b4c56",
  "event_type": "task.updated",
  "timestamp": "2026-01-30T15:45:00Z",
  "user_id": 123,
  "payload": {
    "task_id": 456,
    "changes": {
      "title": {
        "old": "Daily Standup",
        "new": "Daily Standup Meeting"
      },
      "due_date": {
        "old": "2026-01-31T09:00:00Z",
        "new": "2026-01-31T10:00:00Z"
      }
    }
  }
}
```

---

### 3. task.completed

**Topic**: `tasks.completed`
**Published When**: A task is marked as complete
**Publisher**: Backend API

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "user_id", "payload"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "event_type": {
      "type": "string",
      "const": "task.completed"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "user_id": {
      "type": "integer"
    },
    "payload": {
      "type": "object",
      "required": ["task_id", "completed_at"],
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "ID of the completed task"
        },
        "completed_at": {
          "type": "string",
          "format": "date-time",
          "description": "When the task was completed (ISO 8601 UTC)"
        }
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "3e8f2a7b-9d1c-4e56-b2a3-8c7d4e5f6a90",
  "event_type": "task.completed",
  "timestamp": "2026-01-30T16:00:00Z",
  "user_id": 123,
  "payload": {
    "task_id": 456,
    "completed_at": "2026-01-30T16:00:00Z"
  }
}
```

---

### 4. task.deleted

**Topic**: `tasks.deleted`
**Published When**: A task is permanently deleted
**Publisher**: Backend API

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "user_id", "payload"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "event_type": {
      "type": "string",
      "const": "task.deleted"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "user_id": {
      "type": "integer"
    },
    "payload": {
      "type": "object",
      "required": ["task_id"],
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "ID of the deleted task"
        }
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "7b9c3e2f-4d1a-5e67-a8b9-2c3d4e5f6a78",
  "event_type": "task.deleted",
  "timestamp": "2026-01-30T17:30:00Z",
  "user_id": 123,
  "payload": {
    "task_id": 456
  }
}
```

---

### 5. reminder.due

**Topic**: `reminders.due`
**Published When**: A reminder time is reached
**Publisher**: Reminder Service

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "user_id", "payload"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "event_type": {
      "type": "string",
      "const": "reminder.due"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "user_id": {
      "type": "integer"
    },
    "payload": {
      "type": "object",
      "required": ["reminder_id", "task_id", "task_title", "due_date"],
      "properties": {
        "reminder_id": {
          "type": "integer",
          "description": "ID of the reminder record"
        },
        "task_id": {
          "type": "integer",
          "description": "ID of the task this reminder is for"
        },
        "task_title": {
          "type": "string",
          "description": "Title of the task (for notification)"
        },
        "due_date": {
          "type": "string",
          "format": "date-time",
          "description": "When the task is due (ISO 8601 UTC)"
        },
        "reminder_offset": {
          "type": "integer",
          "description": "Minutes before due date (e.g., 30)"
        }
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d",
  "event_type": "reminder.due",
  "timestamp": "2026-01-31T08:30:00Z",
  "user_id": 123,
  "payload": {
    "reminder_id": 789,
    "task_id": 456,
    "task_title": "Daily Standup Meeting",
    "due_date": "2026-01-31T09:00:00Z",
    "reminder_offset": 30
  }
}
```

---

## Topic Configuration

### Kafka Topics

All topics use the following configuration:

- **Partitions**: 3 (for parallel processing)
- **Replication Factor**: 3 (for high availability in production)
- **Retention**: 7 days (168 hours)
- **Cleanup Policy**: delete (remove old messages after retention period)

### Topic Names

| Event Type | Kafka Topic | Dapr Pub/Sub Name |
|------------|-------------|-------------------|
| task.created | tasks.created | tasks.created |
| task.updated | tasks.updated | tasks.updated |
| task.completed | tasks.completed | tasks.completed |
| task.deleted | tasks.deleted | tasks.deleted |
| reminder.due | reminders.due | reminders.due |

---

## Event Publishing Guidelines

1. **Event ID**: Always generate a new UUID v4 for each event
2. **Timestamp**: Use UTC timezone (ISO 8601 format with 'Z' suffix)
3. **User ID**: Include the authenticated user who triggered the action
4. **Idempotency**: Consumers should use event_id to detect and skip duplicate events
5. **Ordering**: Events for the same task_id maintain order within a partition
6. **Error Handling**: Failed publishes should be retried with exponential backoff
7. **Monitoring**: Track event publish success/failure rates and latency

---

## Event Consumption Guidelines

1. **At-Least-Once Delivery**: Dapr guarantees at-least-once delivery, so consumers must be idempotent
2. **Offset Management**: Dapr automatically manages Kafka consumer offsets
3. **Error Handling**: Failed event processing should return HTTP 4xx/5xx to trigger retry
4. **Dead Letter Queue**: Configure DLQ for events that fail after max retries
5. **Monitoring**: Track consumer lag, processing latency, and error rates

---

## Future Event Types

Potential future events (not implemented in Step 5):

- `task.assigned`: When a task is assigned to a user
- `task.comment_added`: When a comment is added to a task
- `task.attachment_uploaded`: When a file is attached to a task
- `notification.sent`: When a notification is successfully delivered
- `notification.failed`: When a notification delivery fails

---

## References

- Dapr Pub/Sub: https://docs.dapr.io/developing-applications/building-blocks/pubsub/
- Kafka Topic Configuration: https://kafka.apache.org/documentation/#topicconfigs
- JSON Schema: https://json-schema.org/
- iCal RRULE: https://icalendar.org/iCalendar-RFC-5545/3-3-10-recurrence-rule.html
