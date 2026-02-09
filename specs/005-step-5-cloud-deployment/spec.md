# Feature Specification: Step 5 - Advanced Cloud Deployment

**Feature Branch**: `005-step-5-cloud-deployment`
**Created**: 2026-01-30
**Status**: Draft
**Input**: User description: "Create Step 5: Advanced Cloud Deployment specification with advanced features, event-driven architecture, Dapr, and cloud deployment"

## Overview

Step 5 transforms the Todo Chatbot into a production-grade distributed system with advanced task management features (recurring tasks, due dates, reminders, priorities, tags, search, filter, sort), event-driven architecture using Kafka and Dapr, multi-environment deployment (Minikube + cloud), CI/CD automation via GitHub Actions, and comprehensive monitoring and logging infrastructure.

**Architecture Evolution**:
- **From**: Basic web application (Step 2-3) deployed on local Kubernetes (Step 4)
- **To**: Production-grade distributed system with advanced features, event-driven patterns, cloud deployment, CI/CD automation, and full observability

**Key Components**:
- Advanced task management features (8 new capabilities)
- Event-driven architecture (Kafka topics, event consumers)
- Dapr distributed runtime (5 building blocks)
- Reminder service (asynchronous reminder processing)
- Multi-environment deployment (Minikube local + Azure AKS/GCP GKE/Oracle Cloud)
- CI/CD pipeline (GitHub Actions)
- Monitoring stack (Prometheus, Grafana, Zipkin/Jaeger, log aggregation)

## User Scenarios & Testing

### User Story 1 - Recurring Tasks (Priority: P1)

Users need to create tasks that repeat automatically on a schedule (daily standup, weekly reports, monthly reviews) without manually recreating them each time.

**Why this priority**: Recurring tasks are the most requested advanced feature and provide immediate value by reducing repetitive work. This is the foundation for advanced task management.

**Independent Test**: Can be fully tested by creating a recurring task with a daily recurrence rule, waiting for the next occurrence time, and verifying the task automatically generates a new instance. Delivers value immediately by automating task creation.

**Acceptance Scenarios**:

