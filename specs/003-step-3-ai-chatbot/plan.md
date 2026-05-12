# Implementation Plan: AI-Powered Chatbot for Task Management

**Branch**: `003-step-3-ai-chatbot` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-step-3-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create an AI-powered chatbot interface that allows users to manage their todo tasks through natural language conversations. The system uses OpenAI Agents SDK for natural language understanding, MCP (Model Context Protocol) server for standardized tool operations, and maintains stateless architecture with database-backed conversation persistence. Users can add, view, complete, update, and delete tasks by chatting with an AI agent that understands conversational commands.

**Technical Approach**:
- Build MCP server with 5 stateless tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Integrate OpenAI Agents SDK to process natural language and invoke MCP tools
- Implement stateless chat endpoint that fetches conversation history from database on each request
- Add Conversation and Message database models using SQLModel
- Use OpenAI ChatKit for frontend chat UI
- Extend existing FastAPI backend from Step 2 with chat capabilities
- Maintain user authentication and data isolation from Step 2

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, Neon PostgreSQL client
- Frontend: OpenAI ChatKit, Next.js 16+, Better Auth (existing)
**Storage**: Neon Serverless PostgreSQL (existing from Step 2, adding Conversation and Message tables)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Linux server (backend), Web browsers (frontend)
**Project Type**: Web application (existing monorepo with backend/frontend separation)
**Performance Goals**:
- Chat response time <3 seconds (p95) including AI processing
- MCP tool execution <500ms (p95)
- Conversation history retrieval <200ms
- Support 100 concurrent conversations
**Constraints**:
- Stateless backend architecture (no in-memory state)
- All conversation state must persist in database
- Users can only access their own tasks and conversations
- MCP tools must be stateless and database-backed
**Scale/Scope**:
- Support multi-user conversations (100+ concurrent users)
- Conversation history up to 50 messages per conversation
- Natural language understanding for 8+ command variations per operation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Step 3 Constitutional Requirements

#### XIV. Model Context Protocol (MCP) Architecture ✅
- [x] MCP server built using Official MCP SDK
- [x] Five MCP tools exposed: add_task, list_tasks, complete_task, delete_task, update_task
- [x] Tools are stateless and store state in database
- [x] Tools have clear purpose, parameters, return values, and examples (documented in spec)
- [x] Tools enforce user authentication and data isolation

#### XV. OpenAI Agents SDK Integration ✅
- [x] OpenAI Agents SDK used for AI logic
- [x] Agent configured with MCP tools available for invocation
- [x] Runner executes agent with conversation history context
- [x] Agent understands natural language commands and maps to tools
- [x] Agent provides friendly confirmations after tool invocations
- [x] Graceful error handling with user-friendly messages

#### XVI. Stateless Conversational Architecture ✅
- [x] Chat endpoint is stateless
- [x] Conversation state persists to database (not in-memory)
- [x] Each request fetches conversation history from database
- [x] Each response stores new messages to database
- [x] Conversation context built fresh on every request
- [x] Server holds no state between requests

#### XVII. Conversational Database Models ✅
- [x] Conversation model: user_id, id, created_at, updated_at
- [x] Message model: user_id, id, conversation_id, role, content, created_at
- [x] Conversations belong to users (foreign key)
- [x] Messages belong to conversations (foreign key)
- [x] Messages have role: "user" or "assistant"
- [x] Proper indexes on foreign keys

#### XVIII. OpenAI ChatKit Frontend ✅
- [x] OpenAI ChatKit used for chat UI
- [x] ChatKit configured with domain allowlist (for production deployment)
- [x] Chat UI sends messages to `/api/{user_id}/chat` endpoint
- [x] Frontend displays conversation history
- [x] Frontend shows tool invocations (optional - planned for transparency)

### Core Principles Compliance (Steps 1-2 Inherited)

#### I. Spec-Driven Development ✅
- [x] Complete specification exists in spec.md
- [x] All requirements defined before implementation
- [x] Claude Code will generate all implementation
- [x] No manual coding allowed

#### III. Clean Architecture ✅
- [x] Clear separation: models, services, MCP tools, API endpoints, frontend
- [x] No circular dependencies
- [x] Layered architecture maintained

#### IV. Test-Driven Development ✅
- [x] Tests will be written before implementation
- [x] Minimum coverage: >90% for new code
- [x] All functional requirements have test scenarios

#### VII. Security & Best Practices ✅
- [x] User authentication enforced (Better Auth from Step 2)
- [x] Data isolation (users only see their own conversations/tasks)
- [x] Input validation at all boundaries
- [x] No hardcoded secrets (environment variables)
- [x] Protection against prompt injection and tool misuse

