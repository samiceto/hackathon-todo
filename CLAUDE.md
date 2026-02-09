# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

---

# Project-Specific Context: Hackathon Todo

## Project Overview

**Hackathon Todo** is a progressive task management application being built in 5 incremental steps, from a simple CLI tool to a cloud-deployed full-stack application with AI capabilities.

**Current Status**: Step 1 Complete, Monorepo Restructuring in Progress 🔨

## Monorepo Structure

This project is organized as a monorepo to support gradual evolution from console app to full-stack application:

```
hackathon-todo/                    # Root (you are here)
├── .spec-kit/                     # Monorepo configuration
│   └── config.yaml               # Phase definitions, tech stack
├── backend/                       # Backend services
│   ├── console/                  # Step 1: Original console app (working)
│   │   ├── src/hackathon_todo/  # Console app source
│   │   ├── tests/               # Console app tests (129 tests, 97.44% coverage)
│   │   ├── pyproject.toml       # Python project config
│   │   └── README.md            # Console app documentation
│   └── CLAUDE.md                # Backend-specific context (future FastAPI)
├── frontend/                      # Frontend application (future)
│   └── CLAUDE.md                # Frontend-specific context (future Next.js)
├── specs/                         # Organized specifications
│   ├── features/                 # Feature specifications
│   ├── api/                      # API endpoint specifications
│   ├── database/                 # Database schema specifications
│   ├── ui/                       # UI component specifications
│   ├── overview.md              # Project overview
│   └── architecture.md          # System architecture
├── history/                       # Development history
│   └── prompts/                  # Prompt History Records
├── CLAUDE.md                     # Root context (this file)
└── README.md                     # User documentation
```

## Navigation Guide

**When working on different parts of the project, read the appropriate CLAUDE.md:**

- **Root CLAUDE.md** (this file): Monorepo organization, SDD workflow, general guidelines
- **backend/CLAUDE.md**: Backend-specific context (console app, future FastAPI)
- **frontend/CLAUDE.md**: Frontend-specific context (future Next.js)

**Technology Stack**:
- **Current (Step 1)**: Python 3.13+, UV, pytest, in-memory storage
- **Future (Step 2+)**: FastAPI, Next.js 16+, PostgreSQL, Better Auth, Docker
- **Future (Step 3+)**: OpenAI chatbot, MCP integration
- **Future (Step 4+)**: Kubernetes deployment

**Entry Points**:
- Console app: `cd backend/console && uv run hackathon-todo`
- Backend API: (not yet implemented)
- Frontend: (not yet implemented)

## Current Implementation Status

### Step 1: Core Todo Features ✅ COMPLETE
**Status**: All 5 user stories implemented, tested, and integrated
**Test Coverage**: 97.44% (129 tests passing)
**Features**:
- ✅ Add tasks (title + optional description)
- ✅ View all tasks (formatted list with status indicators)
- ✅ Mark tasks complete/incomplete (toggle)
- ✅ Update task details (title and/or description)
- ✅ Delete tasks
- ✅ Interactive menu-driven interface
- ✅ Error handling with retry logic
- ✅ Graceful exit (Ctrl+C support)

### Steps 2-5: Future Roadmap
- **Step 2**: Full-stack web app (FastAPI, Next.js, PostgreSQL, Docker)
- **Step 3**: AI-powered chatbot (OpenAI integration, NLP)
- **Step 4**: Local Kubernetes deployment (Minikube)
- **Step 5**: Advanced cloud deployment (CI/CD, monitoring)

## Architecture Overview

### Layered Architecture (Step 1)

The application uses clean architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│  Application Layer (main.py)           │  ← Entry point, menu loop
├─────────────────────────────────────────┤
│  UI Layer (ui.py)                      │  ← User interaction, formatting
├─────────────────────────────────────────┤
│  Storage Layer (storage.py)            │  ← CRUD operations
├─────────────────────────────────────────┤
│  Data Layer (models.py)                │  ← Task entity, validation
└─────────────────────────────────────────┘
```

**Design Principles**:
- Each layer depends only on layers below it
- No circular dependencies
- Clear interfaces between layers
- Testable in isolation

## Module Organization

### Console App (backend/console/src/hackathon_todo/)

For detailed console app architecture, see **backend/CLAUDE.md**

**Key modules**:
- **models.py**: Task dataclass with validation
- **storage.py**: In-memory CRUD operations
- **ui.py**: Console interface functions
- **main.py**: Application entry point

**Tests** (backend/console/tests/):
- 129 tests, 97.44% coverage
- Unit tests: test_models.py, test_storage.py, test_ui.py
- Integration tests: test_integration.py

## Key Implementation Details

### Task Data Model

```python
@dataclass
class Task:
    id: int                    # Unique identifier (auto-assigned)
    title: str                 # Required, non-empty
    description: str = ""      # Optional
    completed: bool = False    # Status (incomplete by default)
    created_at: datetime       # Creation timestamp (auto-assigned)
