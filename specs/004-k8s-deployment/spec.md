# Feature Specification: Local Kubernetes Deployment

**Feature Branch**: `004-k8s-deployment`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "create 004-step-4.... dir in D:\Quarter-4\spec_kit_plus\hackathon-todo\specs and make spec.md file inside, only for step 4 from D:\Quarter-4\spec_kit_plus\hackathon-todo\.specify\memory\constitution.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Backend API to Minikube (Priority: P1)

As a developer, I want to deploy the FastAPI backend application to a local Kubernetes cluster using Minikube, so that I can run the application in a production-like container orchestration environment.

**Why this priority**: Backend containerization and deployment is the foundation for the entire Kubernetes deployment. Without the backend running on Kubernetes, none of the other features can function.

**Independent Test**: Deploy backend container to Minikube, verify all pods are running with status "Ready 1/1", access the /health endpoint via port forwarding, and execute a sample task CRUD operation through the API.

**Acceptance Scenarios**:

1. **Given** a FastAPI backend application with Dockerfile, **When** I build the Docker image and deploy to Minikube using Helm, **Then** backend pods are running and healthy (liveness/readiness probes passing)
2. **Given** backend deployed on Minikube, **When** I access the /health endpoint via port forwarding, **Then** I receive a 200 OK response confirming service availability
3. **Given** backend running on Minikube, **When** I create a task via the API, **Then** the task is persisted to the external Neon database and can be retrieved
4. **Given** backend deployment with ConfigMaps and Secrets, **When** I inspect environment variables in the pod, **Then** configuration values match expected settings (CORS origins, database URL, API keys)

---

### User Story 2 - Deploy Frontend Application to Minikube (Priority: P2)

As a developer, I want to deploy the Next.js frontend application to a local Kubernetes cluster, so that users can access the web interface through Kubernetes Services with proper routing to the backend.

**Why this priority**: Frontend deployment enables end-to-end user interaction through the Kubernetes cluster. It depends on the backend being operational (P1) but is essential for testing the complete application flow.

**Independent Test**: Deploy frontend container to Minikube, access the application via NodePort from the host machine, verify that the UI loads correctly, and confirm that it can communicate with the backend service.

**Acceptance Scenarios**:

1. **Given** a Next.js frontend with Dockerfile and backend already deployed, **When** I build the frontend image and deploy to Minikube, **Then** frontend pods are running and accessible via NodePort service
2. **Given** frontend deployed on Minikube, **When** I access the application via minikube service URL or NodePort, **Then** the UI loads successfully in my browser
3. **Given** frontend and backend running on Minikube, **When** I perform a task operation through the UI, **Then** the frontend successfully communicates with the backend API within the cluster
4. **Given** frontend service configured as NodePort, **When** I check the service details, **Then** the frontend is accessible from my host machine on the specified NodePort (e.g., 30000)

---

### User Story 3 - Manage Configuration with Helm Charts (Priority: P3)

As a developer, I want to manage all Kubernetes resources using Helm charts with templating and values files, so that I can easily configure, deploy, upgrade, and rollback the application across different environments.

**Why this priority**: Helm provides declarative infrastructure management, versioning, and easy rollbacks. While important for operational efficiency, the application can technically be deployed using raw Kubernetes manifests, making this lower priority than getting the containers running (P1-P2).

**Independent Test**: Create Helm charts with templates, deploy the application using "helm install", upgrade the deployment with "helm upgrade", and rollback to a previous version with "helm rollback" - all without application downtime.

**Acceptance Scenarios**:

1. **Given** Helm charts with values.yaml and values-dev.yaml, **When** I run "helm install todo-app ./helm/todo-app -f values-dev.yaml", **Then** all backend and frontend resources are created successfully
2. **Given** a running Helm deployment, **When** I change a configuration value and run "helm upgrade", **Then** the deployment updates with rolling update strategy and zero downtime
3. **Given** a Helm deployment that has been upgraded, **When** I run "helm rollback todo-app", **Then** the deployment reverts to the previous version successfully
4. **Given** Helm values with environment-specific overrides, **When** I deploy with values-dev.yaml, **Then** Minikube-specific settings (NodePort, reduced replicas) are applied

---

