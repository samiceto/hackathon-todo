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

**Current Status**: Step 1 Complete (Core Todo Features) ✅

**Technology Stack (Step 1)**:
- Python 3.13+ with type hints
- UV package manager
- pytest with pytest-cov (97.44% coverage)
- In-memory storage (migrating to PostgreSQL in Step 2)

**Entry Point**: `uv run hackathon-todo` or `uv run python -m hackathon_todo.main`

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

### src/hackathon_todo/

**__init__.py** (7 lines)
- Package initialization
- Exports main components

**models.py** (99 lines) ✅
- `Task` dataclass with validation
- Fields: id, title, description, completed, created_at
- Type hints for all fields
- Immutable ID and created_at after creation

**storage.py** (209 lines) ✅
- `TaskStorage` class for in-memory CRUD operations
- Methods: add(), get(), get_all(), update(), mark_complete(), delete(), count()
- Sequential ID assignment (auto-increment)
- Error handling for invalid IDs
- Thread-safe for single-process use

**ui.py** (386 lines) ⚠️
- All user interface functions
- Input helpers: get_non_empty_input(), get_task_id(), get_optional_input()
- UI operations: add_task_ui(), view_tasks_ui(), mark_complete_ui(), update_task_ui(), delete_task_ui()
- display_menu() function
- **Note**: Exceeds 300-line guideline; refactoring recommended for Step 2

**main.py** (88 lines) ✅
- Application entry point
- Menu loop with choice routing
- Welcome/goodbye messages
- KeyboardInterrupt (Ctrl+C) handling
- Integrates all 5 user stories

### tests/

**conftest.py**
- pytest fixtures
- TaskStorage fixture with clean state per test

**test_models.py**
- Task dataclass tests
- Validation tests

**test_storage.py**
- CRUD operation tests
- Edge case handling

**test_ui.py**
- UI function tests
- Input validation tests
- Error handling tests

**test_integration.py**
- End-to-end workflow tests
- TestDisplayMenu (1 test)
- TestFullCRUDWorkflow (2 tests)
- TestEdgeCaseWorkflows (3 tests)
- TestDataPersistence (2 tests)
- TestMainFunction (7 tests)

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
# Run all tests with coverage
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
# Primary method
uv run hackathon-todo

# Alternative
uv run python -m hackathon_todo.main

# Run tests
uv run pytest

# Install dependencies
uv sync
```

## Quick Reference

### Important Paths
- **Source**: `src/hackathon_todo/`
- **Tests**: `tests/`
- **Specs**: `specs/001-step-1-core-features/`
- **History**: `history/prompts/001-step-1-core-features/`
- **Constitution**: `.specify/memory/constitution.md`

### Key Files to Reference
- **README.md**: User documentation, quick start guide
- **tasks.md**: Implementation roadmap (41 tasks, Phases 1-9)
- **plan.md**: Architecture decisions and design
- **spec.md**: User stories and acceptance criteria

### Current Branch
- **Name**: `001-step-1-core-features`
- **Status**: Step 1 implementation complete, Phase 9 (polish) in progress

---

**Last Updated**: 2026-01-01 (Phase 9 - Polish & Documentation in progress)
