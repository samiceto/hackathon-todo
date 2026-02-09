# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-k8s-deployment/`
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/

**Branch**: `004-k8s-deployment`
**Feature**: Step 4 - Kubernetes Deployment with Minikube and Helm

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

This is a monorepo with:
- **Backend**: `backend/api/` (FastAPI application)
- **Frontend**: `frontend/` (Next.js application)
- **Helm Charts**: `helm/todo-app/`
- **Kubernetes Manifests**: `k8s/` (optional reference)
- **Documentation**: `specs/004-k8s-deployment/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Minikube cluster setup

- [X] T001 Verify prerequisites: Docker Desktop 24+, Minikube 1.32+, kubectl 1.28+, Helm 3.x installed
- [X] T002 Start Minikube cluster with recommended configuration (2 CPUs, 4GB RAM, docker driver)
- [X] T003 [P] Configure kubectl to use Minikube context
- [X] T004 [P] Configure Docker CLI to use Minikube's Docker daemon via `eval $(minikube docker-env)`
- [X] T005 Create Helm chart directory structure at helm/todo-app/
- [X] T006 Create Chart.yaml metadata file at helm/todo-app/Chart.yaml
- [X] T007 [P] Create values.yaml (production defaults) at helm/todo-app/values.yaml
- [X] T008 [P] Create values-dev.yaml (Minikube overrides) at helm/todo-app/values-dev.yaml
- [X] T009 [P] Create _helpers.tpl template helpers at helm/todo-app/templates/_helpers.tpl
- [X] T010 [P] Create NOTES.txt post-install guide at helm/todo-app/templates/NOTES.txt
- [X] T011 [P] Update .gitignore to exclude secrets.yaml and built Docker images

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Docker image creation and base Helm templates that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T012 Create backend Dockerfile with multi-stage build at backend/api/Dockerfile
- [X] T013 Create backend .dockerignore at backend/api/.dockerignore
- [X] T014 Update Next.js config to enable standalone output in frontend/next.config.js
- [X] T015 Create frontend Dockerfile with multi-stage build at frontend/Dockerfile
- [X] T016 Create frontend .dockerignore at frontend/.dockerignore
- [X] T017 Build backend Docker image (todo-backend:latest) using Minikube's Docker daemon
- [X] T018 Build frontend Docker image (todo-frontend:latest) using Minikube's Docker daemon
- [X] T019 Verify both Docker images exist in Minikube's Docker environment

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Deploy Backend API to Minikube (Priority: P1) 🎯 MVP

**Goal**: Deploy FastAPI backend application to Minikube with health checks and database connectivity

**Independent Test**: Deploy backend container, verify pods running (Ready 1/1), access /health endpoint via port forwarding, execute sample CRUD operation through API

### Implementation for User Story 1

- [X] T020 [P] [US1] Create backend Deployment template at helm/todo-app/templates/backend-deployment.yaml
- [X] T021 [P] [US1] Create backend Service (ClusterIP) template at helm/todo-app/templates/backend-service.yaml
- [X] T022 [P] [US1] Create backend ConfigMap template at helm/todo-app/templates/backend-configmap.yaml
- [X] T023 [P] [US1] Create backend Secret template at helm/todo-app/templates/backend-secret.yaml
- [X] T024 [US1] Configure backend Deployment with liveness probe (path: /health, port: 8000)
- [X] T025 [US1] Configure backend Deployment with readiness probe (path: /health, port: 8000)
- [X] T026 [US1] Set backend resource limits (CPU: 500m, Memory: 512Mi) and requests (CPU: 250m, Memory: 256Mi)
- [X] T027 [US1] Configure backend environment variables from ConfigMap (DATABASE_URL, CORS_ORIGINS, LOG_LEVEL)
- [X] T028 [US1] Configure backend secrets from Secret (OPENAI_API_KEY, BETTER_AUTH_SECRET)
- [X] T029 [US1] Set backend replicas to 2 in values.yaml, override to 1 in values-dev.yaml
- [X] T030 [US1] Deploy backend to Minikube using `helm install todo-app ./helm/todo-app -f values-dev.yaml --set backend.secrets.openaiApiKey=... --set backend.secrets.betterAuthSecret=...`
- [X] T031 [US1] Verify backend pods reach Running status with Ready 1/1 within 60 seconds
- [X] T032 [US1] Test backend health endpoint via port-forward: `kubectl port-forward svc/todo-app-backend 8000:8000` and curl http://localhost:8000/health
- [X] T033 [US1] Test backend CRUD operations through API (create task, list tasks, update task, delete task)
- [X] T034 [US1] Verify backend environment variables match expected values: `kubectl exec <pod> -- env | grep DATABASE_URL`

**Checkpoint**: Backend is fully deployed and operational on Minikube, all P1 acceptance criteria met

---

## Phase 4: User Story 2 - Deploy Frontend Application to Minikube (Priority: P2)

**Goal**: Deploy Next.js frontend to Minikube with NodePort access and backend communication

**Independent Test**: Deploy frontend container, access UI via NodePort from host machine, verify UI loads, confirm communication with backend service

### Implementation for User Story 2

- [X] T035 [P] [US2] Create frontend Deployment template at helm/todo-app/templates/frontend-deployment.yaml
- [X] T036 [P] [US2] Create frontend Service (NodePort) template at helm/todo-app/templates/frontend-service.yaml
- [X] T037 [P] [US2] Create frontend ConfigMap template at helm/todo-app/templates/frontend-configmap.yaml
- [X] T038 [US2] Configure frontend Deployment with liveness probe (path: /, port: 3000)
- [X] T039 [US2] Configure frontend Deployment with readiness probe (path: /, port: 3000)
- [X] T040 [US2] Set frontend resource limits (CPU: 200m, Memory: 256Mi) and requests (CPU: 100m, Memory: 128Mi)
- [X] T041 [US2] Configure frontend environment variables from ConfigMap (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- [X] T042 [US2] Set frontend replicas to 2 in values.yaml, override to 1 in values-dev.yaml
- [X] T043 [US2] Configure frontend Service as NodePort on port 30000 in values-dev.yaml
- [X] T044 [US2] Deploy frontend using `helm upgrade todo-app ./helm/todo-app -f values-dev.yaml`
- [X] T045 [US2] Verify frontend pods reach Running status with Ready 1/1 within 60 seconds
- [X] T046 [US2] Access frontend via NodePort: `minikube service todo-app-frontend` (should open browser)
- [X] T047 [US2] Verify frontend UI loads successfully in browser at http://<minikube-ip>:30000
- [X] T048 [US2] Test frontend-backend communication: create a task through UI, verify it persists
- [X] T049 [US2] Verify frontend Service details: `kubectl get svc todo-app-frontend` shows NodePort 30000

**Checkpoint**: Frontend is deployed and accessible from host machine, can communicate with backend

---

## Phase 5: User Story 3 - Manage Configuration with Helm Charts (Priority: P3)

**Goal**: Implement full Helm chart lifecycle management with templating, upgrades, and rollbacks

**Independent Test**: Deploy with `helm install`, upgrade with `helm upgrade`, rollback with `helm rollback` - all without downtime

### Implementation for User Story 3

- [X] T050 [US3] Add rolling update strategy to backend Deployment (maxSurge: 1, maxUnavailable: 0)
- [X] T051 [US3] Add rolling update strategy to frontend Deployment (maxSurge: 1, maxUnavailable: 0)
- [X] T052 [US3] Parameterize all hardcoded values in backend templates using Helm templating syntax
- [X] T053 [US3] Parameterize all hardcoded values in frontend templates using Helm templating syntax
- [X] T054 [US3] Create values-prod.yaml placeholder for future production overrides at helm/todo-app/values-prod.yaml
- [X] T055 [US3] Test Helm install: `helm install todo-app ./helm/todo-app -f values-dev.yaml` (fresh cluster)
- [X] T056 [US3] Verify all backend and frontend resources created successfully after install
- [X] T057 [US3] Make configuration change in values-dev.yaml (e.g., change LOG_LEVEL from info to debug)
- [X] T058 [US3] Test Helm upgrade: `helm upgrade todo-app ./helm/todo-app -f values-dev.yaml`
- [X] T059 [US3] Verify rolling update occurs with zero downtime (watch pods: `kubectl get pods -w`)
- [X] T060 [US3] Verify configuration change applied: `kubectl get configmap todo-app-backend-config -o yaml | grep LOG_LEVEL`
- [X] T061 [US3] Test Helm rollback: `helm rollback todo-app`
- [X] T062 [US3] Verify rollback completes successfully and previous configuration restored
- [X] T063 [US3] Verify Helm history: `helm history todo-app` shows all revisions

**Checkpoint**: Helm chart supports full lifecycle management with zero-downtime updates

---

## Phase 6: User Story 4 - Implement Health Checks and Resource Limits (Priority: P4)

**Goal**: Configure comprehensive health checks and resource limits for production-readiness

**Independent Test**: Deploy with health checks, simulate pod crash, verify Kubernetes auto-restart, confirm resource limits enforced

### Implementation for User Story 4

- [X] T064 [US4] Verify backend liveness probe configured (initialDelaySeconds: 30, periodSeconds: 10, timeoutSeconds: 5, failureThreshold: 3)
- [X] T065 [US4] Verify backend readiness probe configured (initialDelaySeconds: 10, periodSeconds: 5, timeoutSeconds: 3, failureThreshold: 2)
- [X] T066 [US4] Verify frontend liveness probe configured (initialDelaySeconds: 30, periodSeconds: 10, timeoutSeconds: 5, failureThreshold: 3)
- [X] T067 [US4] Verify frontend readiness probe configured (initialDelaySeconds: 10, periodSeconds: 5, timeoutSeconds: 3, failureThreshold: 2)
- [X] T068 [US4] Test liveness probe failure: simulate backend pod crash using `kubectl delete pod`
- [X] T069 [US4] Verify Kubernetes automatically restarts crashed backend pod within 30 seconds
- [X] T070 [US4] Test readiness probe: deploy backend with failing readiness check, verify no traffic routed
- [X] T071 [US4] Enable Minikube metrics-server addon: `minikube addons enable metrics-server`
- [X] T072 [US4] Verify resource usage: `kubectl top pods` shows backend <512Mi memory and <500m CPU
- [X] T073 [US4] Verify resource usage: `kubectl top pods` shows frontend <256Mi memory and <200m CPU
- [X] T074 [US4] Test resource limits: describe pods to confirm requests and limits match specifications
- [X] T075 [US4] Document health check configuration in quickstart.md

**Checkpoint**: All health checks working, resource limits enforced, Kubernetes auto-healing verified

---

## Phase 7: User Story 5 - Use AI DevOps Tools for Accelerated Deployment (Priority: P5)

**Goal**: Leverage AI tools (Gordon, kubectl-ai, Kagent) to accelerate workflows and troubleshooting

**Independent Test**: Use Gordon for Dockerfile optimization, kubectl-ai for deployments, Kagent for cluster analysis, document time savings

### Implementation for User Story 5

- [ ] T076 [P] [US5] Verify Docker AI (Gordon) availability: check Docker Desktop Beta features
- [ ] T077 [P] [US5] Install kubectl-ai: `npm install -g kubectl-ai` (requires Node.js and OpenAI API key)
- [ ] T078 [P] [US5] Research Kagent installation and verify availability
- [ ] T079 [US5] Test Gordon: `docker ai "Review my backend Dockerfile for best practices"` and document suggestions
- [ ] T080 [US5] Test Gordon: `docker ai "Optimize my frontend Dockerfile for smallest image size"` and document suggestions
- [ ] T081 [US5] Test kubectl-ai: `kubectl-ai "scale the backend to 2 replicas"` and verify execution
- [ ] T082 [US5] Test kubectl-ai troubleshooting: simulate pod failure and ask `kubectl-ai "why are pods failing?"`
- [ ] T083 [US5] Test Kagent: `kagent "analyze the cluster health"` and document insights
- [ ] T084 [US5] Test Kagent: `kagent "optimize resource allocation for my deployments"` and document suggestions
- [ ] T085 [US5] Compare manual vs AI-assisted workflow time for common tasks (document in PHR)
- [ ] T086 [US5] Document AI tool usage patterns and prompts in quickstart.md
- [ ] T087 [US5] Create fallback procedures for when AI tools are unavailable

**Checkpoint**: AI DevOps tools integrated, workflows documented, time savings quantified

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final improvements

- [X] T088 [P] Update root README.md with Step 4 deployment instructions
- [X] T089 [P] Update CLAUDE.md with Step 4 container and Kubernetes context
- [X] T090 [P] Create deployment troubleshooting guide in specs/004-k8s-deployment/TROUBLESHOOTING.md
- [X] T091 Run complete quickstart.md validation: fresh Minikube cluster to deployed application in <30 minutes
- [X] T092 Test end-to-end application flow: Tasks UI + Chatbot with all Step 3 features working on Kubernetes
- [X] T093 Document resource usage metrics (pod CPU/memory, image sizes, startup times)
- [X] T094 [P] Add security scanning documentation: `docker scan todo-backend:latest` and `docker scan todo-frontend:latest`
- [X] T095 Test Helm chart portability: uninstall, re-install on clean cluster, verify success
- [X] T096 Verify all 15 success criteria from spec.md are met
- [X] T097 Create PHR documenting Step 4 completion with metrics and learnings

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (Backend) must complete before User Story 2 (Frontend) since frontend needs backend service
  - User Story 3 (Helm) can proceed after US1+US2
  - User Story 4 (Health Checks) can proceed after US1+US2
  - User Story 5 (AI Tools) can proceed in parallel with US1-4 (optional accelerator)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Backend)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - Frontend)**: Depends on User Story 1 (needs backend service URL)
- **User Story 3 (P3 - Helm)**: Depends on User Story 1 + 2 (needs deployments to upgrade/rollback)
- **User Story 4 (P4 - Health Checks)**: Depends on User Story 1 + 2 (health checks are part of deployments)
- **User Story 5 (P5 - AI Tools)**: Independent - can run in parallel as optional accelerator

### Within Each User Story

- Kubernetes resource templates (Deployment, Service, ConfigMap, Secret) can be created in parallel
- Deployment must occur after all templates are created
- Verification tests must occur after deployment
- Configuration of health checks and resource limits happens within Deployment templates

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003, T004 can run in parallel (kubectl + Docker configuration)
**Phase 1 (Setup)**: Tasks T007, T008, T009, T010, T011 can run in parallel (Helm chart files)

**Phase 2 (Foundational)**: Tasks T012, T013 can run in parallel (backend Docker files)
**Phase 2 (Foundational)**: Tasks T014, T015, T016 can run in parallel (frontend Docker files)

**Phase 3 (User Story 1)**: Tasks T020, T021, T022, T023 can run in parallel (backend Kubernetes templates)

**Phase 4 (User Story 2)**: Tasks T035, T036, T037 can run in parallel (frontend Kubernetes templates)

**Phase 7 (User Story 5)**: Tasks T076, T077, T078 can run in parallel (AI tool installations)

**Phase 8 (Polish)**: Tasks T088, T089, T090, T094 can run in parallel (documentation tasks)

---

## Parallel Example: User Story 1 (Backend Deployment)

```bash
# Launch all Kubernetes template creation in parallel:
Task T020: "Create backend Deployment template at helm/todo-app/templates/backend-deployment.yaml"
Task T021: "Create backend Service template at helm/todo-app/templates/backend-service.yaml"
Task T022: "Create backend ConfigMap template at helm/todo-app/templates/backend-configmap.yaml"
Task T023: "Create backend Secret template at helm/todo-app/templates/backend-secret.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Minikube + Helm structure)
2. Complete Phase 2: Foundational (Docker images)
3. Complete Phase 3: User Story 1 (Backend Deployment)
4. **STOP and VALIDATE**: Test backend independently via port-forward
5. Deploy/demo backend on Kubernetes