### User Story 4 - Implement Health Checks and Resource Limits (Priority: P4)

As a platform engineer, I want all containers to have liveness/readiness probes and resource limits configured, so that Kubernetes can automatically restart unhealthy pods and prevent resource starvation.

**Why this priority**: Health checks and resource limits improve reliability and stability but are not strictly required for initial deployment. The application can run without them, though it won't be production-ready.

**Independent Test**: Deploy containers with health checks configured, simulate a pod crash or unresponsive state, verify that Kubernetes automatically restarts the pod. Test resource limits by checking pod resource usage doesn't exceed defined constraints.

**Acceptance Scenarios**:

1. **Given** deployments with liveness probes configured, **When** a pod becomes unresponsive (simulated), **Then** Kubernetes automatically restarts the pod after the failure threshold is reached
2. **Given** deployments with readiness probes configured, **When** a pod is not ready to serve traffic, **Then** Kubernetes does not route traffic to that pod until it passes readiness checks
3. **Given** deployments with resource limits (CPU, memory), **When** I check pod resource usage, **Then** containers cannot exceed defined limits and Kubernetes enforces constraints
4. **Given** deployments with resource requests, **When** Kubernetes schedules pods, **Then** it ensures nodes have sufficient resources before placement

---

### User Story 5 - Use AI DevOps Tools for Accelerated Deployment (Priority: P5)

As a developer learning Kubernetes, I want to leverage AI-powered DevOps tools (Gordon, kubectl-ai, Kagent), so that I can accelerate Dockerfile creation, Helm chart generation, and troubleshooting without deep Kubernetes expertise.

**Why this priority**: AI tools improve developer experience and learning curve but are optional accelerators. The deployment can be accomplished with traditional CLI tools, making this the lowest priority enhancement.

**Independent Test**: Use Gordon to generate Dockerfiles, kubectl-ai to deploy resources, and Kagent to analyze cluster health. Verify that AI-generated configurations work correctly and document the time savings compared to manual approach.

**Acceptance Scenarios**:

1. **Given** Docker AI Agent (Gordon) enabled, **When** I ask "Create a production Dockerfile for FastAPI", **Then** Gordon generates an optimized multi-stage Dockerfile that builds successfully
2. **Given** kubectl-ai installed, **When** I ask "deploy the todo frontend with 2 replicas", **Then** kubectl-ai generates and applies the correct Deployment manifest
3. **Given** Kagent configured, **When** I ask "analyze the cluster health", **Then** Kagent provides actionable insights about cluster resource usage, pod status, and potential issues
4. **Given** a failing pod, **When** I use kubectl-ai to troubleshoot with "why are pods failing?", **Then** kubectl-ai identifies the root cause and suggests remediation steps

---

### Edge Cases

- What happens when the Minikube cluster runs out of resources (CPU/memory)?
  - Kubernetes should fail to schedule new pods and report "Insufficient cpu/memory" errors
  - Existing running pods should continue operating unless evicted due to node pressure

- How does the system handle backend pod crashes?
  - Liveness probes detect unresponsive containers
  - Kubernetes automatically restarts crashed pods
  - Multiple replicas ensure availability during restarts

- What happens when the external Neon database is unreachable?
  - Backend health checks fail, pods marked as not ready
  - Kubernetes stops routing traffic to unhealthy pods
  - Application returns appropriate error messages to users

- How does the system handle configuration changes without downtime?
  - Rolling updates deploy new pods gradually
  - Old pods remain running until new pods are ready
  - Service routing ensures zero downtime during updates

- What happens when Helm charts have invalid configuration?
  - Helm validates templates before applying
  - Installation fails with descriptive error messages
  - No changes are applied to the cluster (atomic operation)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST containerize the FastAPI backend using Docker with multi-stage builds for optimization
