---
id: 0002
title: Create Step 3 Implementation Plan
stage: plan
date: 2026-01-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-step-3-ai-chatbot
branch: 003-step-3-ai-chatbot
user: system
command: /sp.plan
labels: ["plan", "step-3", "ai-chatbot", "mcp", "openai-agents", "architecture"]
links:
  spec: specs/003-step-3-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-step-3-ai-chatbot/plan.md
tests:
 - No tests (planning document)
---

## Prompt

now create plan.md file for step 3 , and also include in plans if workflow id needed ask me to provide, or anything else,

## Response snapshot

Created comprehensive implementation plan for Step 3 AI-Powered Chatbot feature following SDD principles.

**Plan Structure**:

**Summary**: AI chatbot for task management using OpenAI Agents SDK + MCP server + stateless architecture

**Technical Context**:
- Languages: Python 3.13+ (backend), TypeScript/Next.js 16+ (frontend)
- Dependencies: OpenAI Agents SDK, Official MCP SDK, FastAPI, ChatKit, SQLModel
- Storage: Neon PostgreSQL (extends Step 2 with Conversation and Message tables)
- Performance: <3s response time, <500ms tool execution, 100 concurrent users
- Architecture: Stateless backend with database-backed conversation persistence

**Constitution Check**: ✅ PASS
- All Step 3 principles (XIV-XVIII) validated
- MCP Architecture, OpenAI Agents SDK, Stateless Architecture, Database Models, ChatKit Frontend
- Core principles inherited from Steps 1-2 (SDD, Clean Architecture, TDD, Security)
- Zero violations - no complexity justifications needed

**Project Structure**:
- Extends existing monorepo from Step 2
- Backend: New mcp/ and agents/ modules in backend/api/src/
- Frontend: New chat/ components and pages in frontend/src/
- Database: New Conversation and Message models
- Tests: New test files for MCP tools, agent, and chat API

**Phase 0 - Research** (6 research tasks):
1. OpenAI Agents SDK integration patterns with FastAPI
2. MCP server implementation using Official MCP SDK
3. OpenAI ChatKit setup in Next.js 16+ (App Router)
4. Stateless conversation architecture best practices
5. Agent behavior and prompt engineering for task management
6. Security and prompt injection prevention

**Phase 1 - Design & Contracts**:
- Data Model: Conversation and Message entities (data-model.md)
- API Contracts: MCP tools, chat endpoint, agent config (contracts/)
- Quickstart: Setup and development workflow (quickstart.md)

**Phase 2 - Task Breakdown**:
- Not created by /sp.plan - requires separate /sp.tasks command
- Expected phases: Setup, MCP Server, Agent Integration, Chat API, ChatKit Frontend, Integration Testing, Documentation

**Open Questions for User** (5 questions):
1. Workflow ID: GitHub Actions workflow ID or CI/CD configuration?
2. OpenAI API Key: Already have one or need instructions?
3. ChatKit Domain Allowlist: Production domain or deploy later?
4. MCP Server Deployment: Same FastAPI process (recommended) or separate service?
5. Conversation History Limits: Keep indefinitely or automatic cleanup?

**Defaults Provided**: Can proceed with reasonable defaults if not specified

## Outcome

- ✅ Impact: Complete implementation plan for Step 3 with architecture, research tasks, and design phases
- 🧪 Tests: No tests (planning document)
- 📁 Files: 1 file created (plan.md - 516 lines)
- 🔁 Next prompts: Phase 0 research (resolve technical questions), then Phase 1 design (data-model.md, contracts/), then /sp.tasks for task breakdown
- 🧠 Reflection: Plan successfully extends Step 2 architecture with AI capabilities while maintaining constitutional compliance and clean architecture principles

## Evaluation notes (flywheel)

- Failure modes observed: None - plan structure comprehensive and constitutional requirements validated
- Graders run and results (PASS/FAIL): PASS - Constitution Check gates passed, all Step 3 principles addressed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run Phase 0 research to resolve technical questions about OpenAI Agents SDK, MCP SDK, and ChatKit integration patterns
