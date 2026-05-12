---
id: 0004
title: Add Step 3 AI Chatbot Principles
stage: constitution
date: 2026-01-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 002-step-2-web-app
user: system
command: /sp.constitution
labels: ["constitution", "step-3", "ai-chatbot", "mcp", "openai-agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - No tests (constitution document)
---

## Prompt

create constituiotn step 3 , and keep existing content unchanged, remaining steps is finishing the step 3 will be starting no mixing allowed, follow the pettern as it's already decleared between step 1 and 2, create a heading for step 3 and start,,, the content is: """ Phase III: Todo AI Chatbot
Basic Level Functionality
Objective: Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture and using Claude Code and Spec-Kit Plus.
💡Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.
Requirements
Implement conversational interface for all Basic Level features
Use OpenAI Agents SDK for AI logic
Build MCP server with Official MCP SDK that exposes task operations as tools
Stateless chat endpoint that persists conversation state to database
AI agents use MCP tools to manage tasks. The MCP tools will also be stateless and will store state in the database.
Technology Stack
Component
Technology
Frontend
OpenAI ChatKit
Backend
Python FastAPI
AI Framework
OpenAI Agents SDK
MCP Server
Official MCP SDK
ORM
SQLModel
Database
Neon Serverless PostgreSQL
Authentication
Better Auth

[Full content provided including architecture, database models, MCP tools specification, agent behavior, conversation flow, natural language commands, deliverables, ChatKit setup, and architecture benefits]
"""

## Response snapshot

Constitution updated to version 3.0.0 with Step 3 (AI-Powered Chatbot) added.

**Major additions**:
- Step 3 Overview and Principles (XIV-XVIII)
- MCP Architecture principle (XIV)
- OpenAI Agents SDK Integration principle (XV)
- Stateless Conversational Architecture principle (XVI)
- Conversational Database Models principle (XVII)
- OpenAI ChatKit Frontend principle (XVIII)
- Complete requirements, technology stack, and constraints
- MCP tools specification (add_task, list_tasks, complete_task, delete_task, update_task)
- Natural language command examples
- Step 3 development workflow
- Step 3 quality gates
- Architecture benefits table

**Pattern consistency**: Followed the same structure established between Step 1 and Step 2:
- Step overview with objective and development approach
- Step-specific principles with Roman numerals (continuing from Step 2)
- Functional and non-functional requirements
- Technology stack table
- Architecture diagram
- API endpoints specification
- Environment variables
- Project structure additions
- Development workflow (Specification → Implementation → Validation)
- Quality gates checklist

**Version bump**: 2.0.0 → 3.0.0 (MAJOR) - Adding Step 3 fundamentally extends project scope with AI-powered natural language interface using OpenAI Agents SDK, MCP server architecture, and conversational state management.

## Outcome

- ✅ Impact: Constitution extended with comprehensive Step 3 guidance for AI-powered chatbot implementation
- 🧪 Tests: No tests (constitution document)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Create Step 3 specification using /sp.specify when ready to start implementation
- 🧠 Reflection: Successfully maintained pattern consistency with Steps 1-2 while adding new AI-specific principles (MCP, OpenAI Agents SDK, stateless architecture)

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution structure and patterns followed correctly
- Graders run and results (PASS/FAIL): PASS - All placeholders filled, version updated, sync impact report created
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): When starting Step 3, verify all principles are implementable with Claude Code + Spec-Kit Plus workflow
