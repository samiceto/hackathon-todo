---
id: 0002
title: Create Step 5 Implementation Plan
stage: plan
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-step-5-cloud-deployment
branch: 005-step-5-cloud-deployment
user: claude-code
command: /sp.plan
labels: ["plan", "step-5", "cloud-deployment", "event-driven", "dapr", "kafka", "cicd", "monitoring"]
links:
  spec: specs/005-step-5-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-step-5-cloud-deployment/plan.md
  - specs/005-step-5-cloud-deployment/design/research.md
  - specs/005-step-5-cloud-deployment/design/data-model.md
  - specs/005-step-5-cloud-deployment/design/quickstart.md
  - specs/005-step-5-cloud-deployment/contracts/module-interfaces.md
tests:
  - N/A (planning phase - implementation tests will be defined in /sp.tasks)
---

## Prompt

create plan.md for step 5

## Response snapshot

Successfully generated comprehensive implementation plan for Step 5: Advanced Cloud Deployment using Plan subagent.

**Plan Structure**:
- **11 Implementation Phases**: Phase 0 (Research) through Phase 11 (Documentation)
- **7 Critical Technology Decisions**: RRULE parsing, Kafka broker, cloud platform, search strategy, reminder processing, CI/CD workflow, monitoring stack
- **Extended Data Models**: Task model enhancements, new TaskTag and Reminder models
- **Event Schemas**: 5 event types (task.created, task.updated, task.completed, task.deleted, reminders.due)
- **Microservice Architecture**: Backend API + Reminder Service + Frontend
- **Dapr Components**: 5 building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation)
- **Multi-Environment Deployment**: Minikube (local) + Cloud production (AKS/GKE/OKE)

**Key Technical Decisions**:
1. **RRULE Parsing**: python-dateutil for RFC 5545 compliance
2. **Kafka Broker**: Redpanda Cloud for Minikube, Confluent Cloud for production, Dapr abstraction for portability
3. **Cloud Platforms**: Support Azure AKS, GCP GKE, Oracle Cloud via Helm values files
4. **Search**: PostgreSQL tsvector with GIN index (not Elasticsearch to avoid complexity)
5. **Reminders**: Dapr Cron Binding (every 1 minute) with database queries
6. **CI/CD**: Separate workflows (ci.yml for testing/security, cd.yml for deployment)
7. **Monitoring**: In-cluster Prometheus + Grafana for portability

**Phase Breakdown**:
- **Phase 0**: Research and Design (technology validation, event schemas, Dapr component specs)
- **Phase 1**: Database Schema and Models (Task, TaskTag, Reminder models with migrations)
- **Phase 2**: Recurrence and Search Services (RRULE parsing, full-text search, tag filtering)
- **Phase 3**: Event Publishing Infrastructure (EventPublisher service, Dapr Pub/Sub integration)
- **Phase 4**: Reminder Service (Microservice with Dapr Cron Binding, event publishing)
- **Phase 5**: API Endpoints for Advanced Features (REST endpoints for recurring tasks, reminders, priorities, tags, search)
- **Phase 6**: Frontend UI for Advanced Features (React components for advanced features, date pickers, tag UI)
- **Phase 7**: Local Minikube Deployment (Helm chart updates, Dapr on Minikube, local testing)
- **Phase 8**: CI/CD Pipeline (GitHub Actions workflows, security scanning, automated deployment)
- **Phase 9**: Cloud Deployment (Cloud Helm values, cloud Dapr configuration, production deployment)
- **Phase 10**: Monitoring and Observability (Prometheus, Grafana, tracing, logging, alerting)
- **Phase 11**: Documentation and Polish (README updates, troubleshooting guides, architecture diagrams)

**Module Design Highlights**:
- Extended Task model with priority, due_date, recurrence_rule, reminder_offset, next_occurrence fields
- TaskTag model for many-to-many relationship with tasks
- Reminder model with task_id, reminder_at, sent fields
- RecurrenceService for RRULE parsing and next occurrence calculation
- EventPublisher service for Kafka integration via Dapr
- Reminder Service as separate microservice with health checks and graceful shutdown

**Dapr Component Specifications**:
- Pub/Sub: Kafka via Dapr (topics: tasks.created, tasks.updated, tasks.completed, tasks.deleted, reminders.due)
- State Store: Redis via Dapr (for distributed state management)
- Bindings: Cron Binding (every 1 minute for reminder polling)
- Secrets: Vault or Kubernetes Secrets via Dapr
- Service Invocation: Backend ↔ Reminder Service communication

**Event Schema Example**:
```json
{
  "event_id": "uuid",
  "event_type": "task.created",
  "timestamp": "2026-01-30T12:00:00Z",
  "user_id": 123,
  "payload": {
    "task_id": 456,
    "title": "Daily Standup",
    "priority": "high",
    "due_date": "2026-01-31T09:00:00Z",
    "recurrence_rule": "FREQ=DAILY"
  }
}
```

**Risk Analysis**:
1. **RRULE Complexity**: Mitigated by using python-dateutil (battle-tested library)
2. **Kafka Access**: Fallback to alternative Dapr Pub/Sub components (Redis Streams, Azure Service Bus)
3. **Reminder Accuracy**: 1-minute polling interval achieves 60-second SLA (acceptable trade-off vs. complexity)
4. **Cloud Portability**: Helm values files for each cloud provider, Dapr abstractions for cloud services
5. **CI/CD Complexity**: Incremental rollout (Minikube first, then cloud), automated rollback strategies

## Outcome

- ✅ Impact: Generated comprehensive 11-phase implementation plan for Step 5 covering advanced features, event-driven architecture, microservices, multi-environment deployment, CI/CD automation, and observability. All technology decisions documented with rationale and trade-offs. Plan ready for task breakdown via /sp.tasks.
- 🧪 Tests: Planning phase - no tests executed. Test specifications will be created during /sp.tasks breakdown for each implementation phase.
- 📁 Files: 5 files created (plan.md with 11 phases, research.md with 7 technology decisions, data-model.md with extended schemas, quickstart.md with developer guide, module-interfaces.md with service contracts)
- 🔁 Next prompts: Run `/sp.tasks` to break down 11-phase plan into atomic, testable tasks with acceptance criteria. Then start Phase 0 (Research) to validate technology choices and create event schemas.
- 🧠 Reflection: Step 5 plan successfully bridges the gap between high-level specification (11 user stories) and concrete implementation (11 phases). Key architectural decisions documented with clear rationale: Dapr for portability, python-dateutil for RRULE compliance, PostgreSQL tsvector for search (avoiding Elasticsearch complexity), separate reminder microservice for scalability, in-cluster monitoring for portability. The plan maintains flexibility for cloud provider choice while ensuring production-grade observability and automation.

## Evaluation notes (flywheel)

- Failure modes observed: None - Plan generation succeeded on first attempt with comprehensive coverage of all specification requirements
- Graders run and results (PASS/FAIL): N/A (planning phase - graders will be applied during implementation phases)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): When implementing Step 5, validate Phase 0 (Research) decisions by building proof-of-concept for RRULE parsing with python-dateutil and Dapr Pub/Sub integration before committing to full implementation. This reduces risk of technology mismatch and enables early course correction if assumptions prove incorrect.