```

### Storage Pattern

- **Type**: In-memory dictionary `{task_id: Task}`
- **ID Generation**: Sequential auto-increment (next_id counter)
- **Persistence**: Session-based (data lost on exit)
- **Migration Path**: Ready for PostgreSQL in Step 2 (same interface)

### UI Patterns

**Input Validation**:
- `get_non_empty_input()`: Retry loop for required fields
- `get_task_id()`: Numeric validation + existence check
- `get_optional_input()`: Skip with Enter, whitespace treated as skip

**Status Indicators**:
- `○` (white circle) = Incomplete task
- `✓` (check mark) = Complete task

**Error Handling**:
- User-friendly error messages
- Retry loops for invalid input
- No crashes on bad data

### Menu Loop Pattern

```python
while True:
    display_menu()
    choice = input("Enter your choice (1-6): ")

    if choice == "1": add_task_ui(storage)
    elif choice == "2": view_tasks_ui(storage)
    # ... other choices
    elif choice == "6": break
    else: print("Invalid choice...")
```

## Testing Approach

### Test-Driven Development (TDD)
- Write tests first, then implementation
- All features have comprehensive test coverage
- Manual tests documented for each phase

### Test Coverage Metrics
- **Total**: 97.44% (195 statements, 129 tests)
- **Requirement**: >90% coverage (exceeded ✅)
- **Breakdown**:
  - models.py: 100%
  - storage.py: 100%
  - ui.py: 96%
  - main.py: 97%

### Test Organization
- Unit tests per module (test_models.py, test_storage.py, test_ui.py)
- Integration tests (test_integration.py)
- Manual end-to-end tests (documented in history/)

### Running Tests

```bash
# Console app tests
cd backend/console
uv run pytest

# Verbose output
uv run pytest -v

# Coverage report
uv run pytest --cov=src/hackathon_todo --cov-report=html
```

## Development Workflow

### Spec-Driven Development (SDD) Process

1. **Specify** (`/sp.specify`): Define requirements in specs/<feature>/spec.md
2. **Plan** (`/sp.plan`): Create implementation plan in specs/<feature>/plan.md
3. **Tasks** (`/sp.tasks`): Break down into testable tasks in specs/<feature>/tasks.md
4. **Implement** (`/sp.implement`): Execute tasks phase by phase (TDD approach)
5. **Validate**: Verify acceptance criteria met

### Current Feature Structure

```
specs/001-step-1-core-features/
├── spec.md           # User stories, acceptance criteria
├── plan.md           # Architecture decisions, module design
├── tasks.md          # 41 tasks across 9 phases
├── data-model.md     # Task entity specification
└── module-interfaces.md  # Function signatures, contracts
```

### Prompt History Records (PHRs)

All development work is documented in `history/prompts/001-step-1-core-features/`:
- 0001-0008: Initial setup and foundational components
- 0009: Phase 6 implementation (Update Task Details)
- 0010: Phase 7 implementation (Delete Tasks)
- 0011: Phase 8 implementation (Application Integration)
- 0012+: Phase 9+ (Polish & Documentation)

## Known Constraints and Technical Debt

### Module Size
- **ui.py**: 386 lines (exceeds 300-line guideline)
- **Acceptable**: For Step 1 MVP
- **Refactoring Plan**: Split into input_helpers.py, task_operations.py, menu.py in Step 2

### Data Persistence
- **Current**: In-memory (data lost on exit)
- **Acceptable**: For Step 1 CLI application
- **Migration**: PostgreSQL + SQLModel in Step 2

### Concurrency
- **Current**: Single-process, no threading
- **Acceptable**: For Step 1 CLI application
- **Enhancement**: Thread-safe storage in Step 2 web application

## Working with This Codebase

### Adding New Features

1. Check if it fits Step 1 scope (CLI todo features)
2. If yes: Update spec.md, plan.md, tasks.md
3. Follow TDD: Write tests first, then implementation
4. Maintain >90% test coverage
5. Create PHR for implementation work

### Modifying Existing Features

1. Read relevant module and tests first
2. Understand current behavior and contracts
3. Update tests to reflect new behavior
4. Update implementation
5. Verify all 129 existing tests still pass
6. Document changes in PHR

### Code Style Guidelines

- **Type Hints**: Required for all functions
- **Docstrings**: Required for public functions
- **Error Handling**: User-friendly messages, retry loops
- **Testing**: 100% coverage for new code
- **Naming**: Descriptive, clear intent (e.g., get_non_empty_input())

### Running the Application

```bash
# Console app (Step 1)
cd backend/console
uv run hackathon-todo
# OR
uv run python -m hackathon_todo.main

