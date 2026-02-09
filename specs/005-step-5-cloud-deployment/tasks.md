# Tasks: Step 5 - Advanced Cloud Deployment

**Input**: Design documents from `/specs/005-step-5-cloud-deployment/`
**Prerequisites**: spec.md (11 user stories), plan.md (11 phases, 7 technology decisions)

**Tests**: No TDD tests requested - implementation verification via manual testing and acceptance scenarios

**Organization**: Tasks are grouped by user story (US1-US11) to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Web application structure** (backend/ + frontend/ + reminder-service/):
- Backend API: `backend/api/src/`
- Reminder Service: `backend/reminder-service/src/`
- Frontend: `frontend/src/`
- Helm charts: `helm/todo-app/`
- CI/CD: `.github/workflows/`
- Documentation: `specs/005-step-5-cloud-deployment/design/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Step 5

- [x] T001 Create reminder-service directory structure at backend/reminder-service/
- [x] T002 Initialize reminder-service Python project with pyproject.toml (FastAPI, dapr, sqlmodel, python-dateutil)
- [x] T003 [P] Create event schema documentation in specs/005-step-5-cloud-deployment/design/event-schemas.md
- [x] T004 [P] Create Dapr component specifications in specs/005-step-5-cloud-deployment/design/dapr-components.md
- [x] T005 [P] Document technology decisions in specs/005-step-5-cloud-deployment/design/research.md (RRULE parsing, Kafka broker, search strategy)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema Extensions

- [x] T006 Create Alembic migration for Task model extensions in backend/api/alembic/versions/003_add_advanced_task_fields.py (priority, due_date, recurrence_rule, reminder_offset, next_occurrence)
- [x] T007 [P] Create TaskTag model in backend/api/src/models/task_tag.py (id, task_id, tag_name, created_at)
- [x] T008 [P] Create Reminder model in backend/api/src/models/reminder.py (id, task_id, user_id, reminder_at, sent, created_at)
- [x] T009 Create database indexes migration in backend/api/alembic/versions/004_add_search_and_reminder_indexes.py (GIN index for full-text search, composite index for reminders)

### Event Infrastructure

- [x] T010 Create Event model/schema in backend/api/src/models/event.py (event_id, event_type, timestamp, user_id, payload)
- [x] T011 Implement EventPublisher service in backend/api/src/services/event_publisher.py (publish via Dapr Pub/Sub API)
- [x] T012 [P] Create Dapr Pub/Sub component YAML in helm/todo-app/templates/dapr-pubsub.yaml (Kafka configuration)
- [x] T013 [P] Create Dapr State Store component YAML in helm/todo-app/templates/dapr-statestore.yaml (Redis configuration)
- [x] T014 [P] Create Dapr Secrets component YAML in helm/todo-app/templates/dapr-secrets.yaml (Kubernetes Secrets)

### Reminder Service Foundation

- [x] T015 Create reminder-service main.py in backend/reminder-service/src/main.py (FastAPI app with health endpoint)
- [x] T016 Create reminder-service Dockerfile in backend/reminder-service/Dockerfile (multi-stage build, non-root user)
- [x] T017 [P] Create reminder-service Helm Deployment in helm/todo-app/templates/reminder-deployment.yaml (with Dapr sidecar annotations)
- [x] T018 [P] Create reminder-service Helm Service in helm/todo-app/templates/reminder-service.yaml (ClusterIP)
- [x] T019 Create Dapr Cron Binding component YAML in helm/todo-app/templates/dapr-cron-binding.yaml (every 1 minute schedule)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Recurring Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks that repeat automatically on a schedule (daily, weekly, monthly)

**Independent Test**: Create a recurring task with daily recurrence rule, wait for next occurrence time, verify new task instance generated automatically

### Implementation for User Story 1

- [x] T020 [P] [US1] Install python-dateutil dependency in backend/api/pyproject.toml
- [x] T021 [P] [US1] Create PriorityLevel enum in backend/api/src/models/task.py (low, medium, high, urgent)
- [x] T022 [US1] Update Task model to include advanced fields in backend/api/src/models/task.py (priority, due_date, recurrence_rule, reminder_offset, next_occurrence)
- [x] T023 [US1] Create RecurrenceService in backend/api/src/services/recurrence_service.py (parse RRULE, calculate next_occurrence using python-dateutil)
- [x] T024 [US1] Add RRULE validation to task creation in backend/api/src/api/tasks.py (validate format before saving)
- [x] T025 [US1] Update POST /tasks endpoint to accept recurrence_rule in backend/api/src/api/tasks.py
- [x] T026 [US1] Update PUT /tasks/{id} endpoint to accept recurrence_rule in backend/api/src/api/tasks.py
- [x] T027 [US1] Implement recurring task generator background job in backend/api/src/services/recurrence_processor.py (query tasks with next_occurrence <= now, create new instances)
- [x] T028 [US1] Add recurrence pattern display formatting in frontend/src/components/tasks/RecurrenceDisplay.tsx (RRULE to human-readable)
- [x] T029 [US1] Add recurrence rule input UI in frontend/src/components/tasks/RecurrenceInput.tsx (daily, weekly, monthly presets + custom RRULE)
- [x] T030 [US1] Update TaskForm component to include recurrence input in frontend/src/components/tasks/TaskForm.tsx
- [x] T031 [US1] Update task list display to show recurrence pattern in frontend/src/app/tasks/page.tsx

**Checkpoint**: User Story 1 (Recurring Tasks) should be fully functional and testable independently

---

## Phase 4: User Story 2 - Due Dates and Reminders (Priority: P1)

**Goal**: Users can set deadlines and receive reminders before the deadline

**Independent Test**: Create a task with due date 5 minutes in future and 2-minute reminder offset, verify reminder event published 3 minutes in future

### Implementation for User Story 2

- [x] T032 [P] [US2] Update POST /tasks endpoint to accept due_date and reminder_offset in backend/api/src/api/tasks.py
- [x] T033 [P] [US2] Update PUT /tasks/{id} endpoint to accept due_date and reminder_offset in backend/api/src/api/tasks.py
- [x] T034 [US2] Implement reminder creation logic in backend/api/src/services/task_service.py (calculate reminder_at = due_date - reminder_offset, create Reminder record)
- [x] T035 [US2] Update task creation to publish task.created event in backend/api/src/api/tasks.py (via EventPublisher)
- [x] T036 [US2] Update task update to publish task.updated event in backend/api/src/api/tasks.py (via EventPublisher)
- [x] T037 [US2] Update task completion to publish task.completed event in backend/api/src/api/tasks.py (via EventPublisher)
- [x] T038 [US2] Update task deletion to publish task.deleted event in backend/api/src/api/tasks.py (via EventPublisher)
- [x] T039 [US2] Add due date picker UI component in frontend/src/components/tasks/DueDatePicker.tsx (date + time selection)
- [x] T040 [US2] Add reminder offset input UI component in frontend/src/components/tasks/ReminderOffsetInput.tsx (minutes before due date)
- [x] T041 [US2] Update TaskForm to include due date and reminder inputs in frontend/src/components/tasks/TaskForm.tsx
- [x] T042 [US2] Update task list display to show due dates in frontend/src/app/tasks/page.tsx

**Checkpoint**: User Story 2 (Due Dates and Reminders) should be fully functional and testable independently

---

## Phase 5: User Story 3 - Task Priorities and Tags (Priority: P2)

**Goal**: Users can categorize tasks by priority level and apply multiple tags

**Independent Test**: Create tasks with different priorities and tags, filter and sort by priority and tag combinations to verify correct results

### Implementation for User Story 3

- [x] T043 [P] [US3] Create TaskTag table migration in backend/api/alembic/versions/005_create_task_tags_table.py (✅ Already done in Phase 2 - T007)
- [x] T044 [P] [US3] Create TagService in backend/api/src/services/tag_service.py (add_tag, remove_tag, get_tags_for_task, validate max 10 tags)
- [x] T045 [US3] Update POST /tasks endpoint to accept priority in backend/api/src/api/tasks.py (default: medium) (✅ Already done in Phase 3)
- [x] T046 [US3] Update PUT /tasks/{id} endpoint to accept priority in backend/api/src/api/tasks.py (✅ Already done in Phase 3)
- [x] T047 [US3] Create POST /tasks/{id}/tags endpoint in backend/api/src/api/tasks.py (add tag to task, validate max 10)
- [x] T048 [US3] Create DELETE /tasks/{id}/tags/{tag_name} endpoint in backend/api/src/api/tasks.py (remove tag from task)
- [x] T049 [US3] Create GET /tasks/{id}/tags endpoint in backend/api/src/api/tasks.py (get all tags for task)
- [x] T050 [US3] Add priority selector UI component in frontend/src/components/tasks/PrioritySelector.tsx (low, medium, high, urgent with color coding)
- [x] T051 [US3] Add tag input UI component in frontend/src/components/tasks/TagInput.tsx (autocomplete, max 10 tags)
- [x] T052 [US3] Update TaskForm to include priority and tag inputs in frontend/src/components/tasks/TaskForm.tsx
- [x] T053 [US3] Update task list display to show priority badges and tags in frontend/src/app/tasks/page.tsx (✅ Priority already done in Phase 3)

**Checkpoint**: User Story 3 (Priorities and Tags) should be fully functional and testable independently

---

## Phase 6: User Story 4 - Search, Filter, and Sort (Priority: P2)

**Goal**: Users can search tasks, filter by multiple criteria, and sort results

**Independent Test**: Create 50 tasks with varied titles, descriptions, priorities, tags, and due dates, perform search queries and multi-criteria filters to verify correct results

### Implementation for User Story 4

- [x] T054 [P] [US4] Create SearchService in backend/api/src/services/search_service.py (PostgreSQL tsvector full-text search)
- [x] T055 [P] [US4] Create FilterService in backend/api/src/services/filter_service.py (build dynamic queries for status, priority, tags, due date ranges)
- [x] T056 [US4] Update GET /tasks endpoint to accept search query parameter in backend/api/src/api/tasks.py (full-text search on title and description)
- [x] T057 [US4] Update GET /tasks endpoint to accept filter parameters in backend/api/src/api/tasks.py (status, priority, tags, due_date_start, due_date_end)
- [x] T058 [US4] Update GET /tasks endpoint to accept sort parameters in backend/api/src/api/tasks.py (created_at, updated_at, due_date, priority, title with asc/desc)
- [x] T059 [US4] Add search bar UI component in frontend/src/components/tasks/SearchBar.tsx (debounced search input)
- [x] T060 [US4] Add filter panel UI component in frontend/src/components/tasks/FilterPanel.tsx (status, priority, tags, due date range)
- [x] T061 [US4] Add sort controls UI component in frontend/src/components/tasks/SortControls.tsx (dropdown with sort options)
- [x] T062 [US4] Update task list page to integrate search, filter, sort in frontend/src/app/tasks/page.tsx
- [x] T063 [US4] Add search result highlighting in frontend/src/components/tasks/TaskItem.tsx (highlight matching text)

**Checkpoint**: User Story 4 (Search, Filter, Sort) should be fully functional and testable independently

---

## Phase 7: User Story 5 - Event-Driven Task Management (Priority: P3)

**Goal**: System publishes events for all task state changes to enable asynchronous processing

**Independent Test**: Perform task operations (create, update, complete, delete), verify corresponding events published to Kafka topics with correct schemas

### Implementation for User Story 5

- [x] T064 [P] [US5] Create event schema definitions in specs/005-step-5-cloud-deployment/design/event-schemas.md (task.created, task.updated, task.completed, task.deleted, reminders.due)
- [x] T065 [US5] Verify EventPublisher integration in task endpoints in backend/api/src/api/tasks.py (already done in T035-T038, verify completeness)
- [x] T066 [US5] Add event idempotency (deduplicate events) in backend/api/src/services/event_publisher.py (use event_id for idempotency)
- [x] T067 [US5] Add event delivery guarantees (retry logic) in backend/api/src/services/event_publisher.py (Dapr handles retries, but add local queueing)
- [x] T068 [US5] Create event consumer test utility in backend/api/tests/test_event_publisher.py (subscribe to topics, verify event delivery)
- [x] T069 [US5] Document event-driven architecture in specs/005-step-5-cloud-deployment/design/event-architecture.md (event flow diagrams, topic structure)

**Checkpoint**: User Story 5 (Event-Driven Architecture) should be fully functional and testable independently

---

## Phase 8: User Story 6 - Reminder Service (Priority: P3)

**Goal**: Dedicated service consumes task events, schedules reminders, and publishes reminder events when due

**Independent Test**: Publish task.created event with due date 10 minutes in future and 5-minute reminder offset, verify reminder service calculates correct reminder time and publishes reminder.due event at scheduled time

### Implementation for User Story 6

- [x] T070 [P] [US6] Create event consumer for task.created in backend/reminder-service/src/consumers/task_created_consumer.py (subscribe via Dapr, create Reminder record)
- [x] T071 [P] [US6] Create event consumer for task.updated in backend/reminder-service/src/consumers/task_updated_consumer.py (update Reminder record if due_date changed)
- [x] T072 [P] [US6] Create event consumer for task.deleted in backend/reminder-service/src/consumers/task_deleted_consumer.py (delete associated Reminder records)
- [x] T073 [P] [US6] Create event consumer for task.completed in backend/reminder-service/src/consumers/task_completed_consumer.py (mark Reminder as sent=true to prevent duplicate)
- [x] T074 [US6] Implement ReminderProcessor in backend/reminder-service/src/services/reminder_processor.py (query reminders with reminder_at <= now and sent=false, publish reminder.due events)
- [x] T075 [US6] Create Dapr Cron Binding endpoint in backend/reminder-service/src/main.py (POST /cron endpoint triggered every 1 minute, calls ReminderProcessor)
- [x] T076 [US6] Add Dapr subscription configuration in backend/reminder-service/src/main.py (subscribe to task.created, task.updated, task.completed, task.deleted topics)
- [x] T077 [US6] Implement idempotency checks in ReminderProcessor in backend/reminder-service/src/services/reminder_processor.py (prevent duplicate reminder sends)
- [x] T078 [US6] Add logging and error handling in reminder-service in backend/reminder-service/src/main.py (structured logging for event consumption)
- [x] T079 [US6] Configure Dapr sidecar annotations for reminder-service in helm/todo-app/templates/reminder-deployment.yaml (app-id, port, subscriptions)

**Checkpoint**: User Story 6 (Reminder Service) should be fully functional and testable independently

---

## Phase 9: User Story 7 - Dapr Integration (Priority: P4)

**Goal**: Integrate Dapr distributed runtime to abstract infrastructure complexity

**Independent Test**: Deploy backend service with Dapr sidecar, publish event via Dapr Pub/Sub API to test topic, subscribe via Dapr subscription, verify event delivered without direct Kafka client usage

### Implementation for User Story 7

- [x] T080 [P] [US7] Install Dapr Python SDK in backend/api/pyproject.toml and backend/reminder-service/pyproject.toml
- [x] T081 [P] [US7] Configure Dapr annotations for backend in helm/todo-app/templates/backend-deployment.yaml (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port)
- [x] T082 [US7] Update EventPublisher to use Dapr Pub/Sub API in backend/api/src/services/event_publisher.py (replace direct Kafka client with Dapr SDK)
- [x] T083 [US7] Update reminder-service event consumers to use Dapr subscriptions in backend/reminder-service/src/main.py (Dapr subscription endpoints)
- [x] T084 [US7] Create Dapr Service Invocation helper in backend/api/src/services/dapr_client.py (invoke reminder-service via Dapr)
- [x] T085 [US7] Create Dapr Secrets integration in backend/api/src/config.py (fetch secrets via Dapr Secrets API instead of environment variables)
- [x] T086 [US7] Update Helm values to configure Dapr component metadata in helm/todo-app/values-dev.yaml (Kafka brokers, Redis connection, secret store)
- [x] T087 [US7] Document Dapr component usage in specs/005-step-5-cloud-deployment/design/dapr-components.md (Pub/Sub, State Store, Cron Binding, Secrets, Service Invocation)

**Checkpoint**: User Story 7 (Dapr Integration) should be fully functional and testable independently

---

## Phase 10: User Story 8 - Local Deployment on Minikube (Priority: P4)

**Goal**: Deploy complete Step 5 stack on local Minikube cluster for development and testing

**Independent Test**: Deploy Helm chart to Minikube with values-dev.yaml, verify all pods running (backend, frontend, reminder-service with Dapr sidecars), execute end-to-end tests covering all advanced features

### Implementation for User Story 8

- [ ] T088 [P] [US8] Create Minikube setup script in scripts/setup-minikube.sh (start Minikube with 2+ CPUs and 3GB+ RAM)
- [ ] T089 [P] [US8] Create Dapr installation script in scripts/install-dapr-minikube.sh (dapr init -k, verify Dapr system pods)
- [ ] T090 [US8] Create Kafka/Redpanda deployment YAML in helm/todo-app/dependencies/redpanda.yaml (Redpanda for local development)
- [ ] T091 [US8] Create Redis deployment YAML in helm/todo-app/dependencies/redis.yaml (Redis for Dapr State Store)
- [ ] T092 [US8] Update Helm values-dev.yaml for Minikube in helm/todo-app/values-dev.yaml (local Kafka, local Redis, NodePort services)
- [ ] T093 [US8] Create build-local-images script in scripts/build-local-images.sh (build backend, frontend, reminder-service images for Minikube Docker)
- [ ] T094 [US8] Update Helm chart to include Dapr component resources in helm/todo-app/templates/ (apply pubsub, statestore, cron, secrets components)
- [ ] T095 [US8] Create deploy-to-minikube script in scripts/deploy-to-minikube.sh (helm install/upgrade todo-app with values-dev.yaml)
- [ ] T096 [US8] Document Minikube deployment in specs/005-step-5-cloud-deployment/design/quickstart.md (step-by-step local deployment guide)
- [ ] T097 [US8] Create end-to-end test script in scripts/e2e-test-minikube.sh (create recurring task, verify new instance generated, verify reminder event published)

**Checkpoint**: User Story 8 (Local Minikube Deployment) should be fully functional and testable independently

---

## Phase 11: User Story 9 - Cloud Deployment (Priority: P5)

**Goal**: Deploy to production-grade Kubernetes on Azure AKS, Google Cloud GKE, or Oracle Cloud with managed services

**Independent Test**: Deploy to cloud Kubernetes cluster via CI/CD pipeline, verify all pods running in production namespace, access application via cloud load balancer, execute end-to-end tests, monitor metrics/logs/traces

### Implementation for User Story 9

- [ ] T098 [P] [US9] Create cloud infrastructure provisioning guide in specs/005-step-5-cloud-deployment/design/cloud-provisioning.md (AKS, GKE, OKE cluster setup)
- [ ] T099 [P] [US9] Document managed PostgreSQL setup in specs/005-step-5-cloud-deployment/design/cloud-provisioning.md (Azure Database, Cloud SQL, Oracle Autonomous Database)
- [ ] T100 [P] [US9] Document managed Kafka setup in specs/005-step-5-cloud-deployment/design/cloud-provisioning.md (Confluent Cloud, Redpanda Cloud)
- [ ] T101 [P] [US9] Document managed Redis setup in specs/005-step-5-cloud-deployment/design/cloud-provisioning.md (Azure Cache, Cloud Memorystore, Oracle OCI Cache)
- [ ] T102 [US9] Create Helm values-prod-aks.yaml for Azure AKS in helm/todo-app/values-prod-aks.yaml (managed services, LoadBalancer, TLS)
- [ ] T103 [US9] Create Helm values-prod-gke.yaml for Google Cloud GKE in helm/todo-app/values-prod-gke.yaml (managed services, LoadBalancer, TLS)
- [ ] T104 [US9] Create Helm values-prod-oke.yaml for Oracle Cloud in helm/todo-app/values-prod-oke.yaml (managed services, LoadBalancer, TLS)
- [ ] T105 [US9] Update Dapr Pub/Sub component for cloud Kafka in helm/todo-app/templates/dapr-pubsub.yaml (Confluent Cloud broker URLs, SASL auth)
- [ ] T106 [US9] Update Dapr State Store component for cloud Redis in helm/todo-app/templates/dapr-statestore.yaml (managed Redis connection strings)
- [ ] T107 [US9] Create cloud deployment script in scripts/deploy-to-cloud.sh (helm install/upgrade to cloud cluster with environment-specific values)
- [ ] T108 [US9] Configure cloud load balancer and TLS certificates in helm/todo-app/templates/frontend-ingress.yaml (Ingress with TLS termination)
- [ ] T109 [US9] Document cloud deployment in specs/005-step-5-cloud-deployment/design/cloud-deployment.md (step-by-step cloud deployment guide)

**Checkpoint**: User Story 9 (Cloud Deployment) should be fully functional and testable independently

---

## Phase 12: User Story 10 - CI/CD Automation (Priority: P5)

**Goal**: Automated CI/CD pipeline using GitHub Actions for tests, builds, and deployments

**Independent Test**: Create pull request with code change, merge to main, verify GitHub Actions workflow runs successfully through all stages (test, build, push, deploy), confirm updated application running in production

### Implementation for User Story 10

- [ ] T110 [P] [US10] Create CI workflow in .github/workflows/ci.yml (run tests on PR, lint, type check)
- [ ] T111 [P] [US10] Add backend tests to CI workflow in .github/workflows/ci.yml (pytest for backend/api and backend/reminder-service)
- [ ] T112 [P] [US10] Add frontend tests to CI workflow in .github/workflows/ci.yml (npm test for frontend)
- [ ] T113 [US10] Add Docker image build to CI workflow in .github/workflows/ci.yml (build backend, frontend, reminder-service images)
- [ ] T114 [US10] Add security scanning to CI workflow in .github/workflows/ci.yml (Trivy or Snyk for vulnerability scanning)
- [ ] T115 [US10] Add container registry push to CI workflow in .github/workflows/ci.yml (push to Docker Hub, GCR, or ACR with commit SHA tags)
- [ ] T116 [US10] Add Helm chart validation to CI workflow in .github/workflows/ci.yml (helm lint, helm template validation)
- [ ] T117 [US10] Create CD workflow in .github/workflows/cd.yml (deploy on merge to main)
- [ ] T118 [US10] Add Helm deployment to CD workflow in .github/workflows/cd.yml (helm upgrade --install with new image tags)
- [ ] T119 [US10] Add smoke tests to CD workflow in .github/workflows/cd.yml (health check endpoints, critical user flows)
- [ ] T120 [US10] Add rollback mechanism to CD workflow in .github/workflows/cd.yml (helm rollback on health check failure)
- [ ] T121 [US10] Configure GitHub Secrets in repository settings (cloud credentials, API keys, database URLs, container registry tokens)
- [ ] T122 [US10] Document CI/CD pipeline in specs/005-step-5-cloud-deployment/design/cicd-pipeline.md (workflow structure, secret management, deployment strategy)

**Checkpoint**: User Story 10 (CI/CD Automation) should be fully functional and testable independently

---

## Phase 13: User Story 11 - Monitoring and Observability (Priority: P5)

**Goal**: Comprehensive monitoring, logging, and distributed tracing infrastructure for production operations

**Independent Test**: Deploy monitoring stack (Prometheus, Grafana, Zipkin), generate application traffic, verify metrics collected, dashboards display data, traces captured, logs aggregated, alerts trigger when thresholds exceeded

### Implementation for User Story 11

- [ ] T123 [P] [US11] Create Prometheus deployment in helm/todo-app/dependencies/prometheus.yaml (Prometheus server, scrape configs for backend, frontend, reminder-service)
- [ ] T124 [P] [US11] Create Grafana deployment in helm/todo-app/dependencies/grafana.yaml (Grafana server, datasource configuration for Prometheus)
- [ ] T125 [P] [US11] Create Zipkin deployment in helm/todo-app/dependencies/zipkin.yaml (Zipkin server for distributed tracing)
- [ ] T126 [US11] Add Prometheus metrics endpoints to backend in backend/api/src/main.py (request count, latency, error rate using prometheus_client)
- [ ] T127 [US11] Add Prometheus metrics endpoints to reminder-service in backend/reminder-service/src/main.py (event consumption rate, reminder processing lag)
- [ ] T128 [US11] Configure distributed tracing in backend in backend/api/src/main.py (OpenTelemetry integration, Zipkin exporter)
- [ ] T129 [US11] Configure distributed tracing in reminder-service in backend/reminder-service/src/main.py (OpenTelemetry integration, Zipkin exporter)
- [ ] T130 [US11] Create Grafana dashboard JSON for application metrics in helm/todo-app/dashboards/application-dashboard.json (request rate, latency, error rate, task operations)
- [ ] T131 [US11] Create Grafana dashboard JSON for Kubernetes cluster in helm/todo-app/dashboards/cluster-dashboard.json (pod health, resource usage, Dapr component status)
- [ ] T132 [US11] Create Prometheus Alertmanager configuration in helm/todo-app/dependencies/alertmanager.yaml (notification channels, alert routing)
- [ ] T133 [US11] Create Prometheus alert rules in helm/todo-app/dependencies/prometheus-rules.yaml (error rate > 1%, latency > 500ms, consumer lag > 1000, pod restarts)
- [ ] T134 [US11] Configure log aggregation in helm/todo-app/dependencies/loki.yaml (Loki for log aggregation, Promtail for log collection)
- [ ] T135 [US11] Add structured logging to backend in backend/api/src/main.py (JSON logs with trace_id, user_id, request_id)
- [ ] T136 [US11] Add structured logging to reminder-service in backend/reminder-service/src/main.py (JSON logs with trace_id, event_id)
- [ ] T137 [US11] Document monitoring and observability in specs/005-step-5-cloud-deployment/design/monitoring.md (metrics, dashboards, alerts, tracing, logging)

**Checkpoint**: User Story 11 (Monitoring and Observability) should be fully functional and testable independently

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize Step 5 implementation

- [ ] T138 [P] Update README.md with Step 5 features and deployment instructions in README.md
- [ ] T139 [P] Create architecture diagrams in specs/005-step-5-cloud-deployment/design/architecture-diagrams.md (event flow, Dapr components, deployment architecture)
- [ ] T140 [P] Create troubleshooting guide in specs/005-step-5-cloud-deployment/design/troubleshooting.md (common issues, debugging steps)
- [ ] T141 Create performance optimization checklist in specs/005-step-5-cloud-deployment/checklists/performance.md (database query optimization, caching strategies)
- [ ] T142 Create security hardening checklist in specs/005-step-5-cloud-deployment/checklists/security.md (input validation, SQL injection prevention, RBAC, secret management)
- [ ] T143 Run end-to-end validation on Minikube using scripts/e2e-test-minikube.sh (all 11 user stories)
- [ ] T144 Run end-to-end validation on cloud using scripts/e2e-test-cloud.sh (all 11 user stories)
- [ ] T145 Verify all acceptance scenarios from spec.md (75+ scenarios across 11 user stories)
- [ ] T146 Verify all success criteria from spec.md (23 success criteria)
- [ ] T147 Document known limitations and future improvements in specs/005-step-5-cloud-deployment/design/future-work.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-13)**: All depend on Foundational phase completion
  - US1 (Recurring Tasks): Can start after Foundational - No dependencies on other stories
  - US2 (Due Dates & Reminders): Can start after Foundational - No dependencies on other stories
  - US3 (Priorities & Tags): Can start after Foundational - No dependencies on other stories
  - US4 (Search, Filter, Sort): Can start after Foundational - No dependencies on other stories
  - US5 (Event-Driven): Can start after Foundational - No dependencies on other stories
  - US6 (Reminder Service): Depends on US5 (Event-Driven) completion - requires events to consume
  - US7 (Dapr Integration): Can start after Foundational - Refactors existing code to use Dapr
  - US8 (Minikube Deployment): Depends on US1-US7 completion - deploys all features locally
  - US9 (Cloud Deployment): Depends on US8 completion - extends Minikube deployment to cloud
  - US10 (CI/CD): Depends on US9 completion - automates cloud deployments
  - US11 (Monitoring): Depends on US9 completion - monitors production workloads
- **Polish (Phase 14)**: Depends on all desired user stories being complete

### User Story Dependencies

- **Tier 1 (Independent - Can Start After Foundational)**:
  - US1 (Recurring Tasks): No dependencies
  - US2 (Due Dates & Reminders): No dependencies
  - US3 (Priorities & Tags): No dependencies
  - US4 (Search, Filter, Sort): No dependencies
  - US5 (Event-Driven): No dependencies

- **Tier 2 (Depends on Tier 1)**:
  - US6 (Reminder Service): Depends on US5 (Event-Driven)
  - US7 (Dapr Integration): Depends on US5 (Event-Driven)

- **Tier 3 (Depends on Tier 1 & 2)**:
  - US8 (Minikube Deployment): Depends on US1-US7 completion

- **Tier 4 (Depends on Tier 3)**:
  - US9 (Cloud Deployment): Depends on US8 (Minikube)

- **Tier 5 (Depends on Tier 4)**:
  - US10 (CI/CD): Depends on US9 (Cloud)
  - US11 (Monitoring): Depends on US9 (Cloud)

### Within Each User Story

- Database migrations before services
- Services before API endpoints
- API endpoints before frontend components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005 can run in parallel (different documentation files)
- **Foundational Phase**:
  - T007, T008 can run in parallel (different model files)
  - T012, T013, T014 can run in parallel (different Dapr component files)
  - T017, T018 can run in parallel (different Helm template files)
- **Tier 1 User Stories**: US1, US2, US3, US4, US5 can all run in parallel (independent features)
- **Within Each User Story**: Tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Recurring Tasks)

```bash
# Launch all models and services for User Story 1 together:
Task T020: "Install python-dateutil dependency"
Task T021: "Create PriorityLevel enum"
# (After T020, T021 complete)