1. **Given** a user creates a task titled "Daily Standup" with recurrence rule "FREQ=DAILY", **When** the task due date passes, **Then** a new instance of the task is automatically created with the next occurrence date
2. **Given** a user creates a recurring task "Weekly Team Meeting" with "FREQ=WEEKLY;BYDAY=MO", **When** Monday arrives, **Then** the task appears in the user's task list with the correct due date
3. **Given** a user creates a recurring task with "FREQ=MONTHLY;BYMONTHDAY=1", **When** the first day of the month arrives, **Then** a new task instance is created automatically
4. **Given** a recurring task has been created, **When** the user views the task details, **Then** the recurrence pattern is displayed in human-readable format (e.g., "Repeats daily" or "Repeats every Monday")
5. **Given** a user completes one instance of a recurring task, **When** the next occurrence time arrives, **Then** a new incomplete task is created (completion doesn't stop recurrence)

---

### User Story 2 - Due Dates and Reminders (Priority: P1)

Users need to set deadlines for tasks and receive reminders before the deadline to ensure timely completion and avoid missing important tasks.

**Why this priority**: Due dates and reminders are critical for task management effectiveness. Without them, users miss deadlines and the application provides limited value over a simple checklist.

**Independent Test**: Can be fully tested by creating a task with a due date 5 minutes in the future and a 2-minute reminder offset, then verifying a reminder event is published 3 minutes in the future and can be consumed by a notification service.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date of "2026-02-01 14:00", **When** the task is saved, **Then** the due date is stored and displayed in the task details
2. **Given** a task has a due date and reminder offset of 30 minutes, **When** 30 minutes before the due date arrives, **Then** a reminder event is published to the Kafka topic "reminders.due"
3. **Given** a reminder service is running, **When** a reminder event is published, **Then** the service consumes the event and marks the reminder as sent in the database
4. **Given** multiple tasks have reminders due at the same time, **When** the reminder processing cron job runs, **Then** all due reminders are processed within 60 seconds
5. **Given** a user updates a task's due date, **When** the due date changes, **Then** the associated reminder is rescheduled with the new due date minus the reminder offset
6. **Given** a task is completed before the reminder time, **When** the reminder time arrives, **Then** no reminder is sent (reminders are skipped for completed tasks)

---

### User Story 3 - Task Priorities and Tags (Priority: P2)

Users need to categorize tasks by priority level (urgent, high, medium, low) and apply multiple tags to organize tasks by project, context, or category for better task management and filtering.

**Why this priority**: Priorities and tags enable users to focus on important work and organize tasks effectively. While valuable, they can be used independently of recurring tasks and reminders.

**Independent Test**: Can be fully tested by creating tasks with different priorities and tags, then filtering and sorting the task list by priority and tag combinations to verify correct results.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** they set the priority to "urgent", **Then** the priority is saved and displayed with the task
2. **Given** a user creates a task, **When** they add tags "work", "meeting", and "q1-goals", **Then** all three tags are associated with the task and displayed
3. **Given** multiple tasks exist with different priorities, **When** the user sorts tasks by priority, **Then** tasks are ordered: urgent → high → medium → low
4. **Given** tasks have various tags, **When** the user filters tasks by tag "work", **Then** only tasks containing the "work" tag are displayed
5. **Given** a user views their task list, **When** they filter by priority "high" and tag "meeting", **Then** only tasks with both priority=high AND tag=meeting are shown
6. **Given** a task has multiple tags, **When** the user removes one tag, **Then** the tag is disassociated from the task but other tags remain

---

### User Story 4 - Search, Filter, and Sort (Priority: P2)

Users need to quickly find specific tasks using full-text search, filter tasks by multiple criteria (status, priority, tags, due date ranges), and sort results by various fields to efficiently locate and prioritize their work.

**Why this priority**: Search and filtering are essential for managing large task lists (100+ tasks). These capabilities work independently of other advanced features and provide immediate productivity gains.

**Independent Test**: Can be fully tested by creating 50 tasks with varied titles, descriptions, priorities, tags, and due dates, then performing search queries, multi-criteria filters, and different sort orders to verify correct results.

**Acceptance Scenarios**:

1. **Given** a user has multiple tasks, **When** they search for "meeting notes", **Then** all tasks containing "meeting" or "notes" in the title or description are returned
2. **Given** search results are returned, **When** the user views the results, **Then** matching text is highlighted in the task title and description
3. **Given** a user applies filters, **When** they filter by status=incomplete AND priority=high AND tag=work, **Then** only tasks matching all three criteria are displayed
4. **Given** tasks have various due dates, **When** the user filters by due date range "2026-02-01 to 2026-02-07", **Then** only tasks with due dates in that week are shown
5. **Given** filtered tasks are displayed, **When** the user sorts by "due date ascending", **Then** tasks are ordered from soonest to latest due date
6. **Given** a user sorts tasks, **When** they sort by "created date descending", **Then** the most recently created tasks appear first
7. **Given** a user has applied filters, **When** they clear all filters, **Then** all tasks are displayed again

---

### User Story 5 - Event-Driven Task Management (Priority: P3)

The system needs to publish events for all task state changes (created, updated, completed, deleted) to enable asynchronous processing, audit trails, integrations, and future features like notifications and analytics.

**Why this priority**: Event-driven architecture is foundational for scalability and extensibility but provides no direct user-facing value initially. It enables reminders (P1) and future integrations.

**Independent Test**: Can be fully tested by performing task operations (create, update, complete, delete) and verifying corresponding events are published to Kafka topics with correct event schemas and can be consumed by test consumers.

**Acceptance Scenarios**:

1. **Given** a user creates a new task, **When** the task is saved to the database, **Then** a "task.created" event is published to Kafka with the task details
2. **Given** a user updates a task title, **When** the update is saved, **Then** a "task.updated" event is published with old and new values
3. **Given** a user marks a task complete, **When** the status changes, **Then** a "task.completed" event is published with the task ID and completion timestamp
4. **Given** a user deletes a task, **When** the task is removed from the database, **Then** a "task.deleted" event is published with the task ID
5. **Given** events are published, **When** a consumer service subscribes to the topic, **Then** events are delivered to the consumer in the order they were published
6. **Given** an event is published, **When** the Kafka broker is temporarily unavailable, **Then** the event is queued and published when the broker recovers (delivery guarantee)
7. **Given** events are published, **When** the consumer processes an event, **Then** the event data includes: event_id, event_type, timestamp, user_id, and payload with task details

---

### User Story 6 - Reminder Service (Priority: P3)

The system needs a dedicated reminder service that consumes task events, calculates reminder times, schedules reminders, and publishes reminder events when due to enable timely task notifications.

**Why this priority**: The reminder service is infrastructure that enables the reminder feature (P1) but provides no standalone value. It must be implemented to support User Story 2.

**Independent Test**: Can be fully tested by publishing a "task.created" event with a due date 10 minutes in the future and 5-minute reminder offset, then verifying the reminder service calculates the correct reminder time (5 minutes from now) and publishes a "reminder.due" event at the scheduled time.

**Acceptance Scenarios**:

1. **Given** a "task.created" event is published with due_date and reminder_offset, **When** the reminder service consumes the event, **Then** a reminder record is created in the database with scheduled_at = due_date - reminder_offset
2. **Given** reminders are scheduled, **When** the cron binding triggers the reminder processor every minute, **Then** all reminders with scheduled_at <= current_time and sent=false are processed
3. **Given** a reminder is due, **When** the processor handles it, **Then** a "reminder.due" event is published to Kafka and the reminder is marked sent=true
4. **Given** a "task.updated" event changes the due date, **When** the reminder service consumes the event, **Then** the associated reminder's scheduled_at is updated to reflect the new due date
5. **Given** a "task.deleted" event is published, **When** the reminder service consumes it, **Then** any scheduled reminders for that task are deleted
6. **Given** a "task.completed" event is published, **When** the reminder service consumes it, **Then** the reminder is marked as sent=true to prevent duplicate reminders
7. **Given** the reminder service crashes, **When** it restarts, **Then** it resumes processing from the last committed Kafka offset (no duplicate or lost reminders)

---

### User Story 7 - Dapr Integration (Priority: P4)

The system needs to integrate Dapr distributed application runtime to abstract infrastructure complexity (Kafka, Redis, secrets management) and provide portable, cloud-agnostic APIs for pub/sub, state management, bindings, and service invocation.

**Why this priority**: Dapr is infrastructure enablement that simplifies development and operations but provides no direct user value. It's essential for event-driven architecture (P3) and cloud deployment (P5).

**Independent Test**: Can be fully tested by deploying the backend service with a Dapr sidecar, publishing an event via Dapr Pub/Sub API to a test topic, subscribing to the topic via Dapr subscription, and verifying the event is delivered correctly without direct Kafka client usage.

**Acceptance Scenarios**:

1. **Given** Dapr is installed on the cluster, **When** backend pods are deployed, **Then** each pod has a Dapr sidecar container running alongside the application container
2. **Given** a Dapr Pub/Sub component is configured for Kafka, **When** the backend publishes an event via Dapr Pub/Sub API, **Then** the event is delivered to the configured Kafka topic
3. **Given** a reminder service subscribes to a topic via Dapr subscription, **When** an event is published to that topic, **Then** the Dapr sidecar delivers the event to the reminder service's HTTP endpoint
4. **Given** a Dapr State Store component is configured for Redis, **When** the backend saves state via Dapr State API, **Then** the state is persisted in Redis and retrievable via Dapr State API
5. **Given** a Dapr Cron Binding is configured with schedule "*/1 * * * *", **When** the schedule triggers, **Then** Dapr invokes the reminder service's binding endpoint every minute
6. **Given** Dapr Secrets component is configured for Kubernetes Secrets, **When** the backend requests a secret via Dapr Secrets API, **Then** the secret value is retrieved from Kubernetes and returned
7. **Given** services use Dapr Service Invocation, **When** the frontend calls the backend via Dapr, **Then** Dapr handles service discovery, retries, and mTLS automatically

---

### User Story 8 - Local Deployment on Minikube (Priority: P4)

Developers need to deploy the complete Step 5 application stack (backend, frontend, reminder service, Kafka, Redis, Dapr) on a local Minikube cluster for development, testing, and validation before cloud deployment.

**Why this priority**: Local deployment is essential for development workflow but provides no direct user value. It enables developers to test the full distributed system locally before cloud deployment (P5).

**Independent Test**: Can be fully tested by deploying the Helm chart to Minikube with values-minikube.yaml, verifying all pods are running (backend, frontend, reminder-service, each with Dapr sidecars), and executing end-to-end tests covering all advanced features.

**Acceptance Scenarios**:

1. **Given** Minikube is running with 2+ CPUs and 4GB+ RAM, **When** Dapr is initialized on Minikube, **Then** Dapr system pods are running in the dapr-system namespace
2. **Given** Kafka/Redpanda is deployed on Minikube, **When** the deployment completes, **Then** Kafka brokers are accessible at the configured service endpoint
3. **Given** Redis is deployed on Minikube, **When** the deployment completes, **Then** Redis is accessible for Dapr State Store usage
4. **Given** Dapr components are applied to Minikube, **When** kubectl get components is executed, **Then** all components (pubsub, statestore, cron, secrets) show status=ready
5. **Given** the Helm chart is deployed with values-minikube.yaml, **When** kubectl get pods is executed, **Then** backend, frontend, and reminder-service pods are running with Dapr sidecars (2/2 ready)
6. **Given** all services are deployed, **When** the frontend is accessed via minikube service command, **Then** the UI loads and all Step 5 features are functional
7. **Given** events are published, **When** the reminder service logs are checked, **Then** event consumption and reminder processing are visible in the logs
8. **Given** a rolling update is performed, **When** helm upgrade is executed, **Then** pods are updated with zero downtime (new pods start before old pods terminate)

---

### User Story 9 - Cloud Deployment (Priority: P5)

The application needs to be deployed to production-grade Kubernetes on Azure AKS, Google Cloud GKE, or Oracle Cloud with managed services (PostgreSQL, Kafka, Redis), CI/CD automation, and comprehensive monitoring to serve real users at scale.

**Why this priority**: Cloud deployment is the final step that makes the application production-ready and accessible to users. It depends on all previous user stories being complete and tested locally.

**Independent Test**: Can be fully tested by deploying to a cloud Kubernetes cluster via CI/CD pipeline, verifying all pods are running in production namespace, accessing the application via cloud load balancer, executing end-to-end tests, and monitoring metrics/logs/traces to confirm production readiness.

**Acceptance Scenarios**:

1. **Given** a cloud Kubernetes cluster (AKS/GKE/OKE) is provisioned, **When** kubectl cluster-info is executed, **Then** cluster details show the cloud-managed control plane
2. **Given** managed PostgreSQL is provisioned, **When** the backend connects to the database, **Then** connection succeeds and migrations run successfully
3. **Given** Confluent Cloud or Redpanda Cloud Kafka is configured, **When** Dapr Pub/Sub component is applied, **Then** events publish successfully to the cloud-managed Kafka brokers
4. **Given** managed Redis is provisioned, **When** Dapr State Store component is applied, **Then** state operations succeed against the cloud Redis instance
5. **Given** Dapr is installed on the cloud cluster, **When** Dapr components are applied, **Then** all components (pubsub, statestore, cron, secrets) are configured for cloud services
6. **Given** GitHub Actions CI/CD pipeline is configured, **When** code is pushed to main branch, **Then** pipeline runs tests, builds images, pushes to container registry, and deploys to cloud cluster via Helm
7. **Given** the application is deployed to cloud, **When** the frontend load balancer URL is accessed, **Then** the UI loads over HTTPS and all features are functional
8. **Given** the application is running in production, **When** monitoring dashboards are accessed, **Then** Prometheus metrics, Grafana dashboards, and distributed traces are visible
9. **Given** logs are being generated, **When** log aggregation service is queried, **Then** backend, frontend, and reminder-service logs are searchable and filterable
10. **Given** alerting is configured, **When** error rate exceeds 1% or latency exceeds 500ms, **Then** alerts are triggered in Prometheus Alertmanager

---

### User Story 10 - CI/CD Automation (Priority: P5)

Developers need an automated CI/CD pipeline using GitHub Actions that runs tests, builds container images, pushes to registry, and deploys to cloud Kubernetes on every merge to main branch to enable rapid, reliable, and repeatable deployments.

**Why this priority**: CI/CD automation is essential for production operations but provides no direct user value. It enables fast iteration and reduces deployment errors for cloud deployment (P5).

**Independent Test**: Can be fully tested by creating a pull request with a code change, merging to main, and verifying GitHub Actions workflow runs successfully through all stages (test, build, push, deploy), then confirming the updated application is running in production.

**Acceptance Scenarios**:

1. **Given** a pull request is created, **When** GitHub Actions CI workflow runs, **Then** all tests (backend unit, integration, frontend tests) execute and pass
2. **Given** CI workflow passes, **When** the workflow builds Docker images, **Then** backend, frontend, and reminder-service images are built with tags matching the git commit SHA
3. **Given** images are built, **When** the workflow pushes to container registry, **Then** all three images are pushed successfully and tagged with both commit SHA and "latest"
4. **Given** images are pushed, **When** Helm lint is executed, **Then** the Helm chart passes validation with no errors
5. **Given** security scanning is configured, **When** images are scanned, **Then** scan results are reported (vulnerabilities identified if present)
6. **Given** a pull request is merged to main, **When** GitHub Actions CD workflow runs, **Then** the workflow deploys the application to the cloud cluster using Helm with the new image tags
7. **Given** deployment completes, **When** smoke tests execute against production, **Then** health checks pass and critical user flows succeed
8. **Given** deployment fails, **When** health checks fail or smoke tests fail, **Then** the deployment is automatically rolled back to the previous version
9. **Given** deployment succeeds, **When** the deployment completes, **Then** the new application version is serving traffic and old pods are terminated
10. **Given** GitHub Secrets are configured, **When** the workflow runs, **Then** secrets (cloud credentials, API keys, database URLs) are injected securely without being exposed in logs

---

### User Story 11 - Monitoring and Observability (Priority: P5)

Operations teams need comprehensive monitoring, logging, and distributed tracing infrastructure (Prometheus, Grafana, Zipkin/Jaeger, log aggregation) to track application health, performance, and troubleshoot issues in production.

**Why this priority**: Monitoring is critical for production operations but provides no direct user value. It enables proactive incident response and performance optimization for cloud deployment (P5).

**Independent Test**: Can be fully tested by deploying monitoring stack (Prometheus, Grafana, Zipkin), generating application traffic, and verifying metrics are collected, dashboards display data, traces are captured, logs are aggregated, and alerts trigger when thresholds are exceeded.

**Acceptance Scenarios**:

1. **Given** Prometheus is deployed, **When** application metrics endpoints are scraped, **Then** metrics (request count, latency, error rate) are collected and queryable in Prometheus UI
2. **Given** Grafana is deployed, **When** Grafana dashboards are accessed, **Then** dashboards display application metrics, Kubernetes cluster health, and Dapr component status
3. **Given** Zipkin or Jaeger is deployed, **When** a request flows through frontend → backend → reminder service, **Then** a distributed trace is captured showing the complete request path with timing
4. **Given** log aggregation is configured, **When** backend logs an error, **Then** the error log is searchable in the log aggregation service (Loki, ELK, or cloud logging)
5. **Given** Prometheus Alertmanager is configured, **When** error rate exceeds 1% for 5 minutes, **Then** an alert is triggered and sent to the configured notification channel
6. **Given** Prometheus Alertmanager is configured, **When** p95 latency exceeds 500ms for 5 minutes, **Then** an alert is triggered
7. **Given** Kafka consumer lag alerts are configured, **When** reminder service lag exceeds 1000 messages, **Then** an alert is triggered
8. **Given** pod restart alerts are configured, **When** a pod crashes and restarts, **Then** an alert is triggered with pod name and namespace
9. **Given** distributed tracing is enabled, **When** traces are viewed in Jaeger UI, **Then** trace context propagates across HTTP requests, Kafka events, and Dapr calls
10. **Given** business metrics are instrumented, **When** tasks are created, completed, and reminders are sent, **Then** these metrics are collected and visible in Grafana dashboards

---

### Edge Cases

- What happens when a recurring task's recurrence rule is invalid (malformed RRULE syntax)?
  - System MUST reject the task creation/update with a clear error message indicating the RRULE format is invalid
- What happens when a task's due date is set to a past date?
  - System MUST accept the past due date but immediately mark the reminder as overdue (reminder sent immediately or skipped)
- What happens when a user creates 100+ tags on a single task?
  - System MUST enforce a reasonable tag limit (e.g., 10 tags per task) to prevent abuse
- What happens when the reminder service crashes while processing reminders?
  - Dapr guarantees at-least-once delivery; reminder service MUST be idempotent (check reminder.sent before sending)
- What happens when Kafka is unavailable when publishing events?
  - Events MUST be queued locally and retried when Kafka recovers (Dapr handles retry logic)
- What happens when the cloud database connection is lost?
  - Backend MUST return 503 Service Unavailable and Kubernetes health checks MUST trigger pod restart
- What happens when a user searches with special characters (e.g., wildcards, regex)?
  - System MUST sanitize search input to prevent SQL injection and regex denial-of-service attacks
- What happens when GitHub Actions workflow fails during deployment?
  - Deployment MUST be rolled back automatically and monitoring alerts MUST notify the team
- What happens when a reminder is scheduled but the task is deleted before the reminder fires?
  - Reminder service MUST consume task.deleted events and delete associated reminders
- What happens when the Minikube cluster runs out of resources?
  - Pods MUST be evicted based on priority and resource limits to prevent cluster failure
- What happens when multiple reminder services (replicas) process the same reminder concurrently?
  - Reminder records MUST use optimistic locking or database constraints to prevent duplicate reminder sends

## Requirements

### Functional Requirements

**Advanced Task Features**:

- **FR-001**: System MUST support creating tasks with recurrence rules using iCal RRULE format (FREQ=DAILY, FREQ=WEEKLY;BYDAY=MO, FREQ=MONTHLY;BYMONTHDAY=1, etc.)
- **FR-002**: System MUST automatically generate new task instances for recurring tasks when the next occurrence time arrives
- **FR-003**: System MUST allow users to set due dates on tasks with timestamp precision (YYYY-MM-DD HH:MM:SS)
- **FR-004**: System MUST allow users to set reminder offsets on tasks (minutes before due date)
- **FR-005**: System MUST support task priorities with four levels: low, medium, high, urgent
- **FR-006**: System MUST allow users to add multiple tags to tasks (minimum 1, maximum 10 tags per task)
- **FR-007**: System MUST support full-text search across task title and description fields
- **FR-008**: System MUST support filtering tasks by multiple criteria: status (complete/incomplete), priority, tags (multiple), due date ranges
- **FR-009**: System MUST support sorting tasks by: created date, updated date, due date, priority, title (ascending/descending)
- **FR-010**: Users MUST be able to view recurring tasks with human-readable recurrence descriptions (e.g., "Repeats daily", "Repeats every Monday")

**Event-Driven Architecture**:

- **FR-011**: System MUST publish a "task.created" event to Kafka when a task is created
- **FR-012**: System MUST publish a "task.updated" event to Kafka when a task is modified
- **FR-013**: System MUST publish a "task.completed" event to Kafka when a task is marked complete
- **FR-014**: System MUST publish a "task.deleted" event to Kafka when a task is deleted
- **FR-015**: All events MUST include: event_id (UUID), event_type, timestamp (ISO 8601), user_id, and payload with task details
- **FR-016**: Events MUST be published to Kafka topics: tasks.created, tasks.updated, tasks.completed, tasks.deleted
- **FR-017**: System MUST use Dapr Pub/Sub component for Kafka abstraction
- **FR-018**: Event schemas MUST be versioned and immutable

**Reminder Service**:

- **FR-019**: Reminder service MUST consume "task.created" and "task.updated" events to schedule reminders
- **FR-020**: Reminder service MUST calculate reminder time as: due_date - reminder_offset (in minutes)
- **FR-021**: Reminder service MUST store scheduled reminders in the database with: task_id, user_id, scheduled_at, sent (boolean)
- **FR-022**: Reminder service MUST be triggered every minute via Dapr Cron Binding
- **FR-023**: Reminder service MUST query for reminders with scheduled_at <= current_time AND sent = false
- **FR-024**: Reminder service MUST publish "reminder.due" events to Kafka for due reminders
- **FR-025**: Reminder service MUST mark reminders as sent=true after publishing reminder.due event
- **FR-026**: Reminder service MUST consume "task.deleted" events to delete associated reminders
- **FR-027**: Reminder service MUST consume "task.completed" events to mark reminders as sent (skip reminders for completed tasks)
- **FR-028**: Reminder service MUST be idempotent (handle duplicate events without sending duplicate reminders)

**Dapr Integration**:

- **FR-029**: System MUST deploy Dapr sidecars alongside all services (backend, frontend, reminder-service)
- **FR-030**: System MUST use Dapr Pub/Sub API for publishing events (not direct Kafka client)
- **FR-031**: System MUST use Dapr subscriptions for consuming events (not direct Kafka consumer)
- **FR-032**: System MUST use Dapr State Store API for caching (optional, backend can use Dapr State for cache)
- **FR-033**: System MUST use Dapr Cron Binding for periodic reminder processing
- **FR-034**: System MUST use Dapr Secrets API for retrieving sensitive configuration (API keys, database passwords)
- **FR-035**: System MUST use Dapr Service Invocation for service-to-service communication (optional enhancement)
- **FR-036**: Dapr components MUST be configured via Kubernetes manifests (Component resources)

**Multi-Environment Deployment**:

- **FR-037**: System MUST support deployment to Minikube for local development and testing
- **FR-038**: System MUST support deployment to Azure AKS, Google Cloud GKE, or Oracle Cloud for production
- **FR-039**: Helm chart MUST support environment-specific configuration via values files (values-minikube.yaml, values-production.yaml)
- **FR-040**: Minikube deployment MUST use local Kafka/Redpanda and Redis
- **FR-041**: Cloud deployment MUST use managed PostgreSQL (Azure Database, Cloud SQL, Oracle Autonomous DB)
- **FR-042**: Cloud deployment MUST use Confluent Cloud or Redpanda Cloud for Kafka (or alternative Dapr-supported pub/sub)
- **FR-043**: Cloud deployment MUST use managed Redis or cloud-equivalent for Dapr State Store
- **FR-044**: Cloud deployment MUST expose frontend via cloud load balancer with HTTPS/TLS

**CI/CD Pipeline**:

- **FR-045**: System MUST provide GitHub Actions workflow for Continuous Integration (CI)
- **FR-046**: CI workflow MUST run all tests (backend unit, integration, frontend tests) on every push
- **FR-047**: CI workflow MUST build Docker images for backend, frontend, reminder-service with commit SHA tags
- **FR-048**: CI workflow MUST push built images to container registry (Docker Hub, GitHub Container Registry, or cloud registry)
- **FR-049**: CI workflow MUST run security scans on container images (Snyk, Trivy, or similar)
- **FR-050**: CI workflow MUST validate Helm charts with "helm lint"
- **FR-051**: System MUST provide GitHub Actions workflow for Continuous Deployment (CD)
- **FR-052**: CD workflow MUST deploy to cloud Kubernetes cluster on merge to main branch
- **FR-053**: CD workflow MUST use Helm upgrade with new image tags
- **FR-054**: CD workflow MUST run smoke tests against deployed application
- **FR-055**: CD workflow MUST rollback deployment if health checks or smoke tests fail
- **FR-056**: Secrets (API keys, credentials) MUST be stored in GitHub Secrets and injected at deploy time

**Monitoring and Observability**:

- **FR-057**: System MUST deploy Prometheus for metrics collection
- **FR-058**: System MUST deploy Grafana for metrics visualization with dashboards
- **FR-059**: System MUST collect application metrics: request count, latency (p50, p95, p99), error rate
- **FR-060**: System MUST collect infrastructure metrics: CPU, memory, disk, network usage
- **FR-061**: System MUST collect business metrics: tasks created, completed, reminders sent
- **FR-062**: System MUST collect Kafka metrics: consumer lag, throughput, partition health
- **FR-063**: System MUST collect Dapr metrics: sidecar health, component status
- **FR-064**: System MUST deploy Zipkin or Jaeger for distributed tracing
- **FR-065**: System MUST propagate trace context across HTTP requests, Kafka events, and Dapr calls
- **FR-066**: System MUST aggregate logs from all services (backend, frontend, reminder-service) using Loki, ELK, or cloud logging
- **FR-067**: System MUST use structured logging (JSON format) with log levels: DEBUG, INFO, WARN, ERROR, CRITICAL
- **FR-068**: System MUST configure Prometheus Alertmanager with alerts for: error rate >1%, p95 latency >500ms, Kafka consumer lag >1000, pod restarts
- **FR-069**: All logs MUST include correlation IDs (trace IDs) for request tracking

### Key Entities

- **Task** (extended from Step 2-4): Represents a todo item with advanced features
  - Attributes: id, user_id, title, description, completed, priority (low/medium/high/urgent), due_date (timestamp), recurrence_rule (RRULE string), reminder_offset (integer minutes), next_occurrence (timestamp for recurring tasks), created_at, updated_at
  - Relationships: Has many TaskTags, has many Reminders

- **TaskTag**: Represents a tag associated with a task
  - Attributes: task_id (foreign key), tag (string)
  - Relationships: Belongs to Task

- **Reminder**: Represents a scheduled reminder for a task
  - Attributes: id, task_id (foreign key), user_id, scheduled_at (timestamp), sent (boolean), created_at
  - Relationships: Belongs to Task

- **Event**: Represents an event published to Kafka (not stored in database, schema-only)
  - Attributes: event_id (UUID), event_type (task.created/updated/completed/deleted), timestamp (ISO 8601), user_id, payload (task details)

- **Dapr Component**: Represents a Dapr building block configuration
  - Types: Pub/Sub (Kafka), State Store (Redis), Bindings (Cron), Secrets (Kubernetes Secrets)
  - Attributes: Component name, type, version, metadata (configuration key-value pairs)

## Success Criteria

### Measurable Outcomes

**Advanced Features**:

- **SC-001**: Users can create recurring tasks with daily, weekly, or monthly patterns and see new instances generated automatically within 60 seconds of the next occurrence time
- **SC-002**: Users can set due dates and reminders on tasks, and reminder events are published within 60 seconds of the scheduled reminder time (>99% accuracy)
- **SC-003**: Users can filter their task list by priority and tags, and results are returned in under 200ms for lists containing up to 1000 tasks
- **SC-004**: Users can search across tasks using keywords, and search results are returned in under 500ms for databases containing up to 100,000 tasks

**Event-Driven Architecture**:

- **SC-005**: All task state changes (create, update, complete, delete) publish events to Kafka within 50ms of the database transaction completing
- **SC-006**: Reminder service processes task events and schedules reminders with <1 second latency from event publish to reminder record creation
- **SC-007**: Kafka consumer lag remains below 100 messages under normal load (<1000 tasks created per minute)

**Deployment and Operations**:

- **SC-008**: Full application stack (backend, frontend, reminder-service, Dapr, Kafka, Redis) deploys successfully to Minikube in under 5 minutes via Helm chart
- **SC-009**: Full application stack deploys successfully to cloud Kubernetes (AKS/GKE/OKE) via CI/CD pipeline in under 10 minutes from merge to main
- **SC-010**: Application achieves 99.9% uptime SLO (monthly) in production cloud deployment
- **SC-011**: Application handles 10,000 concurrent users without degradation in response time or error rate
- **SC-012**: CI/CD pipeline completes successfully (test, build, deploy) in under 15 minutes for typical code changes

**Observability**:

- **SC-013**: Monitoring dashboards display real-time metrics (request rate, latency, error rate) with <10 second delay from event occurrence
- **SC-014**: Distributed traces capture >95% of requests flowing through multiple services (frontend → backend → reminder-service)
- **SC-015**: Alerts trigger within 5 minutes of SLO violations (error rate >1%, latency >500ms)
- **SC-016**: Logs from all services are searchable and filterable in log aggregation service with <30 second indexing delay

**Developer Experience**:

- **SC-017**: Developers can deploy the full application stack to Minikube locally in under 10 minutes following documentation
- **SC-018**: Developers receive clear feedback from CI pipeline within 5 minutes of pushing code (test results, build status)
- **SC-019**: Failed deployments are automatically rolled back within 2 minutes of health check failure

**Business Impact**:

- **SC-020**: Recurring tasks feature reduces repetitive task creation by 70% for users with weekly/daily recurring work
- **SC-021**: Reminder feature reduces missed task deadlines by 60% for users with time-sensitive tasks
- **SC-022**: Priority and tag features improve task completion rate by 40% for users managing 50+ tasks
- **SC-023**: Search and filter features reduce time to find specific tasks by 80% for users with 100+ tasks

## Assumptions

1. **Cloud Platform Selection**: We assume the user will select one cloud platform (Azure AKS, GCP GKE, or Oracle Cloud) for production deployment. The Helm chart supports all three via environment-specific values files.

2. **Kafka Access**: We assume Confluent Cloud or Redpanda Cloud Kafka access will be available. If unavailable, the user can substitute with an alternative Dapr-supported pub/sub component (Redis Streams, Azure Service Bus, Google Pub/Sub) with identical event contracts.

3. **RRULE Format**: We assume recurring task recurrence rules follow the iCalendar RFC 5545 RRULE format. The system will validate RRULE syntax and reject invalid patterns with clear error messages.

4. **Reminder Delivery**: We assume reminder events published to the "reminders.due" Kafka topic will be consumed by a future notification service (email, SMS, push notifications). Step 5 implements reminder event publishing but not notification delivery.

5. **Database Migration**: We assume the existing Neon Serverless PostgreSQL database from Steps 2-4 will be migrated to cloud-managed PostgreSQL for production, or a new cloud database will be provisioned with data migration handled separately.

6. **Monitoring Stack**: We assume Prometheus, Grafana, and Zipkin/Jaeger will be deployed to the same Kubernetes cluster as the application. Cloud-native alternatives (Azure Monitor, Google Cloud Operations, Oracle Cloud Monitoring) are also supported.

7. **CI/CD Credentials**: We assume GitHub Actions will have necessary credentials (cloud provider service accounts, container registry access, Kubernetes cluster access) configured in GitHub Secrets by the user.

8. **Resource Limits**: We assume cloud Kubernetes clusters will have sufficient resources (CPU, memory, storage) to run all services with defined resource requests/limits. Minikube requires minimum 2 CPUs and 4GB RAM.

9. **Security**: We assume HTTPS/TLS certificates for the frontend load balancer will be provisioned via cloud provider (Let's Encrypt, cloud certificate manager) or provided by the user.

10. **Data Retention**: We assume reminder records will be retained for 90 days after being sent (configurable cleanup job). Task events in Kafka will follow Kafka retention policies (default 7 days, configurable).

11. **Idempotency**: We assume the reminder service will handle Kafka at-least-once delivery by checking the reminder.sent flag before publishing reminder.due events, preventing duplicate reminders.

12. **Time Zones**: We assume all timestamps (due dates, reminder times, event timestamps) use UTC for consistency. Frontend will handle timezone conversion for display purposes.