### Gate Status: ✅ PASS

All constitutional requirements are met by the planned architecture. No violations or complexity justifications needed.

## Project Structure

### Documentation (this feature)

```text
specs/003-step-3-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── checklists/
│   └── requirements.md  # Spec quality checklist (already created)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── mcp-tools.md     # MCP tool specifications
│   ├── chat-api.md      # Chat endpoint contract
│   └── agent-config.md  # Agent configuration and behavior
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application (backend + frontend monorepo - extends Step 2)

backend/
├── console/             # Step 1 - Console app (preserved)
└── api/                 # Step 2 - FastAPI backend (EXTENDED for Step 3)
    ├── src/
    │   ├── models/      # SQLModel models
    │   │   ├── task.py          # Existing from Step 2
    │   │   ├── user.py          # Existing from Step 2
    │   │   ├── conversation.py  # NEW for Step 3
    │   │   └── message.py       # NEW for Step 3
    │   ├── services/    # Business logic
    │   │   └── task_service.py  # Existing from Step 2
    │   ├── api/         # FastAPI routes
    │   │   ├── tasks.py         # Existing from Step 2
    │   │   └── chat.py          # NEW for Step 3
    │   ├── auth/        # JWT verification (existing from Step 2)
    │   ├── mcp/         # NEW for Step 3
    │   │   ├── server.py        # MCP server implementation
    │   │   ├── tools/
    │   │   │   ├── add_task.py
    │   │   │   ├── list_tasks.py
    │   │   │   ├── complete_task.py
    │   │   │   ├── delete_task.py
    │   │   │   └── update_task.py
    │   │   └── __init__.py
    │   └── agents/      # NEW for Step 3
    │       ├── task_agent.py    # OpenAI Agents SDK configuration
    │       ├── runner.py        # Agent runner with conversation context
    │       └── __init__.py
    ├── tests/
    │   ├── test_models.py       # Existing from Step 2
    │   ├── test_tasks_api.py    # Existing from Step 2
    │   ├── test_conversation.py # NEW for Step 3
    │   ├── test_message.py      # NEW for Step 3
    │   ├── test_mcp_tools.py    # NEW for Step 3
    │   ├── test_agent.py        # NEW for Step 3
    │   └── test_chat_api.py     # NEW for Step 3
    ├── alembic/         # Database migrations (existing from Step 2)
    │   └── versions/
    │       └── xxx_add_conversations.py  # NEW migration for Step 3
    ├── .env.example     # Environment variables template (UPDATED)
    └── pyproject.toml   # Python project config (UPDATED with new deps)

frontend/                # Step 2 - Next.js frontend (EXTENDED for Step 3)
├── src/
│   ├── app/
│   │   ├── tasks/       # Existing from Step 2
│   │   ├── auth/        # Existing from Step 2
│   │   └── chat/        # NEW for Step 3
│   │       ├── page.tsx          # Chat interface main page
│   │       └── [id]/page.tsx     # Specific conversation view
│   ├── components/
│   │   ├── tasks/       # Existing from Step 2
│   │   ├── auth/        # Existing from Step 2
│   │   └── chat/        # NEW for Step 3
│   │       ├── ChatInterface.tsx
│   │       ├── MessageList.tsx
│   │       ├── MessageInput.tsx
│   │       └── ConversationHistory.tsx
│   ├── lib/
│   │   ├── api-client.ts        # Existing from Step 2
│   │   ├── auth-config.ts       # Existing from Step 2 (Better Auth)
│   │   └── chatkit-config.ts    # NEW for Step 3
│   └── styles/          # Tailwind CSS (existing from Step 2)
└── tests/
    ├── components/
    │   └── chat/        # NEW for Step 3
    └── integration/
        └── chat.test.tsx # NEW for Step 3

specs/
├── 001-step-1-core-features/  # Step 1 (complete)
├── 002-step-2-web-app/        # Step 2 (complete/in-progress)
└── 003-step-3-ai-chatbot/     # Step 3 (this feature)

history/prompts/
├── 001-step-1-core-features/  # Step 1 PHRs
├── 002-step-2-web-app/        # Step 2 PHRs
└── 003-step-3-ai-chatbot/     # Step 3 PHRs
```

**Structure Decision**: Extending existing web application monorepo from Step 2. The backend/api directory will be extended with new MCP and agents modules. The frontend will add chat interface components using OpenAI ChatKit. This approach maintains consistency with Steps 1-2 while adding AI capabilities as a new layer on top of existing task management infrastructure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional requirements are met by the planned architecture.

---

## Phase 0: Research & Technical Decisions