Task T023: "Create RecurrenceService in backend/api/src/services/recurrence_service.py"
Task T028: "Add recurrence pattern display in frontend/src/components/tasks/RecurrenceDisplay.tsx"
Task T029: "Add recurrence rule input UI in frontend/src/components/tasks/RecurrenceInput.tsx"
# (Backend and frontend can work in parallel)
```

---

## Parallel Example: Tier 1 User Stories

```bash
# After Foundational Phase completes, launch all Tier 1 stories in parallel:
Team Member A: US1 (Recurring Tasks) - T020 through T031
Team Member B: US2 (Due Dates & Reminders) - T032 through T042
Team Member C: US3 (Priorities & Tags) - T043 through T053
Team Member D: US4 (Search, Filter, Sort) - T054 through T063
Team Member E: US5 (Event-Driven) - T064 through T069

# All 5 stories complete and integrate independently
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T019) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 - Recurring Tasks (T020-T031)
4. Complete Phase 4: User Story 2 - Due Dates & Reminders (T032-T042)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy to Minikube (basic deployment without US8 full deployment)

### Incremental Delivery (Recommended)

1. **Foundation**: Complete Setup + Foundational (T001-T019) → Foundation ready
2. **Tier 1 Features**: Add US1-US5 (T020-T069) → Test independently → Advanced features working locally
3. **Tier 2 Infrastructure**: Add US6-US7 (T070-T087) → Event-driven + Dapr integration complete
4. **Tier 3 Local Deployment**: Add US8 (T088-T097) → Full Minikube deployment working
5. **Tier 4 Cloud Production**: Add US9-US11 (T098-T137) → Production deployment with CI/CD and monitoring
6. **Finalization**: Complete Polish phase (T138-T147) → Step 5 complete

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T019)
2. **Once Foundational is done, Tier 1 stories run in parallel**:
   - Developer A: US1 (Recurring Tasks)
   - Developer B: US2 (Due Dates & Reminders)
   - Developer C: US3 (Priorities & Tags)
   - Developer D: US4 (Search, Filter, Sort)
   - Developer E: US5 (Event-Driven)
3. **Tier 2 stories (dependent on Tier 1)**:
   - Developer A: US6 (Reminder Service) - depends on US5
   - Developer B: US7 (Dapr Integration) - depends on US5
4. **Tier 3-5 stories (sequential deployment)**:
   - Team: US8 (Minikube Deployment) → US9 (Cloud Deployment) → US10 (CI/CD) + US11 (Monitoring) in parallel

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label (US1-US11) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tier 1 stories (US1-US5) can run completely in parallel with different team members
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Step 5 is the largest and most complex step - incremental delivery is critical for success
- Minikube deployment (US8) is a critical validation checkpoint before cloud deployment
