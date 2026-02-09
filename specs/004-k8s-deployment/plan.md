# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-k8s-deployment` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-k8s-deployment/spec.md`

**Note**: This plan implements Step 4 from the project constitution: deploying the Todo Chatbot application to a local Kubernetes cluster using Minikube, Helm Charts, and AI-powered DevOps tools (Docker AI/Gordon, kubectl-ai, Kagent).

## Summary

Deploy the fully-functional Todo Chatbot application (Step 3 complete) to a local Kubernetes cluster using Minikube for container orchestration. This involves containerizing the FastAPI backend and Next.js frontend using Docker with multi-stage builds, creating Helm Charts for declarative infrastructure management, implementing health checks and resource limits, and leveraging AI DevOps tools (Gordon for Docker, kubectl-ai/Kagent for Kubernetes) to accelerate deployment workflows. The external Neon PostgreSQL database remains cloud-hosted (not containerized), while all application services run on Minikube with proper configuration management via ConfigMaps and Secrets.

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ (FastAPI application from Step 2-3)
- Frontend: Node.js 20+ / Next.js 16+ (App Router from Step 2-3)
- Container Runtime: Docker 24+ (Docker Desktop with Kubernetes support)
- Orchestration: Kubernetes 1.28+ (via Minikube)

**Primary Dependencies**:
- **Backend**: FastAPI, SQLModel, OpenAI Agents SDK, Better Auth JWT verification, uvicorn
- **Frontend**: Next.js 16+, React, OpenAI ChatKit, Better Auth, Tailwind CSS
- **Container Tools**: Docker, Docker AI Agent (Gordon - optional but recommended)
- **Orchestration Tools**: Minikube, Helm 3.x, kubectl
- **AI DevOps**: kubectl-ai (optional), Kagent (optional)

**Storage**:
- **Database**: Neon Serverless PostgreSQL (external, cloud-hosted - NOT containerized)
- **Container Storage**: Ephemeral (no persistent volumes for application pods)
- **Configuration**: Kubernetes ConfigMaps (non-sensitive), Kubernetes Secrets (API keys, tokens)

**Testing**:
- **Backend**: pytest (existing tests from Steps 1-3)
- **Frontend**: Jest/React Testing Library (if implemented in Steps 2-3)
- **Container Testing**: Docker health checks, manual smoke tests
- **Kubernetes Testing**: Liveness/readiness probes, manual end-to-end testing via port-forwarding
- **Integration**: End-to-end flow verification (frontend → backend → database)

**Target Platform**:
- **Development**: Minikube on Docker Desktop (Linux containers via WSL 2 on Windows)
- **Cluster**: Single-node Kubernetes cluster on local machine
- **Minimum Resources**: 2 CPUs, 4GB RAM (Minikube configuration)
- **Access**: Frontend via NodePort (host:30000), Backend via ClusterIP (internal only)

**Project Type**: Web application (full-stack) with containerized deployment

**Performance Goals**:
- Container startup time: <30 seconds per pod
- Health check response: <5 seconds
- Application API response: <200ms p95 (same as Step 2-3)
- Chat response time: <3 seconds including AI processing (same as Step 3)
- Rolling update completion: <60 seconds with zero downtime
- Helm deployment time: <2 minutes (install/upgrade)

**Constraints**:
- Backend container memory limit: 512Mi, CPU limit: 500m
- Frontend container memory limit: 256Mi, CPU limit: 200m
- Database is external (Neon) - NOT part of Kubernetes cluster
- Minikube cluster must run on developer workstation (no cloud resources)
- Must use Docker Desktop Kubernetes or standalone Minikube
- All AI DevOps tool usage is OPTIONAL (fallback to standard CLI)
- No persistent volumes (application is stateless, database is external)

**Scale/Scope**:
- 2 backend replicas, 2 frontend replicas (development)
- Single Minikube cluster on local machine
- Supports 100+ concurrent users (same as Step 2-3 application)
- 5 Kubernetes Deployments total: backend (2 pods), frontend (2 pods)
- 8+ Kubernetes resources: Deployments, Services, ConfigMaps, Secrets
- Helm Chart with 10+ template files
- Zero downtime during rolling updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec-Driven Development** | ✅ PASS | Feature spec complete in `specs/004-k8s-deployment/spec.md`. All Dockerfiles and Helm charts will be generated via Claude Code from specifications. No manual coding. |
| **II. Iterative Refinement Through AI** | ✅ PASS | Specifications will iterate based on Claude Code output. Dockerfile and Helm chart generation will be refined through spec updates, not manual edits. |
| **III. Clean Architecture & Project Structure** | ✅ PASS | Monorepo structure maintained. New directories: `helm/`, `k8s/` (optional), Docker files in `backend/api/` and `frontend/`. Existing source code unchanged. |
| **IV. Test-Driven Development** | ✅ PASS | Existing tests from Steps 1-3 remain valid. New container tests (health checks) and integration tests (deployment verification) will be specified before implementation. |
| **V. Documentation & Traceability** | ✅ PASS | PHRs will document all development sessions. README updated with Step 4 deployment instructions. Commit messages follow conventional commits. |
| **VI. Human as Tool Strategy** | ✅ PASS | Will invoke user for: Docker base image selection, Helm chart structure decisions, Minikube resource allocation, AI tool availability confirmation. |
| **VII. Security & Best Practices** | ✅ PASS | Dockerfiles use non-root users, minimal base images. Secrets externalized to Kubernetes Secrets. No hardcoded credentials. |

