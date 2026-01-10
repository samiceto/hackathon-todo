---
id: 0003
title: Add Step 2 to Constitution
stage: constitution
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: developer
command: /sp.constitution
labels: ["constitution", "step-2", "full-stack-web-app", "authentication", "database"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document, no tests)
---

## Prompt

now create the constituiton for step 2 under the heading """step 2""" and keep existing content unchanged , and start step 2 after existing content(step 1) is completely finished, dont mix them, the step 2 content is """Phase II: Todo Full-Stack Web Application
Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern multi-user web application with persistent storage.
💡Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.
Requirements
Implement all 5 Basic Level features as a web application
Create RESTful API endpoints
Build responsive frontend interface
Store data in Neon Serverless PostgreSQL database
Authentication – Implement user signup/signin using Better Auth
Technology Stack
Layer
Technology
Frontend
Next.js 16+ (App Router)
Backend
Python FastAPI
ORM
SQLModel
Database
Neon Serverless PostgreSQL
Spec-Driven
Claude Code + Spec-Kit Plus
Authentication
Better Auth

API Endpoints
Method
Endpoint
Description
GET
/api/{user_id}/tasks
List all tasks
POST
/api/{user_id}/tasks
Create a new task
GET
/api/{user_id}/tasks/{id}
Get task details
PUT
/api/{user_id}/tasks/{id}
Update a task
DELETE
/api/{user_id}tasks/{id}
Delete a task
PATCH
/api/{user_id}tasks/{id}/complete
Toggle completion


Securing the REST API
Better Auth + FastAPI Integration
The Challenge
Better Auth is a JavaScript/TypeScript authentication library that runs on your Next.js frontend. However, your FastAPI backend is a separate Python service that needs to verify which user is making API requests.
The Solution: JWT Tokens
Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.
How It Works
User logs in on Frontend → Better Auth creates a session and issues a JWT token
Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
Backend receives request → Extracts token from header, verifies signature using shared secret
Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
Backend filters data → Returns only tasks belonging to that user
What Needs to Change
Component
Changes Required
Better Auth Config
Enable JWT plugin to issue tokens
Frontend API Client
Attach JWT token to every API request header
FastAPI Backend
Add middleware to verify JWT and extract user
API Routes
Filter all queries by the authenticated user's ID

The Shared Secret
Both frontend (Better Auth) and backend (FastAPI) must use the same secret key for JWT signing and verification. This is typically set via environment variable BETTER_AUTH_SECRET in both services.
Security Benefits
Benefit
Description
User Isolation
Each user only sees their own tasks
Stateless Auth
Backend doesn't need to call frontend to verify users
Token Expiry
JWTs expire automatically (e.g., after 7 days)
No Shared DB Session
Frontend and backend can verify auth independently

API Behavior Change
After Auth:
All endpoints require valid JWT token
Requests without token receive 401 Unauthorized
Each user only sees/modifies their own tasks
Task ownership is enforced on every operation

Bottom Line
The REST API endpoints stay the same (GET /api/user_id/tasks, POST /api/user_id/tasks, etc.), but every request now must include a JWT token, and all responses are filtered to only include that user's data.
"""

## Response snapshot

Constitution successfully updated to version 2.0.0 with Step 2 content added.

**Key Changes**:
1. **Version Bump**: 1.0.0 → 2.0.0 (MAJOR)
   - Rationale: Adding Step 2 fundamentally extends project scope from console-only to full-stack web application with authentication, database persistence, and multi-user support

2. **Core Principles (I-VII)**: Unchanged - apply to all steps
   - Spec-Driven Development
   - Iterative Refinement Through AI
   - Clean Architecture & Project Structure (updated monorepo structure)
   - Test-Driven Development
   - Documentation & Traceability
   - Human as Tool Strategy
   - Security & Best Practices

3. **Step 1 Section**: Preserved completely
   - Console app requirements
   - Technology constraints (Python, UV)
   - In-memory storage pattern
   - Console UX standards
   - Development workflow
   - Quality gates

4. **Step 2 Section**: Added comprehensive new content
   - **New Principles (VIII-XIII)**:
     - VIII. Multi-User Architecture (data isolation, authentication)
     - IX. RESTful API Design (6 required endpoints)
     - X. Database Persistence (Neon PostgreSQL, SQLModel)
     - XI. Frontend-Backend Separation (Next.js + FastAPI)
     - XII. JWT Authentication Flow (Better Auth + JWT)
     - XIII. Responsive UI Design (mobile + desktop)

   - **Technology Stack**:
     - Frontend: Next.js 16+ (App Router)
     - Backend: Python FastAPI
     - ORM: SQLModel
     - Database: Neon Serverless PostgreSQL
     - Authentication: Better Auth + JWT

   - **API Endpoints** (all require JWT):
     - GET /api/{user_id}/tasks
     - POST /api/{user_id}/tasks
     - GET /api/{user_id}/tasks/{id}
     - PUT /api/{user_id}/tasks/{id}
     - DELETE /api/{user_id}/tasks/{id}
     - PATCH /api/{user_id}/tasks/{id}/complete

   - **Project Structure**: Monorepo with backend/console (Step 1) and backend/api + frontend (Step 2)

   - **Environment Variables**: Documented for both frontend and backend

   - **Development Workflow**: 6-phase implementation (Database → Backend API → Frontend Auth → Frontend UI → Integration Testing → Documentation)

   - **Quality Gates**: 12 checkpoints before Step 3

**Sync Impact Report**:
- ✅ Constitution updated to v2.0.0
- ⚠ Templates (plan, spec, tasks) - No changes required (structure supports both steps)
- ⚠ Follow-up: Step 2 specifications will be created when starting Step 2 work

**File Modified**:
- .specify/memory/constitution.md (complete rewrite with Step 1 + Step 2)

## Outcome

- ✅ Impact: Constitution successfully expanded from Step 1-only to include comprehensive Step 2 requirements while preserving all Step 1 content unchanged
- 🧪 Tests: N/A (constitution document)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Ready to create Step 2 specifications using /sp.specify when user begins Step 2 work
- 🧠 Reflection: Major version bump appropriate due to significant scope expansion. JWT authentication architecture clearly documented. Monorepo structure supports both steps. Templates remain compatible with both steps.

## Evaluation notes (flywheel)

- Failure modes observed: None - user provided clear, structured requirements for Step 2
- Graders run and results (PASS/FAIL):
  - ✅ PASS: All Step 1 content preserved unchanged
  - ✅ PASS: Step 2 content clearly separated and added after Step 1
  - ✅ PASS: Version bumped to 2.0.0 (MAJOR) with clear rationale
  - ✅ PASS: Sync Impact Report included in constitution file
  - ✅ PASS: No unresolved placeholder tokens
  - ✅ PASS: Templates validated (no changes required)
- Prompt variant (if applicable): Standard constitution amendment
- Next experiment (smallest change to try): When user starts Step 2, create `/sp.specify` for "002-step-2-web-app" feature