**Status**: To be completed by research agents

### Research Tasks

1. **OpenAI Agents SDK Integration Patterns**
   - Question: What is the recommended pattern for integrating OpenAI Agents SDK with FastAPI?
   - Question: How to configure agents with external tools (MCP)?
   - Question: How to manage conversation history with OpenAI Agents SDK?
   - Output: Integration architecture and code patterns

2. **MCP Server Implementation**
   - Question: How to implement MCP server using Official MCP SDK in Python?
   - Question: What is the protocol for tool registration and invocation?
   - Question: How to make MCP tools stateless with database backing?
   - Output: MCP server architecture and implementation approach

3. **OpenAI ChatKit Setup**
   - Question: How to configure OpenAI ChatKit in Next.js 16+ (App Router)?
   - Question: What is the domain allowlist configuration process?
   - Question: How to connect ChatKit to custom backend API?
   - Output: ChatKit integration guide and configuration

4. **Stateless Conversation Architecture**
   - Question: Best practices for stateless chat endpoints with conversation history?
   - Question: How to efficiently load and filter conversation history from database?
   - Question: Optimal database schema for conversation persistence?
   - Output: Architecture patterns and performance optimization strategies

5. **Agent Behavior and Prompt Engineering**
   - Question: How to configure agent system prompts for task management operations?
   - Question: Best practices for natural language to tool mapping?
   - Question: How to handle ambiguous requests and clarifications?
   - Output: Agent configuration and prompt templates

6. **Security and Prompt Injection Prevention**
   - Question: How to prevent prompt injection attacks in conversational AI?
   - Question: Best practices for validating tool invocations?
   - Question: How to ensure data isolation in multi-user AI applications?
   - Output: Security guidelines and validation patterns

### Technology Decisions to Document

1. **MCP Tool Implementation Approach**
   - Decision: [To be determined from research]
   - Alternatives: Direct API calls vs MCP abstraction
   - Rationale: [Based on Official MCP SDK capabilities]

2. **Agent Conversation Context Strategy**
   - Decision: [To be determined from research]
   - Alternatives: Full history vs sliding window vs summarization
   - Rationale: [Based on performance and accuracy tradeoffs]

3. **ChatKit Deployment Configuration**
   - Decision: [To be determined from research]
   - Alternatives: Hosted ChatKit vs self-hosted components
   - Rationale: [Based on domain allowlist requirements]

4. **Error Handling and Fallback Strategy**
   - Decision: [To be determined from research]
   - Alternatives: Retry logic, fallback responses, escalation to human
   - Rationale: [Based on user experience requirements]

**Research Output**: `research.md` will be generated by research agents to resolve all questions above.

---

## Phase 1: Design & Contracts

**Status**: To be completed after Phase 0 research

### Data Model Design

**Output**: `data-model.md`

#### New Entities for Step 3

1. **Conversation**
   - Fields: id (UUID), user_id (FK to User), created_at, updated_at
   - Relationships: belongs_to User, has_many Messages
   - Validation: user_id required
   - Indexes: user_id, created_at DESC

2. **Message**
   - Fields: id (UUID), user_id (FK to User), conversation_id (FK to Conversation), role (enum: user/assistant), content (text), created_at
   - Relationships: belongs_to User, belongs_to Conversation
   - Validation: role must be "user" or "assistant", content required
   - Indexes: conversation_id, created_at ASC

3. **Task** (Existing from Step 2 - no changes)
   - Fields: id (UUID), user_id (FK to User), title, description, completed, created_at, updated_at
   - Note: Already implemented in Step 2

#### Database Migration

- Migration: Add conversations and messages tables
- Indexes: Foreign keys (user_id, conversation_id) and timestamp fields
- Constraints: NOT NULL on required fields, CHECK constraint on role enum

### API Contracts

**Output**: `contracts/` directory with detailed specifications

#### 1. MCP Tools Contract (`contracts/mcp-tools.md`)

Each tool specification includes:
- Tool name
- Purpose
- Input schema (parameters with types and constraints)
- Output schema (return values)
- Error conditions
- Example invocations

Tools:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task

#### 2. Chat API Contract (`contracts/chat-api.md`)

**Endpoint**: POST `/api/{user_id}/chat`

**Request**:
```json
{
  "conversation_id": "uuid-optional",
  "message": "string-required"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "response": "string",
  "tool_calls": [
    {
      "tool": "string",
      "parameters": {},
      "result": {}
    }
  ]
}
```

