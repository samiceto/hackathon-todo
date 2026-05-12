---
id: 0005
title: Implement Phase 2 Foundational
stage: green
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-step-3-ai-chatbot
branch: 003-step-3-ai-chatbot
user: system
command: /sp.implement
labels: ["implementation", "foundational", "database-models", "mcp-server", "agent", "test-infrastructure", "step-3"]
links:
  spec: specs/003-step-3-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/api/src/models/conversation.py
 - backend/api/src/models/message.py
 - backend/api/src/models/user.py
 - backend/api/src/models/__init__.py
 - backend/api/alembic/versions/002_add_conversations_and_messages.py
 - backend/api/src/mcp/server.py
 - backend/api/src/mcp/__init__.py
 - backend/api/src/mcp/tools/__init__.py
 - backend/api/src/agents/task_agent.py
 - backend/api/src/agents/runner.py
 - backend/api/src/agents/__init__.py
 - backend/api/config.py
 - backend/api/tests/conftest.py
 - backend/api/tests/test_utils.py
 - specs/003-step-3-ai-chatbot/tasks.md
tests:
 - Test infrastructure created in conftest.py (fixtures for conversations, messages, MCP tools, agents)
 - Test utilities created in test_utils.py (helper functions for testing)
---

## Prompt

phase 2

## Response snapshot

Implemented Phase 2: Foundational (T009-T017) - Core infrastructure for Step 3 AI-Powered Chatbot.

**Tasks Completed** (9 tasks):

**Database Models (T009-T011)**:

1. **T009**: Created Conversation model (backend/api/src/models/conversation.py)
   - SQLModel with user_id, id, created_at, updated_at
   - Relationships to User and Messages
   - Cascade delete for messages

2. **T010**: Created Message model (backend/api/src/models/message.py)
   - SQLModel with user_id, conversation_id, role, content, created_at
   - MessageRole enum (USER, ASSISTANT)
   - Relationships to User and Conversation
   - Max content length: 10,000 characters

3. **T011**: Created Alembic migration (backend/api/alembic/versions/002_add_conversations_and_messages.py)
   - Conversations table with foreign key to users
   - Messages table with foreign keys to users and conversations
   - Indexes:
     - ix_conversations_user_id
     - ix_conversations_user_id_updated_at (composite, DESC)
     - ix_messages_user_id
     - ix_messages_conversation_id
     - ix_messages_conversation_id_created_at (composite, ASC)

**MCP Server Foundation (T012-T013)**:

4. **T012**: Implemented MCP server (backend/api/src/mcp/server.py)
   - FastMCP server named "todo_mcp"
   - 5 tools with Pydantic validation:
     * todo_add_task: Create new tasks
     * todo_list_tasks: Retrieve tasks with pagination/filtering
     * todo_complete_task: Mark tasks complete/incomplete
     * todo_update_task: Modify task title/description
     * todo_delete_task: Permanently remove tasks
   - Proper tool annotations (readOnlyHint, destructiveHint, idempotentHint)
   - Response formats: JSON and Markdown
   - Database session management

5. **T013**: Created MCP tool utilities (backend/api/src/mcp/tools/__init__.py)
   - get_db_session(): Context manager for database sessions
   - handle_tool_error(): Standardized error formatting
   - format_task_markdown(): Human-readable task formatting
   - format_task_json(): JSON-serializable task formatting
   - verify_task_ownership(): Access control enforcement
   - success_response(), error_response(): Response helpers

**Agent Foundation (T014-T015)**:

6. **T014**: Created task agent (backend/api/src/agents/task_agent.py)
   - TASK_AGENT_INSTRUCTIONS: Comprehensive system prompt
   - create_task_agent(): Standard task agent factory
   - create_agent_with_mcp(): Agent + MCP server connection
   - create_strict_agent(): Deterministic variant
   - create_conversational_agent(): Natural conversation variant
   - MCP integration via MCPServerStreamableHttp
   - Model settings: tool_choice="auto", temperature=0.7

7. **T015**: Created agent runner (backend/api/src/agents/runner.py)
   - run_agent_with_conversation(): Main execution function
     - Loads/creates conversations
     - Retrieves conversation history from database
     - Runs agent with full context
     - Persists user and assistant messages
   - get_conversation_history(): Retrieve conversation for display
   - list_conversations(): List all conversations for user
   - delete_conversation(): Delete conversation and messages

8. **T015 (config)**: Created run-level configuration (backend/api/config.py)
   - OpenAI Agents SDK RunConfig pattern
   - Loads OPENAI_API_KEY from environment
   - AsyncOpenAI client initialization
   - OpenAIChatCompletionsModel configuration
   - Tracing support (TRACING_DISABLED env var)

**Test Infrastructure (T016-T017)**:

9. **T016**: Created test fixtures (backend/api/tests/conftest.py)
   - Database fixtures: engine, session
   - User fixtures: test_user, second_user
   - Task fixtures: test_task, completed_task
   - Conversation fixtures: test_conversation, conversation_with_history
   - Message fixtures: user_message, assistant_message
   - Mock fixtures: mock_mcp_server, mock_agent_response, mock_runner
   - Sample data: sample_task_data, sample_conversations

10. **T017**: Created test utilities (backend/api/tests/test_utils.py)
    - create_test_conversation(): Create test conversations with messages
    - create_test_message(): Create individual test messages
    - mock_agent_result(): Mock agent responses
    - mock_mcp_tool_response(): Mock MCP tool outputs
    - assert_conversation_state(): Validate conversation state
    - assert_message_content(): Validate message content
    - assert_tool_call_made(): Verify tool calls
    - MockMCPTool class: Mock tool for testing

**Updated Files**:
- backend/api/src/models/user.py: Added relationships to conversations and messages
- backend/api/src/models/__init__.py: Exported Conversation, Message, MessageRole
- backend/api/src/mcp/__init__.py: Exported mcp server instance
- backend/api/src/agents/__init__.py: Exported all agent and runner functions
- specs/003-step-3-ai-chatbot/tasks.md: Marked Phase 2 as ✅ COMPLETE

**Next Phase**: Phase 3: User Story 1 - Add Tasks Through Conversation (T018-T033)
- Write tests FIRST (T018-T020)
- Implement MCP tool, agent integration, chat API (T021-T027)
- Build ChatKit frontend (T028-T033)

## Outcome

- ✅ Impact: Complete foundational infrastructure for AI chatbot - database models, MCP server with 5 tools, OpenAI Agents SDK integration, conversation management, test infrastructure
- 🧪 Tests: Test infrastructure created (fixtures and utilities) - ready for TDD in Phase 3
- 📁 Files: 15 files created/modified (3 models, 1 migration, 2 MCP files, 3 agent files, 1 config, 2 test files, 3 package updates, tasks.md)
- 🔁 Next prompts: Proceed to Phase 3 (User Story 1) - MVP functionality for adding tasks conversationally
- 🧠 Reflection: Phase 2 provides complete blocking prerequisites - all user stories can now be implemented independently in parallel. MCP server follows best practices with proper tool naming (todo_*), Pydantic validation, and response formats. Agent uses run-level configuration pattern for flexibility.

## Evaluation notes (flywheel)

- Failure modes observed: None - all implementations follow established patterns from MCP and OpenAI Agents SDK skills
- Graders run and results (PASS/FAIL): PASS - MCP server has 5 tools with proper annotations, agent has comprehensive instructions, test infrastructure complete
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement User Story 1 (T018-T033) to validate conversational task management with add_task functionality
