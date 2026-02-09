"""
OpenAI Agents Package

This package contains the OpenAI Agents SDK integration for conversational task management.

Architecture:
- task_agent.py: Task management agent with MCP integration
  * create_task_agent(): Standard task agent
  * create_agent_with_mcp(): Agent + MCP server connection
  * create_strict_agent(): Deterministic tool usage variant
  * create_conversational_agent(): Natural conversation variant

Step 3: AI-Powered Chatbot - OpenAI Agents SDK Integration
"""

from .task_agent import (
    create_task_agent,
    create_agent_with_mcp,
    create_strict_agent,
    create_conversational_agent,
    TASK_AGENT_INSTRUCTIONS
)

from .runner import (
    run_agent_with_conversation,
    get_conversation_history,
    list_conversations,
    delete_conversation
)

__all__ = [
    # Agent creation functions
    "create_task_agent",
    "create_agent_with_mcp",
    "create_strict_agent",
    "create_conversational_agent",
    "TASK_AGENT_INSTRUCTIONS",
    # Runner functions
    "run_agent_with_conversation",
    "get_conversation_history",
    "list_conversations",
    "delete_conversation"
]