### Incremental Delivery

1. Setup + Foundational → Docker images ready
2. Add User Story 1 (Backend) → Test independently → Backend running on K8s (MVP!)
3. Add User Story 2 (Frontend) → Test independently → Full-stack app on K8s
4. Add User Story 3 (Helm) → Test upgrades/rollbacks → Production-ready deployments
5. Add User Story 4 (Health) → Test auto-healing → Kubernetes orchestration complete
6. Add User Story 5 (AI Tools - Optional) → Accelerate workflows → Enhanced developer experience

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Backend)
   - Developer B: User Story 5 (AI Tools - can proceed independently)
3. After US1 complete:
   - Developer A: User Story 2 (Frontend)
   - Developer B: User Story 4 (Health Checks)
4. After US1+US2 complete:
   - Developer A or B: User Story 3 (Helm lifecycle)

---

## Task Count Summary

- **Phase 1 (Setup)**: 11 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (User Story 1 - Backend)**: 15 tasks
- **Phase 4 (User Story 2 - Frontend)**: 15 tasks
- **Phase 5 (User Story 3 - Helm)**: 14 tasks
- **Phase 6 (User Story 4 - Health)**: 12 tasks
- **Phase 7 (User Story 5 - AI Tools)**: 12 tasks
- **Phase 8 (Polish)**: 10 tasks

**Total**: 97 tasks

**Parallel Tasks**: 21 tasks marked with [P] can run in parallel with other tasks
**User Story Distribution**:
- US1 (Backend): 15 tasks
- US2 (Frontend): 15 tasks
- US3 (Helm): 14 tasks
- US4 (Health): 12 tasks
- US5 (AI Tools): 12 tasks
- Infrastructure: 19 tasks (Setup + Foundational)
- Polish: 10 tasks

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 34 tasks for basic backend deployment

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story builds on previous stories but should be independently completable
- All tasks include exact file paths for implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- AI DevOps tools (US5) are OPTIONAL - include fallback to standard CLI commands
- Database (Neon) remains external - NOT containerized in Step 4

---

**Tasks Generated**: 2026-01-24
**Total Tasks**: 97
**Feature**: 004-k8s-deployment (Step 4 - Local Kubernetes Deployment)
**Next Command**: `/sp.implement` to execute tasks phase by phase