- **FR-002**: System MUST containerize the Next.js frontend using Docker with Next.js standalone output mode
- **FR-003**: Both containers MUST expose health check endpoints (/health for backend, equivalent for frontend)
- **FR-004**: System MUST deploy backend and frontend to Minikube using Kubernetes Deployments with 2 replicas each
- **FR-005**: System MUST expose backend via ClusterIP Service for internal cluster access
- **FR-006**: System MUST expose frontend via NodePort Service for external host access
- **FR-007**: System MUST manage all Kubernetes resources using Helm charts with templating
- **FR-008**: Helm charts MUST support environment-specific configuration via values files (values.yaml, values-dev.yaml)
- **FR-009**: System MUST externalize configuration using Kubernetes ConfigMaps for non-sensitive data
- **FR-010**: System MUST externalize secrets using Kubernetes Secrets for sensitive data (API keys, tokens)
- **FR-011**: All deployments MUST have liveness probes configured to detect unresponsive containers
- **FR-012**: All deployments MUST have readiness probes configured to prevent traffic to non-ready pods
- **FR-013**: All containers MUST have resource requests and limits defined (CPU, memory)
- **FR-014**: System MUST support rolling updates with zero downtime when upgrading deployments
- **FR-015**: System MUST support Helm rollback to revert to previous deployment versions
- **FR-016**: Backend container MUST connect to external Neon PostgreSQL database (not containerized)
- **FR-017**: Frontend container MUST be configured to communicate with backend service within the cluster
- **FR-018**: System MUST run on Minikube cluster with minimum 2 CPUs and 4GB RAM
- **FR-019**: All Docker images MUST follow security best practices (non-root users, minimal base images)
- **FR-020**: System MUST support using AI DevOps tools (Gordon for Docker, kubectl-ai/Kagent for Kubernetes) as optional accelerators

### Key Entities

- **Backend Container**: Docker image containing FastAPI application, Python dependencies, and runtime configuration. Exposes port 8000 with /health endpoint.
- **Frontend Container**: Docker image containing Next.js application with standalone output. Exposes port 3000 with health check capability.
- **Backend Deployment**: Kubernetes Deployment managing 2 backend pod replicas with rolling update strategy, health checks, and resource limits.
- **Frontend Deployment**: Kubernetes Deployment managing 2 frontend pod replicas with rolling update strategy, health checks, and resource limits.
- **Backend Service**: Kubernetes ClusterIP Service routing internal cluster traffic to backend pods on port 8000.
- **Frontend Service**: Kubernetes NodePort Service exposing frontend pods to host machine on NodePort 30000.
- **Backend ConfigMap**: Kubernetes ConfigMap storing non-sensitive backend configuration (CORS origins, database URL without credentials).
- **Backend Secret**: Kubernetes Secret storing sensitive backend data (OpenAI API key, Better Auth secret, database password).
- **Frontend ConfigMap**: Kubernetes ConfigMap storing frontend configuration (API URL, public settings).
- **Helm Chart**: Package containing Chart.yaml metadata, values files, and Kubernetes resource templates for declarative deployment.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend and frontend containers build successfully in under 5 minutes each using multi-stage Dockerfiles
- **SC-002**: All pods reach "Running" status with "Ready 1/1" state within 60 seconds of Helm deployment
- **SC-003**: Health check endpoints respond within 5 seconds for all running containers
- **SC-004**: Frontend is accessible from host machine browser via NodePort within 10 seconds of deployment
- **SC-005**: Backend API responds to CRUD operations with latency under 200ms when accessed within the cluster
- **SC-006**: Helm upgrade completes with zero downtime using rolling update strategy (max 30 seconds to complete)
- **SC-007**: Helm rollback restores previous deployment version within 60 seconds
- **SC-008**: System tolerates single pod failure without service disruption (due to 2 replicas)
- **SC-009**: Kubernetes automatically restarts crashed pods within 30 seconds of liveness probe failure
- **SC-010**: All Step 3 chatbot features (task CRUD, natural language interface, conversation persistence) work correctly when deployed on Kubernetes
- **SC-011**: Resource limits prevent containers from exceeding defined CPU (500m backend, 200m frontend) and memory (512Mi backend, 256Mi frontend) constraints
- **SC-012**: Minikube cluster remains stable with all services running for at least 4 hours of continuous operation
- **SC-013**: AI DevOps tools (if used) reduce deployment time by at least 30% compared to manual approach (documented in PHRs)
- **SC-014**: Documentation enables a new developer to deploy the application to Minikube in under 30 minutes by following README instructions
- **SC-015**: All configuration values can be changed without rebuilding Docker images (via ConfigMaps, Secrets, and Helm values)