# Run tests
cd backend/console
uv run pytest

# Install dependencies
cd backend/console
uv sync
```

## Quick Reference

### Important Paths (Monorepo)
- **Console app source**: `backend/console/src/hackathon_todo/`
- **Console app tests**: `backend/console/tests/`
- **Specs**: `specs/` (organized by type: features/, api/, database/, ui/)
- **History**: `history/prompts/`
- **Constitution**: `.specify/memory/constitution.md`
- **Monorepo config**: `.spec-kit/config.yaml`

### Key Files to Reference
- **Root README.md**: Monorepo overview, quick start guide
- **backend/console/README.md**: Console app documentation
- **backend/CLAUDE.md**: Backend-specific context
- **frontend/CLAUDE.md**: Frontend-specific context (placeholder)
- **specs/overview.md**: Project overview (future)
- **specs/architecture.md**: System architecture (future)

### Current Branch
- **Name**: `004-k8s-deployment`
- **Status**: Step 4 implementation - Phases 5-6 complete (Helm Lifecycle + Health Checks)

---

## Step 4: Kubernetes Deployment Context 🐳

**Status**: IN PROGRESS (Phases 5-6 Complete)
**Goal**: Deploy full-stack Todo Chatbot to local Kubernetes cluster using Minikube and Helm

### Implementation Progress

- ✅ **Phase 1**: Setup (Minikube + Helm structure)
- ✅ **Phase 2**: Foundational (Docker images built)
- ✅ **Phase 3**: User Story 1 (Backend deployed)
- ✅ **Phase 4**: User Story 2 (Frontend deployed)
- ✅ **Phase 5**: User Story 3 (Helm lifecycle management) - **JUST COMPLETED**
- ✅ **Phase 6**: User Story 4 (Health checks + resource limits) - **JUST COMPLETED**
- ⏳ **Phase 7**: User Story 5 (AI DevOps tools) - SKIPPED (optional)
- ⏳ **Phase 8**: Polish & validation - IN PROGRESS

### Kubernetes Architecture

**Deployed Components**:
```
┌──────────────────────────────────────────────┐
│  Kubernetes Cluster (Minikube)              │
│                                              │
│  ┌────────────────┐  ┌──────────────────┐   │
│  │ Frontend Pods  │  │  Backend Pods    │   │
│  │ (Next.js)      │  │  (FastAPI)       │   │
│  │ Replicas: 1    │  │  Replicas: 1     │   │
│  │ Port: 3000     │  │  Port: 8000      │   │
│  └────────┬───────┘  └────────┬─────────┘   │
│           │                   │              │
│  ┌────────▼───────┐  ┌───────▼──────────┐   │
│  │ Frontend Svc   │  │  Backend Svc     │   │
│  │ NodePort:30000 │  │  ClusterIP:8000  │   │
│  └────────────────┘  └──────────────────┘   │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │  ConfigMaps & Secrets                  │  │
│  │  - Backend config (DB, CORS, logs)     │  │
│  │  - Backend secrets (API keys)          │  │
│  │  - Frontend config (API URL)           │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                    │
                    ▼
          External: Neon PostgreSQL
          (NOT containerized)