**Error Responses**:
- 401: Unauthorized (invalid or missing JWT)
- 400: Bad Request (invalid message format)
- 404: Conversation not found (if conversation_id provided but doesn't exist)
- 500: Internal Server Error (agent or tool failure)

#### 3. Agent Configuration Contract (`contracts/agent-config.md`)

- Agent system prompt template
- Tool descriptions for agent
- Conversation history format
- Response format expectations
- Error handling strategies

### Quickstart Guide

**Output**: `quickstart.md`

#### Setup Steps

1. **Environment Configuration**
   - Add OPENAI_API_KEY to backend/.env
   - Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY to frontend/.env.local
   - Configure MCP_SERVER_URL if running separately

2. **Database Migration**
   - Run Alembic migration to add conversations and messages tables
   - Verify indexes created

3. **Backend Setup**
   - Install new dependencies: openai-agents-sdk, mcp-sdk
   - Run backend server: `cd backend/api && uv run uvicorn main:app`

4. **Frontend Setup**
   - Install OpenAI ChatKit: `npm install @openai/chatkit`
   - Configure ChatKit with API endpoint and domain key
   - Run frontend: `cd frontend && npm run dev`

5. **Testing the Integration**
   - Create a test user and authenticate
   - Navigate to /chat
   - Send test messages: "Add a task to buy groceries", "Show me all tasks"
   - Verify agent responds and invokes MCP tools correctly

#### Development Workflow

1. Start backend API server
2. Start frontend dev server
3. Open browser to http://localhost:3000/chat
4. Test natural language commands
5. Check backend logs for MCP tool invocations
6. Verify database updates for conversations and tasks

### Agent Context Update

After completing Phase 1 design, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update CLAUDE.md with:
- New Step 3 modules (mcp/, agents/)
- New database models (Conversation, Message)
- New API endpoint (/chat)
- OpenAI Agents SDK and MCP SDK references
- ChatKit frontend integration notes

---

## Phase 2: Task Breakdown

**Status**: NOT created by /sp.plan - requires separate `/sp.tasks` command

The `/sp.tasks` command will generate `tasks.md` with:
- Testable tasks for each phase
- Dependencies between tasks
- Acceptance criteria for each task
- Estimated complexity
- Test specifications

**Expected Phases in tasks.md**:
1. Setup: Database migrations, environment configuration
2. MCP Server: Implement 5 tools with tests
3. Agent Integration: OpenAI Agents SDK setup and configuration
4. Chat API: Stateless endpoint with conversation persistence
5. ChatKit Frontend: UI components and integration
6. Integration Testing: End-to-end conversation flows
7. Documentation: README updates, deployment guides

---

## Notes

### Dependencies on Step 2

Step 3 builds directly on Step 2 infrastructure:
- ✅ FastAPI backend (extends with /chat endpoint)
- ✅ Neon PostgreSQL database (adds Conversation and Message tables)
- ✅ SQLModel ORM (adds new models)
- ✅ Better Auth + JWT authentication (reuses for chat endpoint)
- ✅ Next.js frontend (adds chat interface)
- ✅ User model and authentication (enforces data isolation)

**Assumption**: Step 2 is complete and functional before starting Step 3 implementation.

### Open Questions for User

Based on the user's request to "include in plans if workflow id needed ask me to provide, or anything else":

1. **Workflow ID**: Do you have a specific GitHub Actions workflow ID or CI/CD pipeline configuration that should be documented in the plan? (If yes, please provide the workflow file path or configuration)

2. **OpenAI API Key**: Do you already have an OpenAI API key for development/testing, or should the plan include instructions for obtaining one?

3. **ChatKit Domain Allowlist**: Do you have a production domain already, or will this be deployed after local development is complete?

4. **MCP Server Deployment**: Should the MCP server run as part of the FastAPI application (same process) or as a separate service? (Recommend: same process for simplicity in Step 3)

5. **Conversation History Limits**: Should there be automatic cleanup or archival of old conversations (e.g., delete after 30 days)? Or keep all conversations indefinitely?

**Note**: These are optional clarifications. The plan can proceed with reasonable defaults if not specified:
- Default: No CI/CD workflow documentation (can be added later)
- Default: User will provide OpenAI API key during setup
- Default: Start with localhost, configure domain allowlist when deploying
- Default: MCP server runs in same FastAPI process
- Default: Keep all conversations indefinitely (no automatic cleanup)

### Next Steps

1. **Research Phase**: Run research agents to resolve technical questions in Phase 0
2. **Design Phase**: Generate data-model.md, contracts/, and quickstart.md
3. **Task Generation**: Run `/sp.tasks` to create detailed task breakdown
4. **Implementation**: Run `/sp.implement` to execute tasks via Claude Code

**Current Status**: Plan complete, ready for Phase 0 research.
