"""
MCP (Model Context Protocol) Server Package

This package contains the MCP server implementation for the Hackathon Todo application.
The MCP server provides standardized tools for AI agents to interact with the task management system.

Architecture:
- server.py: MCP server implementation using FastMCP with 5 tools:
  * todo_add_task: Create new tasks
  * todo_list_tasks: Retrieve tasks with filtering/pagination
  * todo_complete_task: Mark tasks complete/incomplete
  * todo_update_task: Modify task title/description
  * todo_delete_task: Remove tasks permanently

Step 3: AI-Powered Chatbot - MCP Architecture
"""

from .server import mcp

__all__ = ["mcp"]