```

### Docker Images

**Backend (todo-backend:latest)**:
- **Base**: python:3.13-slim
- **Build**: Multi-stage build
- **Size**: ~287MB
- **Health Check**: /health endpoint
- **User**: Non-root (uid 1000)

**Frontend (todo-frontend:latest)**:
- **Base**: node:20-alpine
- **Build**: Multi-stage build (standalone output)
- **Size**: ~206MB
- **Health Check**: / endpoint
- **User**: Non-root (uid 1001)

### Helm Chart Structure

```
helm/todo-app/
├── Chart.yaml                    # v1.0.0, app v4.0.0
├── values.yaml                   # Production defaults
├── values-dev.yaml               # Minikube overrides
├── values-prod.yaml              # Cloud production (Step 5)
└── templates/
    ├── _helpers.tpl              # Template functions
    ├── NOTES.txt                 # Post-install guide
    ├── backend-deployment.yaml   # Backend Deployment
    ├── backend-service.yaml      # Backend Service
    ├── backend-configmap.yaml    # Backend ConfigMap
    ├── backend-secret.yaml       # Backend Secret
    ├── frontend-deployment.yaml  # Frontend Deployment
    ├── frontend-service.yaml     # Frontend Service
    └── frontend-configmap.yaml   # Frontend ConfigMap
```

### Key Features Implemented

#### ✅ Rolling Updates (Phase 5)
- **Strategy**: maxSurge: 1, maxUnavailable: 0
- **Zero Downtime**: New pod starts before old terminates
- **Configuration Changes**: Tracked via checksums (auto-restart)
- **Tested**: Upgrade + rollback workflows verified

#### ✅ Health Checks (Phase 6)
- **Liveness Probe**: Detects crashed containers, auto-restart
  - Backend: `GET /health` (30s delay, 10s period, 5s timeout, 3 failures)
  - Frontend: `GET /` (30s delay, 10s period, 5s timeout, 3 failures)
- **Readiness Probe**: Controls traffic routing
  - Backend: `GET /health` (10s delay, 5s period, 3s timeout, 2 failures)
  - Frontend: `GET /` (10s delay, 5s period, 3s timeout, 2 failures)

#### ✅ Resource Limits (Phase 6)
- **Backend**: CPU 250m request/500m limit, Memory 256Mi request/512Mi limit
- **Frontend**: CPU 100m request/200m limit, Memory 128Mi request/256Mi limit
- **Enforcement**: Kubernetes throttles (CPU) or kills (memory) on limit

#### ✅ Configuration Management
- **ConfigMaps**: Non-sensitive config (CORS, DB URL, log level)
- **Secrets**: API keys (OpenAI, Better Auth)
- **Environment-Specific**: values-dev.yaml vs values-prod.yaml

### Common Kubernetes Commands

```bash
# Deployment status
kubectl get pods -l app.kubernetes.io/instance=todo-app
kubectl get svc

# Logs
kubectl logs -f -l app.kubernetes.io/component=backend
kubectl logs -f -l app.kubernetes.io/component=frontend

# Health checks
kubectl describe pod -l app.kubernetes.io/component=backend | grep -A 10 "Liveness"

# Resource usage (requires metrics-server)
minikube addons enable metrics-server
kubectl top pods -l app.kubernetes.io/instance=todo-app

# Port forwarding
kubectl port-forward svc/todo-app-backend 8000:8000
kubectl port-forward svc/todo-app-frontend 3000:3000

# Access frontend
minikube service todo-app-frontend  # Opens browser to NodePort

# Helm operations
helm list
helm history todo-app
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
helm rollback todo-app
```

### Troubleshooting

**Pods not starting**:
```bash
kubectl describe pod <pod-name>  # Check events
kubectl logs <pod-name>          # Check logs
```

**Image pull errors**:
```bash
# Ensure Docker environment configured
eval $(minikube docker-env)

# Verify images exist
docker images | grep todo

# Rebuild if needed
docker build -t todo-backend:latest backend/api/
docker build -t todo-frontend:latest frontend/
```

**Health check failures**:
```bash
# Test manually
kubectl port-forward svc/todo-app-backend 8000:8000
curl http://localhost:8000/health
```

### Next Steps (Phase 8)

- [ ] Update documentation (README.md, CLAUDE.md) ✅ IN PROGRESS
- [ ] Create troubleshooting guide
- [ ] Run end-to-end validation
- [ ] Document metrics (resource usage, startup times)
- [ ] Test Helm chart portability
- [ ] Verify all success criteria met

---

**Last Updated**: 2026-01-25 (Step 4 - Phases 5-6 complete: Helm Lifecycle + Health Checks)