### Step 4 Specific Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **XIX. Container-First Architecture** | ✅ PASS | Both frontend and backend will be containerized with multi-stage Dockerfiles. Gordon (Docker AI) will be used if available, with standard Docker CLI fallback. |
| **XX. Declarative Infrastructure with Helm** | ✅ PASS | All Kubernetes resources defined via Helm Charts. kubectl-ai/Kagent will assist chart generation. Templates will use parameterization for environment-specific configuration. |
| **XXI. Local Kubernetes with Minikube** | ✅ PASS | Minikube will be used for local cluster (2 CPUs, 4GB RAM). All deployments tested locally before any cloud migration. |
| **XXII. AI-Assisted DevOps Operations** | ✅ PASS | Gordon for Docker, kubectl-ai for Kubernetes, Kagent for cluster analysis. AI tool usage documented in PHRs. Standard CLI fallback if tools unavailable. |
| **XXIII. Environment Parity and Configuration Management** | ✅ PASS | ConfigMaps for non-sensitive config, Secrets for API keys. Helm values files for environment overrides (values-dev.yaml for Minikube). |

### Step 4 Quality Gates (Pre-Implementation)

- [ ] Dockerfiles specified for backend and frontend with multi-stage builds
- [ ] Helm chart structure defined with all required templates
- [ ] ConfigMap and Secret specifications documented
- [ ] Health check endpoints identified (/health for backend)
- [ ] Resource limits specified (CPU, memory for all containers)
- [ ] Minikube setup procedure documented
- [ ] AI DevOps tool usage strategy defined
- [ ] Deployment validation criteria established

### Complexity Justification

**No violations requiring justification.** Step 4 adds containerization and orchestration layer without modifying existing application architecture. This aligns with constitution's incremental evolution approach (Steps 1→2→3→4→5).

## Project Structure

### Documentation (this feature)

