# Dapr Component Specifications: Step 5 - Advanced Cloud Deployment

**Created**: 2026-01-30
**Purpose**: Define Dapr component configurations for distributed application runtime

## Overview

This document specifies the Dapr components used in Step 5 to abstract infrastructure complexity and provide portable, cloud-agnostic APIs.

## Dapr Building Blocks Used

1. **Pub/Sub**: Event publishing and subscription (Kafka)
2. **State Store**: Distributed state management (Redis)
3. **Bindings**: External system integration - Cron trigger (Scheduler)
4. **Secrets**: Secret management (Kubernetes Secrets)
5. **Service Invocation**: Service-to-service calls with mTLS

---

## 1. Pub/Sub Component (Kafka)

**Component Name**: `pubsub-kafka`
**Type**: `pubsub.kafka`
**Purpose**: Event-driven communication between services

### Configuration

**Development (Minikube with Redpanda)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Redpanda broker addresses (local Kubernetes)
    - name: brokers
      value: "redpanda-0.redpanda.default.svc.cluster.local:9092"

    # Consumer group ID
    - name: consumerGroup
      value: "todo-app-consumers"

    # Authentication (none for local Redpanda)
    - name: authType
      value: "none"

    # Topic creation settings
    - name: initialOffset
      value: "oldest"

    # Message delivery settings
    - name: maxMessageBytes
      value: "1048576"  # 1MB

    # Consumer settings
    - name: sessionTimeout
      value: "6000"

    # Producer settings
    - name: producerAcks
      value: "all"
```

**Production (Confluent Cloud / Redpanda Cloud)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: production
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Cloud Kafka broker addresses
    - name: brokers
      value: "pkc-xxxxx.us-west-2.aws.confluent.cloud:9092"

    # Consumer group ID
    - name: consumerGroup
      value: "todo-app-production-consumers"

    # Authentication (SASL/SCRAM for cloud)
    - name: authType
      value: "password"

    - name: saslUsername
      secretKeyRef:
        name: kafka-credentials
        key: username

    - name: saslPassword
      secretKeyRef:
        name: kafka-credentials
        key: password

    - name: saslMechanism
      value: "SCRAM-SHA-256"

    # TLS/SSL settings
    - name: enableTLS
      value: "true"

    # Topic creation settings
    - name: initialOffset
      value: "oldest"

    # Message delivery settings
    - name: maxMessageBytes
      value: "1048576"  # 1MB

    # Producer settings
    - name: producerAcks
      value: "all"
    - name: producerIdempotent
      value: "true"
```

### Topics

All topics are created automatically by Dapr when first published to:

| Topic Name | Purpose | Partitions | Retention |
|------------|---------|------------|-----------|
| tasks.created | Task creation events | 3 | 7 days |
| tasks.updated | Task update events | 3 | 7 days |
| tasks.completed | Task completion events | 3 | 7 days |
| tasks.deleted | Task deletion events | 3 | 7 days |
| reminders.due | Reminder due events | 3 | 7 days |

---

## 2. State Store Component (Redis)

**Component Name**: `statestore-redis`
**Type**: `state.redis`
**Purpose**: Distributed state management for caching and session data

### Configuration

**Development (Minikube with Redis)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
    # Redis connection
    - name: redisHost
      value: "redis-master.default.svc.cluster.local:6379"

    # Authentication
    - name: redisPassword
      secretKeyRef:
        name: redis-credentials
        key: password

    # Database selection
    - name: redisDB
      value: "0"

    # Connection settings
    - name: enableTLS
      value: "false"

    # TTL settings
    - name: ttlInSeconds
      value: "3600"  # 1 hour default TTL
```

**Production (Managed Redis - Azure/GCP/Oracle)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
  namespace: production
spec:
  type: state.redis
  version: v1
  metadata:
    # Managed Redis connection
    - name: redisHost
      value: "todo-redis.redis.cache.windows.net:6380"  # Azure example

    # Authentication
    - name: redisPassword
      secretKeyRef:
        name: redis-credentials
        key: password

    # TLS/SSL settings
    - name: enableTLS
      value: "true"

    # Database selection
    - name: redisDB
      value: "0"

    # TTL settings
    - name: ttlInSeconds
      value: "3600"
```

### Usage Patterns

- **Caching**: Frequently accessed task data, user preferences
- **Session Management**: User session data (future feature)
- **Distributed Locking**: Prevent duplicate reminder processing (future feature)
- **Rate Limiting**: API rate limiting counters (future feature)

