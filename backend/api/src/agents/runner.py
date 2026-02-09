"""
Agent Runner for Task Management Conversations.

This module provides utilities to run the task management agent with conversation
history management, including loading previous messages, running the agent, and
persisting new messages to the database.

Step 3: AI-Powered Chatbot - Agent Runner
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select

from agents import Runner
from agents.run import RunConfig

from ..models import Conversation, Message, MessageRole
from ..db import get_session
from .task_agent import create_agent_with_mcp


async def run_agent_with_conversation(
    user_id: int,
    user_message: str,
    conversation_id: Optional[int] = None,
    config: Optional[RunConfig] = None,
    mcp_server_url: str = "http://localhost:8000/mcp",
    max_history: int = 50
) -> Dict[str, Any]:
    """Run the task agent with conversation context and persist messages.

    This function:
    1. Loads or creates a conversation
    2. Retrieves conversation history from database
    3. Runs the agent with full context
    4. Persists user message and agent response
    5. Returns the response with conversation metadata

    Args:
        user_id (int): User ID for task operations and conversation ownership
        user_message (str): User's input message
        conversation_id (Optional[int]): Existing conversation ID (None creates new)
        config (Optional[RunConfig]): Agent run configuration (from config.py)
        mcp_server_url (str): MCP server URL (default: localhost)
        max_history (int): Maximum messages to include in context (default: 50)

    Returns:
        Dict[str, Any]: Response containing:
            - conversation_id (int): Conversation ID
            - user_message_id (int): Saved user message ID
            - assistant_message_id (int): Saved assistant message ID
            - response (str): Agent's response text
            - tool_calls (List): Tools called during execution
            - created_at (str): Response timestamp

    Example:
        from config import config

        result = await run_agent_with_conversation(
            user_id=1,
            user_message="Add a task to buy groceries",
            config=config
        )

        print(f"Response: {result['response']}")
        print(f"Conversation ID: {result['conversation_id']}")
    """
    # Get database session
    session: Session = next(get_session())

    try:
        # Load or create conversation
        if conversation_id:
            conversation = session.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError(f"Conversation {conversation_id} not found or access denied")
        else:
            # Create new conversation
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Load conversation history (most recent max_history messages)
        history_messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(max_history)
        ).all()

        # Reverse to chronological order
        history_messages = list(reversed(history_messages))

        # Format history for agent context
        formatted_history = [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in history_messages
        ]

        # Save user message
        user_msg = Message(
            user_id=user_id,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=user_message,
            created_at=datetime.utcnow()
        )
        session.add(user_msg)
        session.commit()
        session.refresh(user_msg)

        # Create agent and MCP server
        agent, mcp_server = await create_agent_with_mcp(mcp_server_url=mcp_server_url)

        # Run agent with conversation context
        async with mcp_server:
            # Build full input with history
            if formatted_history:
                # Include history as context
                full_input = "\n".join([
                    f"[Previous conversation]",
                    *[f"{msg['role']}: {msg['content']}" for msg in formatted_history[-10:]],  # Last 10 messages
                    f"[Current message]",
                    f"user: {user_message}"
                ])
            else:
                full_input = user_message

            # Inject user_id into context for MCP tools
            context = {"user_id": user_id}

            # Run agent
            result = await Runner.run(
                starting_agent=agent,
                input=full_input,
                context=context,
                config=config
            )

            # Extract response
            assistant_response = result.final_output

            # Save assistant message
            assistant_msg = Message(
                user_id=user_id,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=assistant_response,
                created_at=datetime.utcnow()
            )
            session.add(assistant_msg)

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)

            session.commit()
            session.refresh(assistant_msg)

            # Return response with metadata
            return {
                "conversation_id": conversation.id,
                "user_message_id": user_msg.id,
                "assistant_message_id": assistant_msg.id,
                "response": assistant_response,
                "tool_calls": getattr(result, "tool_calls", []),
                "created_at": assistant_msg.created_at.isoformat()
            }

    finally:
        session.close()


async def get_conversation_history(
    user_id: int,
    conversation_id: int,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieve conversation history for display.

    Args:
        user_id (int): User ID (for access control)
        conversation_id (int): Conversation ID
        limit (int): Maximum messages to return (default: 50)

    Returns:
        List[Dict[str, Any]]: List of messages with metadata

    Example:
        history = await get_conversation_history(user_id=1, conversation_id=5)
        for msg in history:
            print(f"{msg['role']}: {msg['content']}")
    """
    session: Session = next(get_session())

    try:
        # Verify conversation belongs to user
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise ValueError(f"Conversation {conversation_id} not found or access denied")

        # Get messages
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        ).all()

        return [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

    finally:
        session.close()


async def list_conversations(
    user_id: int,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """List all conversations for a user.

    Args:
        user_id (int): User ID
        limit (int): Maximum conversations to return (default: 20)
        offset (int): Pagination offset (default: 0)

    Returns:
        Dict[str, Any]: Pagination response with conversations

    Example:
        result = await list_conversations(user_id=1)
        for conv in result['conversations']:
            print(f"Conversation {conv['id']}: {conv['message_count']} messages")
    """
    session: Session = next(get_session())

    try:
        # Get total count
        total = len(session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all())

        # Get conversations
        conversations = session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

        # Build response
        conv_list = []
        for conv in conversations:
            # Count messages
            msg_count = len(session.exec(
                select(Message).where(Message.conversation_id == conv.id)
            ).all())

            conv_list.append({
                "id": conv.id,
                "user_id": conv.user_id,
                "message_count": msg_count,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            })

        return {
            "total": total,
            "count": len(conv_list),
            "offset": offset,
            "has_more": total > offset + len(conv_list),
            "conversations": conv_list
        }

    finally:
        session.close()


async def delete_conversation(user_id: int, conversation_id: int) -> bool:
    """Delete a conversation and all its messages.

    Args:
        user_id (int): User ID (for access control)
        conversation_id (int): Conversation ID to delete

    Returns:
        bool: True if deleted, False if not found

    Example:
        deleted = await delete_conversation(user_id=1, conversation_id=5)
        if deleted:
            print("Conversation deleted")
    """
    session: Session = next(get_session())

    try:
        # Find conversation
        conversation = session.get(Conversation, conversation_id)

        if not conversation or conversation.user_id != user_id:
            return False

        # Delete conversation (messages cascade delete automatically)
        session.delete(conversation)
        session.commit()

        return True

    finally:
        session.close()