```text
specs/004-k8s-deployment/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already exists)
├── research.md          # Phase 0 output - Docker/K8s/Helm best practices
├── data-model.md        # Phase 1 output - Container specifications
├── quickstart.md        # Phase 1 output - Minikube deployment guide
├── contracts/           # Phase 1 output - Kubernetes resource contracts
│   ├── backend-deployment.yaml    # Backend Deployment specification
│   ├── frontend-deployment.yaml   # Frontend Deployment specification
│   ├── backend-service.yaml       # Backend Service specification
│   ├── frontend-service.yaml      # Frontend Service specification
│   ├── configmaps.yaml            # ConfigMap specifications
│   └── secrets.yaml               # Secret specifications (placeholders)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Step 4 adds containerization and orchestration infrastructure to existing monorepo:**

```text
hackathon-todo/                          # Repository root
├── .spec-kit/                           # Monorepo config (existing)
│   ├── config.yaml
│   └── memory/
│       └── constitution.md              # v4.0.0 (includes Step 4 principles)
├── .specify/                            # Symlinks to .spec-kit
├── backend/
│   ├── console/                         # Step 1 (preserved, unchanged)
│   └── api/                             # Step 2-3 (existing, add Docker files)
│       ├── Dockerfile                   # NEW: Multi-stage backend container
│       ├── .dockerignore                # NEW: Docker ignore rules
│       ├── src/                         # Existing application code (unchanged)
│       │   ├── models/
│       │   ├── services/
│       │   ├── api/
│       │   ├── auth/
│       │   ├── mcp/
│       │   └── agents/
│       ├── tests/                       # Existing tests (unchanged)
│       ├── alembic/                     # Existing migrations (unchanged)
│       ├── pyproject.toml               # Existing (unchanged)
│       └── .env.example                 # Existing (unchanged)
├── frontend/                            # Step 2-3 (existing, add Docker files)
│   ├── Dockerfile                       # NEW: Multi-stage frontend container
│   ├── .dockerignore                    # NEW: Docker ignore rules
│   ├── src/                             # Existing application code (unchanged)
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── public/                          # Existing (unchanged)
│   ├── package.json                     # Existing (unchanged)
│   └── .env.local.example               # Existing (unchanged)
├── helm/                                # NEW: Helm charts directory
│   └── todo-app/                        # NEW: Main Helm chart
│       ├── Chart.yaml                   # Helm chart metadata
│       ├── values.yaml                  # Default configuration values
│       ├── values-dev.yaml              # Minikube overrides
│       ├── values-prod.yaml             # Production overrides (placeholder for Step 5)
│       └── templates/                   # Kubernetes resource templates
│           ├── _helpers.tpl             # Template helper functions
│           ├── backend-deployment.yaml  # Backend Deployment template
│           ├── backend-service.yaml     # Backend Service template
│           ├── backend-configmap.yaml   # Backend ConfigMap template
│           ├── backend-secret.yaml      # Backend Secret template
│           ├── frontend-deployment.yaml # Frontend Deployment template
│           ├── frontend-service.yaml    # Frontend Service template
│           ├── frontend-configmap.yaml  # Frontend ConfigMap template
│           └── NOTES.txt                # Post-install notes
├── k8s/                                 # NEW (OPTIONAL): Raw manifests for reference
│   ├── backend/                         # Raw backend manifests (if generated)
│   └── frontend/                        # Raw frontend manifests (if generated)
├── specs/                               # Specifications (existing structure)
│   ├── features/
│   │   ├── 001-step-1-core-features/    # Step 1 (existing)
│   │   ├── 002-step-2-web-app/          # Step 2 (if exists)
│   │   ├── 003-step-3-ai-chatbot/       # Step 3 (existing)
│   │   └── 004-k8s-deployment/          # Step 4 (this feature - NEW)
│   ├── api/                             # API specs (existing)
│   ├── database/                        # Database specs (existing)
│   ├── ui/                              # UI specs (existing)
│   ├── containers/                      # NEW: Dockerfile specifications
│   │   ├── backend-dockerfile.md
│   │   └── frontend-dockerfile.md
│   └── kubernetes/                      # NEW: Kubernetes manifest specs
│       ├── deployments.md
│       ├── services.md
│       └── configuration.md
├── history/
│   └── prompts/
│       ├── constitution/                # Constitution PHRs
│       ├── 001-step-1-core-features/    # Step 1 PHRs
│       ├── 003-step-3-ai-chatbot/       # Step 3 PHRs (if exists)
│       └── 004-k8s-deployment/          # NEW: Step 4 PHRs
├── README.md                            # Updated with Step 4 instructions
├── CLAUDE.md                            # Root context (updated for Step 4)
└── .gitignore                           # Updated to exclude built images
```

**Structure Decision**:

This follows **Option 2: Web application** from the template, extended with containerization infrastructure. The structure maintains backward compatibility with Steps 1-3 while adding:

1. **Container Definitions**: Dockerfiles in `backend/api/` and `frontend/` directories alongside their respective source code
2. **Helm Charts**: Centralized `helm/todo-app/` directory for declarative Kubernetes resource management
3. **Specification Docs**: New `specs/containers/` and `specs/kubernetes/` for container and orchestration specifications
4. **Optional Raw Manifests**: `k8s/` directory for reference (can be generated by kubectl-ai or manually)

**Key Design Decisions**:
- Dockerfiles live with their application code (not centralized) for proximity to source
- Single Helm chart (`todo-app`) manages all resources (backend + frontend) for atomic deployments
- Existing application source code remains **completely unchanged** (only Docker/K8s infrastructure added)
- Database remains external (Neon) - not included in Kubernetes deployment

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All Step 4 principles are satisfied without introducing unjustified complexity. The containerization and orchestration infrastructure is additive (does not modify existing application architecture) and aligns with the constitution's incremental evolution strategy.

---

## Phase 0: Research & Discovery

This section will be filled during implementation to document all technology choices, best practices research, and architectural decisions for Docker, Kubernetes, and Helm deployments.

**Research Topics**:
1. Docker multi-stage build best practices for Python FastAPI applications
2. Docker multi-stage build best practices for Next.js applications
3. Kubernetes Deployment strategies (RollingUpdate vs Recreate)
4. Health check implementation patterns (liveness vs readiness probes)
5. Resource limits and requests tuning for FastAPI and Next.js containers
6. Helm chart templating best practices
7. ConfigMap and Secret management strategies
8. Minikube setup and configuration for development workflows
9. AI DevOps tool usage: Gordon, kubectl-ai, Kagent capabilities and limitations
10. Container security best practices (non-root users, minimal images)

**Output**: `research.md` document capturing all findings and decisions

---

## Phase 1: Design & Contracts

This section will be filled during implementation to define concrete container specifications, Kubernetes resource contracts, and deployment procedures.

**Design Artifacts**:
1. **data-model.md**: Container image specifications (Dockerfile structure, base images, build stages, exposed ports, health checks)
2. **contracts/**: Kubernetes resource YAML specifications (Deployments, Services, ConfigMaps, Secrets)
3. **quickstart.md**: Minikube deployment quickstart guide

**Output**: Complete container and Kubernetes resource specifications ready for implementation

---

## Phase 2: Task Breakdown

**Note**: Phase 2 (task generation) is handled by the `/sp.tasks` command and is NOT part of `/sp.plan`.

After Phase 1 completion, run:
```bash
/sp.tasks
```

This will generate `specs/004-k8s-deployment/tasks.md` with dependency-ordered implementation tasks.

---

## Next Steps

1. ✅ Complete plan.md (this file) - **DONE**
2. ⏳ Create research.md - **NEXT**
3. ⏳ Create data-model.md
4. ⏳ Create contracts/ directory with resource specifications
5. ⏳ Create quickstart.md
6. ⏳ Update agent context
7. ⏳ Run `/sp.tasks` to generate tasks.md
8. ⏳ Run `/sp.implement` to execute tasks