---

## 3. Cron Binding Component (Scheduler)

**Component Name**: `cron-reminder-processor`
**Type**: `bindings.cron`
**Purpose**: Trigger reminder processing every 1 minute

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-reminder-processor
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
    # Cron schedule (every 1 minute)
    - name: schedule
      value: "*/1 * * * *"

    # Direction (input binding)
    - name: direction
      value: "input"
```

### Cron Schedule Format

```
*/1 * * * *
│  │ │ │ │
│  │ │ │ └─── Day of week (0-7) (Sunday=0 or 7)
│  │ │ └───── Month (1-12)
│  │ └─────── Day of month (1-31)
│  └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Examples**:
- `*/1 * * * *`: Every 1 minute
- `*/5 * * * *`: Every 5 minutes
- `0 * * * *`: Every hour at minute 0
- `0 9 * * *`: Every day at 9:00 AM

### Binding Endpoint

The cron binding triggers an HTTP POST request to the reminder service:

```
POST http://localhost:8001/cron
Content-Type: application/json

{}
```

---

## 4. Secrets Component (Kubernetes Secrets)

**Component Name**: `kubernetes-secrets`
**Type**: `secretstores.kubernetes`
**Purpose**: Securely access secrets from Kubernetes Secret resources

### Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### Secret Access

Applications can retrieve secrets using Dapr Secrets API:

```python
from dapr.clients import DaprClient

with DaprClient() as client:
    # Get secret from Kubernetes Secret named "database-credentials"
    secret = client.get_secret(
        store_name="kubernetes-secrets",
        key="database-credentials",
        metadata={"namespace": "default"}
    )
    database_url = secret.secrets["url"]
```

### Secrets Managed

| Secret Name | Keys | Purpose |
|-------------|------|---------|
| database-credentials | url, username, password | PostgreSQL connection |
| kafka-credentials | username, password | Kafka authentication (production) |
| redis-credentials | password | Redis authentication |
| openai-credentials | api_key | OpenAI API key (chatbot) |
| better-auth-credentials | secret | Better Auth secret |

---

## 5. Service Invocation

**Purpose**: Service-to-service communication with mTLS, retries, and observability

### Configuration

Service invocation is enabled by default when Dapr sidecar is configured. No additional component needed.

### App IDs

Each service has a unique Dapr app-id:

| Service | Dapr App ID | Port |
|---------|-------------|------|
| Backend API | `backend` | 8000 |
| Reminder Service | `reminder-service` | 8001 |
| Frontend | `frontend` | 3000 |

### Usage Example

**Backend → Reminder Service**:
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    # Invoke reminder service health check
    response = client.invoke_method(
        app_id="reminder-service",
        method_name="health",
        http_verb="GET"
    )
```

### Features

- **mTLS**: Automatic mutual TLS between services
- **Service Discovery**: Automatic service discovery via Kubernetes DNS
- **Retries**: Configurable retry logic for failed calls
- **Circuit Breaking**: Prevent cascading failures
- **Observability**: Automatic distributed tracing with OpenTelemetry

---

## Dapr Sidecar Annotations

### Backend API

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"
  dapr.io/log-level: "info"
  dapr.io/metrics-port: "9090"
```

### Reminder Service

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "reminder-service"
  dapr.io/app-port: "8001"
  dapr.io/enable-api-logging: "true"
  dapr.io/log-level: "info"
  dapr.io/metrics-port: "9091"
```

### Frontend

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "frontend"
  dapr.io/app-port: "3000"
  dapr.io/enable-api-logging: "false"
  dapr.io/log-level: "warn"
```

---

## Component Scoping

Components can be scoped to specific applications:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata: [...]
  scopes:
    - backend
    - reminder-service
```

---

## Environment-Specific Configuration

### Minikube (Development)

- **Kafka**: Redpanda (single broker, no auth)
- **Redis**: Redis (single instance, password auth)
- **Secrets**: Kubernetes Secrets (local)
- **State**: Redis (local)

### Cloud Production (AKS/GKE/OKE)

- **Kafka**: Confluent Cloud or Redpanda Cloud (SASL/SCRAM auth, TLS)
- **Redis**: Managed Redis (Azure Cache, Cloud Memorystore, OCI Cache)
- **Secrets**: Kubernetes Secrets or Cloud Secret Manager
- **State**: Managed Redis (TLS enabled)

---

## Monitoring and Observability

### Dapr Metrics

Dapr sidecars expose Prometheus metrics on port 9090:

- `dapr_http_server_request_count`: HTTP request count
- `dapr_http_server_request_latencies`: HTTP request latency
- `dapr_component_pubsub_ingress_count`: Pub/Sub message ingress count
- `dapr_component_pubsub_egress_count`: Pub/Sub message egress count
- `dapr_component_state_count`: State operation count

### Dapr Tracing

Dapr automatically integrates with Zipkin/Jaeger for distributed tracing:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
```

