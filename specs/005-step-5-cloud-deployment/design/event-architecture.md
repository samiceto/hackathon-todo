# Event-Driven Architecture

**Feature**: Step 5 - Cloud Deployment
**User Story**: US5 - Event-Driven Task Management
**Version**: 1.0.0
**Last Updated**: 2026-01-30

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Event Flow](#event-flow)
3. [Topic Structure](#topic-structure)
4. [Event Schemas](#event-schemas)
5. [Publisher Patterns](#publisher-patterns)
6. [Consumer Patterns](#consumer-patterns)
7. [Delivery Guarantees](#delivery-guarantees)
8. [Error Handling](#error-handling)
9. [Monitoring & Observability](#monitoring--observability)
10. [Integration Points](#integration-points)

---

## Architecture Overview

### Design Philosophy

The event-driven architecture decouples task management operations from downstream processing (reminders, notifications, analytics) using an event sourcing pattern mediated by Kafka and Dapr Pub/Sub.

**Key Principles**:
- **Loose Coupling**: Services communicate via events, not direct calls
- **Scalability**: Asynchronous processing enables independent scaling
- **Reliability**: At-least-once delivery with idempotency protection
- **Auditability**: Full event history for debugging and analytics

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     TASK API (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Task CRUD Operations                                    │  │
│  │  (POST/PUT/DELETE /api/{user_id}/tasks)                  │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  EventPublisher Service                                  │  │
│  │  - Idempotency Cache (10K events)                        │  │
│  │  - Retry Logic (3 attempts, exponential backoff)         │  │
│  │  - Dead Letter Queue (1K failed events)                  │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└─────────────────────┼─┼─────────────────────────────────────────┘
                      │ │
                      ▼ ▼
          ┌───────────────────────────┐
          │   Dapr Pub/Sub API        │
          │   (HTTP Sidecar)          │
          └─────────────┬─────────────┘
                        │
                        ▼
          ┌───────────────────────────┐
          │   Apache Kafka            │
          │   Topics:                 │
          │   - tasks.created         │
          │   - tasks.updated         │
          │   - tasks.completed       │
          │   - tasks.deleted         │
          │   - reminders.due         │
          └─────────────┬─────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Reminder    │ │ Analytics   │ │ Notification│
│ Service     │ │ Service     │ │ Service     │
│ (Consumer)  │ │ (Consumer)  │ │ (Consumer)  │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Technology Stack

- **Message Broker**: Apache Kafka (via Dapr component)
- **Pub/Sub Abstraction**: Dapr Pub/Sub API
- **Publisher**: EventPublisher service (Python, Dapr SDK)
- **Event Schema**: JSON with CloudEvents envelope
- **Serialization**: JSON (application/json)
- **Delivery Semantics**: At-least-once with idempotency

---

## Event Flow

### 1. Task Creation Flow

```
User Request                  Backend Processing                Kafka & Consumers
────────────                  ──────────────────                ─────────────────

POST /tasks
  title: "Buy milk"
  description: "..."
       │
       ▼
┌──────────────────┐
│ Task API Handler │
│  (tasks.py)      │
└────────┬─────────┘
         │
         │ 1. Validate request
         │ 2. Create Task in DB
         │    (PostgreSQL)
         ▼
    ┌─────────┐
    │  Task   │
    │ Created │
    │ (id=42) │
    └────┬────┘
         │
         │ 3. Publish event
         ▼
┌─────────────────────┐
│ EventPublisher      │
│ .publish(event)     │
└────────┬────────────┘
         │
         │ 4. Check idempotency cache
         │    (event_id already published?)
         │    NO → Continue
         │    YES → Skip (return success)
         ▼
┌─────────────────────┐
│ Dapr Pub/Sub API    │
│ POST /publish       │
└────────┬────────────┘
         │
         │ 5. Publish to Kafka
         │    Topic: tasks.created
         │    Partition: user_id hash
         ▼
    ┌────────────┐
    │   Kafka    │────────────┐
    │  Broker    │            │
    └────────────┘            │
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │ Reminder Svc │ │Analytics Svc │ │Notification  │
      │              │ │              │ │Svc           │
      │ Checks if    │ │ Records task │ │ Sends push   │
      │ task has     │ │ creation for │ │ notification │
      │ due_date +   │ │ metrics      │ │ to user      │
      │ reminder     │ │              │ │              │
      │              │ │              │ │              │
      │ Creates      │ │              │ │              │
      │ reminder if  │ │              │ │              │
      │ needed       │ │              │ │              │
      └──────────────┘ └──────────────┘ └──────────────┘
```

### 2. Task Update Flow

```
PUT /tasks/42
  title: "Buy milk & eggs"
       │
       ▼
┌──────────────────┐
│ Task API Handler │
└────────┬─────────┘
         │
         │ 1. Validate request
         │ 2. Update Task in DB
         ▼
    ┌─────────┐
    │  Task   │
    │ Updated │
    └────┬────┘
         │
         │ 3. Publish task.updated event
         ▼
┌─────────────────────┐
│ EventPublisher      │
│ publish(event)      │
└────────┬────────────┘
         │
         ▼
    Kafka Topic: tasks.updated
         │
         └──► Consumers process update
                - Analytics: Track task edit
                - Reminder: Update reminder if due_date changed
                - Search Index: Reindex task
```

### 3. Task Completion Flow

```
PATCH /tasks/42/complete
       │
       ▼
┌──────────────────┐
│ Task API Handler │
└────────┬─────────┘
         │
         │ 1. Mark task.completed = True
         │ 2. Set task.completed_at timestamp
         ▼
    ┌─────────┐
    │  Task   │
    │Complete │
    └────┬────┘
         │
         │ 3. Publish task.completed event
         ▼
┌─────────────────────┐
│ EventPublisher      │
└────────┬────────────┘
         │
         ▼
    Kafka Topic: tasks.completed
         │
         └──► Consumers react
                - Reminder: Cancel pending reminders
                - Analytics: Track completion time
                - Gamification: Award points
```

### 4. Task Deletion Flow

```
DELETE /tasks/42
       │
       ▼
┌──────────────────┐
│ Task API Handler │
└────────┬─────────┘
         │
         │ 1. Soft delete OR hard delete
         │ 2. Remove from DB
         ▼
    ┌─────────┐
    │  Task   │
    │ Deleted │
    └────┬────┘
         │
         │ 3. Publish task.deleted event
         ▼
┌─────────────────────┐
│ EventPublisher      │
└────────┬────────────┘
         │
         ▼
    Kafka Topic: tasks.deleted
         │
         └──► Consumers cleanup
                - Reminder: Delete all reminders for task
                - Search Index: Remove from index
                - Analytics: Mark as deleted in data warehouse
```

---

## Topic Structure

### Topic Naming Convention

Format: `{domain}.{event_type}`

**Rationale**: Allows topic-level access control and consumer filtering by domain.

### Topic Catalog

| Topic Name          | Event Type        | Partitions | Retention | Consumer(s)                        |
|---------------------|-------------------|------------|-----------|-------------------------------------|
| `tasks.created`     | task.created      | 3          | 7 days    | Reminder, Analytics, Notification   |
| `tasks.updated`     | task.updated      | 3          | 7 days    | Reminder, Analytics, Search Indexer |
| `tasks.completed`   | task.completed    | 3          | 7 days    | Reminder, Analytics, Gamification   |
| `tasks.deleted`     | task.deleted      | 3          | 7 days    | Reminder, Search Indexer, Analytics |
| `reminders.due`     | reminder.due      | 3          | 1 day     | Notification Service                |

### Partition Strategy

**Partition Key**: `user_id`

**Rationale**:
- All events for a user go to the same partition → Ordering guaranteed per user
- Users distributed across partitions → Parallelism for multi-user workloads
- Consumer can process users independently

**Example**:
```
User 1 events → Partition 0
User 2 events → Partition 1
User 3 events → Partition 2
User 4 events → Partition 0  (hash(user_id) % 3)
```

### Retention Policy

- **Default**: 7 days for task events (sufficient for replay/debugging)
- **Reminders**: 1 day (transient, no replay needed)
- **Future**: Archive to S3 for long-term analytics

---

## Event Schemas

All events follow CloudEvents specification with custom payload structure.

### Base Event Structure

```json
{
  "event_id": "evt_abc123",           // UUID v4 (idempotency key)
  "event_type": "task.created",       // Event type (routing key)
  "timestamp": "2026-01-30T12:00:00Z", // ISO 8601 UTC
  "user_id": 42,                       // User who triggered event
  "payload": {                         // Event-specific data
    ...
  }
}
```

### Event Type Mapping

| Event Type        | Trigger                  | Payload                                                  |
|-------------------|--------------------------|----------------------------------------------------------|
| `task.created`    | POST /tasks              | task_id, title, description, priority, due_date, recurrence |
| `task.updated`    | PUT /tasks/{id}          | task_id, title, description, completed, priority, due_date, recurrence |
| `task.completed`  | PATCH /tasks/{id}/complete | task_id, title, completed_at                            |
| `task.deleted`    | DELETE /tasks/{id}       | task_id, title                                           |
| `reminder.due`    | Reminder cron job        | task_id, reminder_offset, due_date                       |

### Full Schema Examples

See [event-schemas.md](event-schemas.md) for complete JSON Schema definitions and examples.

---

## Publisher Patterns

### EventPublisher Service

**Location**: `backend/api/src/services/event_publisher.py`

**Responsibilities**:
1. Publish events to Kafka via Dapr Pub/Sub API
2. Ensure idempotency (no duplicate events)
3. Handle transient failures with retries
4. Dead-letter queue for permanent failures

### Publishing Workflow

```python
# In Task API handler (backend/api/src/api/tasks.py)

from src.services.event_publisher import get_event_publisher
from src.models.event import TaskCreatedEvent

@router.post("/{user_id}/tasks", response_model=Task)
def create_task(user_id: int, task_data: TaskCreate):
    # 1. Create task in database
    task = task_service.create_task(user_id, task_data)

    # 2. Create event
    event = TaskCreatedEvent.create(
        user_id=user_id,
        task_id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        recurrence_rule=task.recurrence_rule
    )

    # 3. Publish event (async, fire-and-forget)
    publisher = get_event_publisher()
    publisher.publish(event)

    # 4. Return task immediately (don't wait for event delivery)
    return task
```

### Idempotency Implementation

**Cache Structure**:
- **Type**: In-memory deque with max size (10,000 events)
- **Key**: `event_id` (UUID v4)
- **Eviction**: FIFO when cache is full
- **Thread Safety**: Protected by `threading.Lock`

**How It Works**:
```python
def publish(self, event: Event) -> bool:
    # Check if event already published
    if self._is_duplicate(event.event_id):
        logger.warning(f"Duplicate event: {event.event_id}")
        return True  # Return success (already published)

    # Publish to Kafka via Dapr
    client.publish_event(...)

    # Mark as published (add to cache)
    self._mark_as_published(event.event_id)
```

**Cache Eviction**:
```python
def _mark_as_published(self, event_id: str):
    with self._idempotency_lock:
        # If cache full, remove oldest event_id from set
        if len(self._published_event_ids) == self.max_cache_size:
            oldest_event_id = self._published_event_ids[0]
            self._published_event_ids_set.discard(oldest_event_id)

        # Add to deque (auto-evicts oldest when maxlen reached)
        self._published_event_ids.append(event_id)
        self._published_event_ids_set.add(event_id)
```

### Retry Logic

**Strategy**: Exponential backoff

**Parameters**:
- `max_retries`: 3 attempts (default)
- `initial_backoff_ms`: 1000ms (1 second)
- **Backoff Schedule**: 1s → 2s → 4s

**Implementation**:
```python
def publish(self, event: Event, retry_count: int = 0) -> bool:
    try:
        # Publish via Dapr
        with DaprClient() as client:
            client.publish_event(...)
        return True

    except DaprInternalError as e:
        if retry_count < self.max_retries:
            # Exponential backoff
            backoff_ms = self.initial_backoff_ms * (2 ** retry_count)
            time.sleep(backoff_ms / 1000.0)

            # Retry
            return self.publish(event, retry_count + 1)
        else:
            # Max retries exceeded → Add to DLQ
            self._add_to_dlq(event, str(e))
            return False
```

**Retry Scenarios**:
- Network timeouts
- Kafka broker unavailable
- Dapr sidecar restart
- Transient Kafka errors (leader election)

---

## Consumer Patterns

### Dapr Subscriber Pattern

Consumers subscribe to topics using Dapr's app callback pattern.

**Subscription Configuration** (`backend/reminder-service/subscriptions.yaml`):
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: reminder-task-subscription
spec:
  pubsubname: pubsub-kafka
  topic: tasks.created
  route: /events/task-created
  deadLetterTopic: tasks.created.dlq
```

**Consumer Handler** (FastAPI endpoint):
```python
@app.post("/events/task-created")
async def handle_task_created(event: CloudEvent):
    # 1. Extract event data
    event_id = event.data["event_id"]
    task_id = event.data["payload"]["task_id"]
    due_date = event.data["payload"]["due_date"]

    # 2. Idempotency check (consumer-side)
    if await is_duplicate(event_id):
        return {"status": "ok"}  # Already processed

    # 3. Process event (create reminder if due_date exists)
    if due_date:
        await create_reminder(task_id, due_date)

    # 4. Mark as processed
    await mark_as_processed(event_id)

    return {"status": "ok"}
```

### Consumer Idempotency

**Why Needed**: Kafka provides at-least-once delivery → Events may be delivered multiple times

**Implementation Options**:

1. **Database Unique Constraint** (Recommended):
   ```sql
   CREATE TABLE processed_events (
       event_id TEXT PRIMARY KEY,
       processed_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Consumer inserts event_id on first processing
   -- Subsequent deliveries → INSERT fails → Skip processing
   ```

2. **Idempotency Cache** (Alternative):
   - Redis cache: `SET event:{event_id} "processed" EX 86400`
   - Check before processing

### Error Handling (Consumer-Side)

**Transient Errors** (Retry):
- Database connection errors
- External API timeouts
- Return 500 → Dapr will retry (exponential backoff)

**Permanent Errors** (Dead Letter Queue):
- Invalid event schema
- Business logic violations
- Return 200 + log error → Event moved to DLQ

**DLQ Topic**: `{topic_name}.dlq`
- Example: `tasks.created.dlq`
- Manual review/replay required

---

## Delivery Guarantees

### Publisher Guarantees

**At-Least-Once Delivery**:
- Events published successfully or retried
- Idempotency cache prevents duplicates (publisher-side)
- DLQ captures permanent failures

**Ordering**:
- Per partition (same user_id → same partition)
- No global ordering across users

**Durability**:
- Kafka replication factor: 3 (min 2 in-sync replicas)
- Messages persisted to disk before ACK

### Consumer Guarantees

**At-Least-Once Processing**:
- Dapr redelivers events on consumer failure (non-200 response)
- Consumer must implement idempotency

**Ordering**:
- Single consumer per partition → Sequential processing per user
- Consumer group coordination (Dapr handles)

**Backpressure**:
- Consumer can control processing rate (batch size, concurrency)
- Kafka tracks consumer offset → Replay from last committed offset

---

## Error Handling

### Publisher Error Handling

**Error Types**:

1. **Idempotency Skip** (Not an error):
   - Duplicate `event_id` detected
   - Log warning, return success
   - No retry needed

2. **Transient Errors** (Retry with backoff):
   - Network timeouts
   - Kafka leader election
   - Dapr sidecar restart
   - **Action**: Retry 3 times (1s, 2s, 4s backoff)

3. **Permanent Errors** (Dead Letter Queue):
   - Max retries exceeded
   - Invalid Dapr configuration
   - **Action**: Add to DLQ for manual review

**DLQ Management**:
```python
# Get DLQ size
publisher.get_dlq_size()  # → int

# Get DLQ events for debugging
dlq_events = publisher.get_dlq_events()
# → List[Dict] with event_id, error_message, retry_count

# Clear DLQ after manual fix
publisher.clear_dlq()  # → int (count cleared)
```

### Consumer Error Handling

**Error Response Strategy**:

| Error Type                | HTTP Status | Dapr Behavior        | Recommendation              |
|---------------------------|-------------|----------------------|-----------------------------|
| Transient (DB timeout)    | 500         | Retry with backoff   | Return 500, let Dapr retry  |
| Permanent (invalid data)  | 200         | No retry             | Log error, move to DLQ      |
| Processing success        | 200         | ACK, commit offset   | Return 200                  |

**Example**:
```python
@app.post("/events/task-created")
async def handle_task_created(event: CloudEvent):
    try:
        # Process event
        await process_task(event)
        return {"status": "ok"}

    except DatabaseTimeoutError:
        # Transient error → Retry
        logger.error("DB timeout, Dapr will retry")
        return Response(status_code=500)

    except InvalidEventSchemaError as e:
        # Permanent error → Skip (don't retry)
        logger.error(f"Invalid event: {e}")
        await send_to_dlq(event, str(e))
        return {"status": "error", "message": str(e)}
```

---

## Monitoring & Observability

### Metrics to Track

**Publisher Metrics**:
- `events_published_total` (counter) - by event_type
- `events_failed_total` (counter) - by event_type, error_type
- `events_dlq_total` (gauge) - current DLQ size
- `publish_duration_seconds` (histogram) - latency distribution
- `idempotency_cache_hits_total` (counter) - duplicate events detected

**Consumer Metrics**:
- `events_consumed_total` (counter) - by topic, consumer_id
- `events_processed_success_total` (counter)
- `events_processed_failed_total` (counter)
- `consumer_lag` (gauge) - offset difference between producer and consumer
- `event_processing_duration_seconds` (histogram)

### Logging Best Practices

**Publisher Logs**:
```python
logger.info(
    f"Published event: event_id={event.event_id}, "
    f"event_type={event.event_type}, topic={topic}, "
    f"user_id={event.user_id}, retry_count={retry_count}"
)

logger.error(
    f"Dead Letter Queue: Added event {event.event_id} "
    f"(queue size: {len(self._failed_events_queue)}). "
    f"Error: {error_message}"
)
```

**Consumer Logs**:
```python
logger.info(
    f"Processing event: event_id={event_id}, "
    f"event_type={event_type}, task_id={task_id}"
)

logger.error(
    f"Failed to process event: event_id={event_id}, "
    f"error={str(e)}, will_retry={should_retry}"
)
```

### Distributed Tracing

**Trace Propagation**:
- Dapr auto-injects trace headers (W3C Trace Context)
- Events carry `traceparent` header
- Full request tracing: API → Publisher → Kafka → Consumer

**Trace Spans**:
1. **API Request**: `POST /tasks` (root span)
2. **Task Creation**: Database insert
3. **Event Publishing**: EventPublisher.publish()
4. **Kafka Write**: Dapr → Kafka
5. **Consumer Processing**: Reminder service receives event
6. **Reminder Creation**: Database insert

---

## Integration Points

### 1. Task API ↔ EventPublisher

**Integration**: Synchronous function call

**Code Location**: `backend/api/src/api/tasks.py`

**Pattern**: Fire-and-forget (don't wait for delivery)

```python
from src.services.event_publisher import get_event_publisher

# After creating task in DB
event = TaskCreatedEvent.create(...)
publisher = get_event_publisher()
publisher.publish(event)  # Non-blocking
```

**Error Handling**: Publisher handles retries internally, API doesn't block

### 2. EventPublisher ↔ Dapr Sidecar

**Integration**: HTTP REST API

**Endpoint**: `http://localhost:3500/v1.0/publish/{pubsub-name}/{topic}`

**Code Location**: `backend/api/src/services/event_publisher.py`

**Pattern**: Synchronous HTTP call with retries

```python
with DaprClient() as client:
    client.publish_event(
        pubsub_name="pubsub-kafka",
        topic_name=topic,
        data=event_data,
        data_content_type="application/json"
    )
```

### 3. Dapr ↔ Kafka

**Integration**: Dapr Kafka component

**Configuration**: `backend/api/src/dapr/components/pubsub-kafka.yaml`

**Pattern**: Dapr abstracts Kafka producer/consumer APIs

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-broker:9092"
    - name: consumerGroup
      value: "todo-app"
    - name: authRequired
      value: "false"
```

### 4. Kafka ↔ Consumers

**Integration**: Dapr Subscription + App Callback

**Consumer Registration**: `subscriptions.yaml` in each consumer service

**Pattern**: Dapr polls Kafka, invokes consumer HTTP endpoint

```
Kafka Topic → Dapr Sidecar → HTTP POST /events/{event-type} → Consumer App
```

### 5. Multi-Service Event Flow

**Scenario**: User creates task with due date

```
1. Frontend → POST /api/1/tasks (due_date=2026-02-01)
2. Task API → Create task in DB
3. Task API → EventPublisher.publish(TaskCreatedEvent)
4. EventPublisher → Dapr Sidecar (HTTP)
5. Dapr → Kafka Topic: tasks.created
6. Kafka → Dapr (Reminder Service Sidecar)
7. Dapr → POST /events/task-created (Reminder Service)
8. Reminder Service → Check due_date
9. Reminder Service → Create reminder in DB
10. Reminder Service → Schedule reminder job
```

---

## Architectural Decisions

### ADR 1: Why Kafka over RabbitMQ?

**Decision**: Use Apache Kafka as message broker

**Rationale**:
- **Retention**: Kafka persists events (7 days) → Replay capability
- **Scalability**: Kafka handles higher throughput (100K+ msgs/sec)
- **Consumer Flexibility**: Multiple independent consumers per topic
- **Event Sourcing**: Natural fit for event log pattern

**Trade-offs**:
- **Complexity**: Higher operational overhead vs RabbitMQ
- **Latency**: Slightly higher p99 latency (ms vs μs)
- **Cost**: Requires more resources (3+ brokers for HA)

### ADR 2: Why Dapr Pub/Sub vs Direct Kafka Client?

**Decision**: Use Dapr Pub/Sub abstraction layer

**Rationale**:
- **Portability**: Can swap Kafka → Redis Streams → Azure Service Bus
- **Simplification**: No Kafka client library management
- **Observability**: Built-in tracing, metrics
- **Standardization**: CloudEvents format

**Trade-offs**:
- **Performance**: Extra hop (HTTP to Dapr sidecar)
- **Dependency**: Requires Dapr runtime in every pod
- **Debugging**: One more layer to troubleshoot

### ADR 3: Why At-Least-Once vs Exactly-Once?

**Decision**: At-least-once delivery with idempotency

**Rationale**:
- **Simplicity**: Kafka exactly-once requires complex transaction coordination
- **Idempotency**: Easier to implement idempotency than distributed transactions
- **Cost**: Exactly-once requires more Kafka resources

**Trade-offs**:
- **Duplicate Events**: Consumers must handle duplicates
- **Idempotency Logic**: Every consumer needs deduplication

### ADR 4: Why Fire-and-Forget vs Synchronous Event Publishing?

**Decision**: Fire-and-forget (don't wait for Kafka ACK)

**Rationale**:
- **User Experience**: Fast API responses (don't block on event delivery)
- **Availability**: Task creation succeeds even if Kafka is down temporarily
- **Retries**: EventPublisher handles retries asynchronously

**Trade-offs**:
- **Eventual Consistency**: Consumers process events seconds later
- **Failure Visibility**: User doesn't see event publishing failures
- **DLQ Management**: Requires monitoring for failed events

---

## Future Enhancements

### Short-Term (Step 5)

- [ ] Add event schema validation (JSON Schema)
- [ ] Implement DLQ replay API (retry failed events)
- [ ] Add Prometheus metrics export
- [ ] Set up Grafana dashboards for event monitoring

### Medium-Term (Step 6+)

- [ ] Event versioning strategy (event_type: task.created.v2)
- [ ] Archive old events to S3 (Kafka → S3 connector)
- [ ] Add event filtering (consumer-side routing)
- [ ] Implement SAGA pattern for complex workflows

### Long-Term

- [ ] Migrate to Kafka Streams for stateful processing
- [ ] Add event schema registry (Confluent Schema Registry)
- [ ] Implement event snapshots for faster replay
- [ ] Multi-region event replication

---

## References

- **Event Schemas**: [event-schemas.md](event-schemas.md)
- **EventPublisher Code**: [backend/api/src/services/event_publisher.py](../../backend/api/src/services/event_publisher.py)
- **EventPublisher Tests**: [backend/api/tests/test_event_publisher.py](../../backend/api/tests/test_event_publisher.py)
- **Dapr Pub/Sub Docs**: https://docs.dapr.io/developing-applications/building-blocks/pubsub/
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **CloudEvents Spec**: https://cloudevents.io/

---

**Document Status**: Complete ✅
**Last Reviewed**: 2026-01-30
**Next Review**: After Step 5 deployment
