---
id: 0002
title: Create Step 2 Implementation Plan
stage: plan
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5
feature: 002-step-2-web-app
branch: 002-step-2-web-app
user: developer
command: /sp.plan
labels: ["plan", "step-2", "architecture", "full-stack", "research", "contracts"]
links:
  spec: specs/002-step-2-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-step-2-web-app/plan.md
  - specs/002-step-2-web-app/design/research.md
  - specs/002-step-2-web-app/design/data-model.md
  - specs/002-step-2-web-app/design/quickstart.md
  - specs/002-step-2-web-app/contracts/api-endpoints.md
  - specs/002-step-2-web-app/contracts/auth-flow.md
tests:
  - N/A (planning documents, test strategies defined)
---

## Prompt

go for planing , the credentials are DATABASE_URL='postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

BETTER_AUTH_SECRET=uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC
BETTER_AUTH_URL="http://localhost:3000" if you need anything else ask me to provide.

## Response snapshot

Created comprehensive Step 2 implementation plan with complete architecture design, technology research, and setup documentation.

**Main Plan** (plan.md):
- **Summary**: Transform console app to full-stack web application with Next.js + FastAPI + PostgreSQL
- **Technical Context**: Backend (Python 3.13+, FastAPI), Frontend (TypeScript 5+, Next.js 16+)
- **Constitution Check**: ✅ All 13 Step 2 principles satisfied (VIII-XIII + I-VII)
- **Project Structure**: Detailed file tree for backend/api and frontend with 50+ files planned
- **Complexity Tracking**: No violations - all requirements align with constitution

**Phase 0: Research** (design/research.md):
Five critical technology decisions researched:

1. **Better Auth + FastAPI JWT Integration**
   - Decision: Better Auth issues JWT on frontend, FastAPI verifies on backend
   - Rationale: Stateless auth, horizontal scaling, industry standard
   - Implementation: PyJWT with shared BETTER_AUTH_SECRET

2. **SQLModel Multi-User Data Isolation**
   - Decision: user_id foreign key + explicit query filtering
   - Rationale: Simple, performant, database integrity
   - Index strategy: Primary (id), Secondary (user_id), Composite (user_id, created_at)

3. **Neon PostgreSQL Connection Pooling**
   - Decision: Use Neon's pooler URL + SQLAlchemy QueuePool
   - Configuration: pool_size=5, max_overflow=10, pool_pre_ping=True
   - Rationale: Managed pooling + local optimization

4. **FastAPI CORS Configuration**
   - Decision: Specific origins only (no wildcard), credentials enabled
   - Development: http://localhost:3000
   - Security: Never use `*` with credentials

5. **Next.js 16 App Router Authentication State**
   - Decision: Better Auth hooks + httpOnly cookies
   - Rationale: XSS-resistant, excellent DX
   - Storage: httpOnly cookies (not localStorage)

**Phase 1: Design**:

**Data Model** (design/data-model.md):
- **User Entity**: id, email (unique), hashed_password, timestamps
- **Task Entity**: id, user_id (FK), title, description, completed, timestamps
- **Relationship**: One-to-many (User → Tasks, cascade delete)
- **Validation**: Email format, password min 8 chars, title required (1-500 chars)
- **Security**: Passwords hashed with bcrypt, no sensitive data in responses
- **Performance**: Indexes on users.email, tasks.user_id, tasks(user_id, created_at)

**API Contracts** (contracts/api-endpoints.md):
Eight endpoints documented with full request/response schemas:

**Authentication** (public):
- POST /api/auth/signup - Create account, returns user + JWT
- POST /api/auth/signin - Login, returns user + JWT

**Tasks** (JWT required, user_id must match token):
- GET /api/{user_id}/tasks - List all user's tasks
- POST /api/{user_id}/tasks - Create new task
- GET /api/{user_id}/tasks/{id} - Get single task
- PUT /api/{user_id}/tasks/{id} - Update task
- DELETE /api/{user_id}/tasks/{id} - Delete task
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion

Each endpoint includes:
- Request/response TypeScript schemas
- Success responses (200/201/204)
- Error responses (400/401/403/404/409/422)
- Security notes
- Example curl commands

**Authentication Flow** (contracts/auth-flow.md):
Five detailed flow diagrams:
1. User Signup (11 steps from form to redirect)
2. User Signin (10 steps with password verification)
3. Authenticated API Request (10 steps with JWT validation)
4. User Signout (client-side token deletion)
5. Expired Token (error handling and redirect)

**Security measures documented**:
- Password hashing (bcrypt, 12 rounds)
- JWT security (HS256, 32-char secret, 7-day expiration)
- Token storage (httpOnly cookies recommended)
- CORS configuration (specific origins only)

**Setup Guide** (design/quickstart.md):
Complete step-by-step setup:
- Prerequisites (Python 3.13+, UV, Node 20+, Git)
- Backend setup (4 steps): env vars, dependencies, DB init, run server
- Frontend setup (4 steps): env vars, dependencies, run dev server
- Verification (end-to-end test flow with 7 steps)
- Testing instructions (backend pytest, frontend Jest/Playwright)
- Common issues (5 problems with solutions)
- Environment variables reference (2 tables)
- Database management commands

**Project Structure**:
- **Backend**: backend/api with src/(models, schemas, api, services, db), tests, alembic
- **Frontend**: frontend with src/(app, components, lib), tests/(unit, e2e)
- **Specs**: research, data-model, contracts, quickstart all created
- **Monorepo**: backend/console preserved (Step 1 unchanged)

## Outcome

- ✅ Impact: Complete implementation plan created with architecture design, technology research, data models, API contracts, authentication flows, and setup instructions for full-stack web application
- 🧪 Tests: Test strategies defined (pytest for backend, Jest/RTL/Playwright for frontend, target >90% coverage)
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, api-endpoints.md, auth-flow.md)
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown based on this plan
- 🧠 Reflection: Architecture balances spec requirements with constitution mandates. JWT integration well-defined. Database credentials incorporated securely. All Step 2 principles (VIII-XIII) satisfied with clear implementation patterns.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan is comprehensive and actionable
- Graders run and results (PASS/FAIL):
  - ✅ PASS: All 13 Step 2 constitution principles satisfied (VIII-XIII + I-VII)
  - ✅ PASS: Technical context fully specified (no NEEDS CLARIFICATION markers)
  - ✅ PASS: Project structure detailed (backend/api + frontend with 50+ files)
  - ✅ PASS: Research complete (5 technology decisions with rationale)
  - ✅ PASS: Data model complete (User + Task entities, validation, indexes)
  - ✅ PASS: API contracts complete (8 endpoints with full schemas)
  - ✅ PASS: Auth flow complete (5 sequence diagrams, security measures)
  - ✅ PASS: Quickstart guide complete (setup, testing, troubleshooting)
  - ✅ PASS: Database credentials incorporated securely (env vars, not hardcoded)
  - ✅ PASS: Backward compatibility ensured (backend/console preserved)
- Prompt variant (if applicable): Standard /sp.plan with user-provided credentials
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to break down implementation into actionable tasks organized by user story priority