---

## Practical Implementation Examples (T087)

### 1. Publishing Events via Dapr Pub/Sub

**Location**: `backend/api/src/services/event_publisher.py`

```python
from dapr.clients import DaprClient
from ..models.event import Event

class EventPublisher:
    def __init__(self, pubsub_name: str = "pubsub-kafka"):
        self.pubsub_name = pubsub_name

    def publish(self, event: Event) -> bool:
        """Publish event to Kafka via Dapr Pub/Sub API."""
        topic = self._get_topic_name(event.event_type)
        event_data = event.model_dump(mode="json")

        with DaprClient() as client:
            client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=event_data,
                data_content_type="application/json"
            )
        return True

    def _get_topic_name(self, event_type: str) -> str:
        """Map event types to Kafka topics."""
        topic_map = {
            "task.created": "tasks.created",
            "task.updated": "tasks.updated",
            "task.completed": "tasks.completed",
            "task.deleted": "tasks.deleted",
            "reminder.due": "reminders.due"
        }
        return topic_map.get(event_type, event_type)
```

**Features**:
- ✅ No direct Kafka client needed - Dapr handles connection
- ✅ Automatic retries with exponential backoff
- ✅ Idempotency via event_id tracking
- ✅ Dead letter queue for failed events

### 2. Subscribing to Events via Dapr

**Location**: `backend/reminder-service/src/main.py`

```python
from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI()

# Dapr subscription configuration endpoint
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Tell Dapr which topics to subscribe to."""
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

# Event handler endpoint
@app.post("/events/task-created")
async def handle_task_created_event(event: Dict[str, Any]):
    """Handle task.created event from Dapr."""
    task_id = event.get('data', {}).get('payload', {}).get('task_id')
    # Process event...
    return {"status": "success"}
```

**Features**:
- ✅ Declarative subscription via `/dapr/subscribe` endpoint
- ✅ Automatic message delivery from Dapr sidecar
- ✅ Built-in retry logic and error handling

### 3. Service Invocation via Dapr

**Location**: `backend/api/src/services/dapr_client.py`

```python
from dapr.clients import DaprClient
from typing import Dict, Any, Optional

class DaprServiceClient:
    """Helper for invoking other services via Dapr Service Invocation API."""

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        http_verb: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invoke a method on another service."""
        with DaprClient() as client:
            response = client.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=data,
                http_verb=http_verb
            )
            return response.json()

    async def invoke_reminder_service(
        self,
        method_name: str,
        http_verb: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convenience method to invoke reminder service."""
        return await self.invoke_service(
            app_id="reminder-service",
            method_name=method_name,
            http_verb=http_verb,
            data=data
        )
```

**Usage**:
```python
# Backend calls reminder service health check
client = DaprServiceClient()
result = await client.invoke_reminder_service("health")
print(result)  # {'status': 'healthy', 'service': 'reminder-service'}
```

**Features**:
- ✅ No hardcoded URLs - Dapr handles service discovery
- ✅ Automatic mTLS encryption between services
- ✅ Built-in retries and circuit breaking
- ✅ Distributed tracing via OpenTelemetry

### 4. Fetching Secrets via Dapr

**Location**: `backend/api/src/config.py`

```python
import os
from dapr.clients import DaprClient

class DaprSecretsConfig:
    """Helper for fetching secrets from Dapr Secrets Store."""

    def __init__(
        self,
        secret_store_name: str = "kubernetes-secrets",
        use_dapr: bool = False
    ):
        self.secret_store_name = secret_store_name
        self.use_dapr = use_dapr

    def get_secret(self, secret_key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from Dapr or environment variable."""
        if self.use_dapr:
            try:
                with DaprClient() as client:
                    secret_response = client.get_secret(
                        store_name=self.secret_store_name,
                        key=secret_key
                    )
                    return secret_response.secret.get(secret_key)
            except Exception as e:
                logger.warning(f"Failed to fetch secret from Dapr: {e}")

        # Fallback to environment variable
        return os.getenv(secret_key, default)

# Usage
dapr_secrets = DaprSecretsConfig(use_dapr=True)
openai_key = dapr_secrets.get_secret("OPENAI_API_KEY")
```

**Features**:
- ✅ Centralized secret management via Kubernetes Secrets or Vault
- ✅ Automatic secret rotation support
- ✅ Fallback to environment variables for local development

### 5. Helm Values Configuration

**Location**: `helm/todo-app/values-dev.yaml`

```yaml
dapr:
  enabled: true

  # Pub/Sub component (Kafka/Redpanda)
  pubsub:
    name: pubsub-kafka
    type: pubsub.kafka
    version: v1
    metadata:
      - name: brokers
        value: "redpanda:9092"
      - name: authType
        value: "none"
      - name: consumerGroup
        value: "todo-app-group"

  # State Store component (Redis)
  statestore:
    name: statestore-redis
    type: state.redis
    version: v1
    metadata:
      - name: redisHost
        value: "redis-master:6379"
      - name: redisPassword
        secretKeyRef:
          name: redis
          key: redis-password

  # Cron Binding component
  cronBinding:
    name: cron-reminder-processor
    type: bindings.cron
    version: v1
    metadata:
      - name: schedule
        value: "*/1 * * * *"  # Every 1 minute
      - name: direction
        value: "input"

  # Secrets Store component
  secrets:
    name: kubernetes-secrets
    type: secretstores.kubernetes
    version: v1
    metadata:
      - name: defaultNamespace
        value: "default"
```

### 6. Kubernetes Deployment with Dapr Annotations

**Location**: `helm/todo-app/templates/backend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  template:
    metadata:
      annotations:
        # Dapr sidecar annotations
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
```

**What happens**:
1. Dapr sidecar injector detects annotations
2. Adds Dapr sidecar container to pod (2/2 containers)
3. Sidecar runs on ports 3500 (HTTP) and 50001 (gRPC)
4. Application calls Dapr sidecar for pub/sub, state, secrets, etc.

---

## Benefits of Dapr Integration

### Before Dapr (Direct Kafka/Redis)
- ❌ Applications tightly coupled to Kafka client libraries
- ❌ Different SDKs for different languages (kafka-python, node-kafka, etc.)
- ❌ Manual retry logic, error handling, circuit breaking
- ❌ Hardcoded broker URLs and credentials
- ❌ No built-in observability (tracing, metrics)
- ❌ Complex service-to-service communication
- ❌ Secret management scattered across env vars

### After Dapr
- ✅ Language-agnostic HTTP/gRPC APIs for all infrastructure
- ✅ Swap Kafka for RabbitMQ/Azure Service Bus without code changes
- ✅ Built-in retries, circuit breaking, bulkheading
- ✅ Configuration externalized to Dapr components
- ✅ Automatic distributed tracing and metrics
- ✅ mTLS and service discovery for all service calls
- ✅ Centralized secret management with rotation support

---

## Troubleshooting

### Check Dapr Sidecar Status
```bash
# Check if pods have Dapr sidecars (should show 2/2 containers)
kubectl get pods -l app.kubernetes.io/component=backend

# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Check Dapr components
kubectl get components
```

### Test Pub/Sub Locally
```bash
# Port-forward to backend Dapr sidecar
kubectl port-forward <backend-pod> 3500:3500

# Publish event via Dapr HTTP API
curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/tasks.created \
  -H "Content-Type: application/json" \
  -d '{"event_id": "test-123", "event_type": "task.created"}'
```

### Test Service Invocation
```bash
# Call reminder-service from backend via Dapr
curl http://localhost:3500/v1.0/invoke/reminder-service/method/health
```

---

## References

- Dapr Documentation: https://docs.dapr.io/
- Dapr Pub/Sub: https://docs.dapr.io/developing-applications/building-blocks/pubsub/
- Dapr State Management: https://docs.dapr.io/developing-applications/building-blocks/state-management/
- Dapr Bindings: https://docs.dapr.io/developing-applications/building-blocks/bindings/
- Dapr Secrets: https://docs.dapr.io/developing-applications/building-blocks/secrets/
- Dapr Service Invocation: https://docs.dapr.io/developing-applications/building-blocks/service-invocation/
- Kafka Component: https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/
- Redis Component: https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-redis/
