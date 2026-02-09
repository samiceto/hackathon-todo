"""
Chat Server Implementation for Task Management.

Provides conversational task management through chat interface.
Integrates with OpenAI API with function calling for task operations.

Architecture:
- FastAPI handles HTTP requests and streaming responses
- SQLModel Store persists conversations and messages to PostgreSQL
- OpenAI API processes natural language with function calling
- Task operations executed via TaskService
"""
from typing import Optional, AsyncIterator, Dict, Any
from datetime import datetime
import json

from openai import AsyncOpenAI
from sqlmodel import Session, select

from ..models import Conversation, Message, MessageRole
from ..db.session import engine
from ..config import settings
from ..services.tasks import TaskService
from ..schemas.task import CreateTaskRequest, UpdateTaskRequest


class ChatService:
    """
    Service for handling chat operations.

    Provides natural language task management through OpenAI integration
    with function calling for task operations.
    """

    def __init__(self):
        """Initialize chat service with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"  # or "gpt-3.5-turbo" for faster responses

        # Define available functions for OpenAI
        self.functions = [
            {
                "name": "list_tasks",
                "description": "Get all tasks for the user. Returns a list of tasks with their details including id, title, description, and completion status.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "add_task",
                "description": "Create a new task for the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title (required, 1-500 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description (max 5000 characters)"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as complete or incomplete (toggle completion status).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to toggle completion"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "update_task",
                "description": "Update a task's title and/or description.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the task (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the task (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "delete_task",
                "description": "Permanently delete a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        ]

    async def create_conversation(self, user_id: int) -> Conversation:
        """Create a new conversation.

        Args:
            user_id: User ID who owns the conversation

        Returns:
            Conversation: Created conversation object
        """
        with Session(engine) as session:
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation

    async def get_conversation(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get conversation by ID with ownership check.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for ownership verification

        Returns:
            Conversation if found and owned by user, None otherwise
        """
        with Session(engine) as session:
            conversation = session.get(Conversation, conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation
            return None

    async def get_conversation_history(
        self,
        conversation_id: int,
        user_id: int
    ) -> list[dict]:
        """Get conversation message history.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for ownership verification

        Returns:
            List of messages in OpenAI format
        """
        with Session(engine) as session:
            # Verify ownership
            conversation = session.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                return []

            # Get messages
            messages = session.exec(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .where(Message.user_id == user_id)
                .order_by(Message.created_at.asc())
            ).all()

            # Format for OpenAI
            return [
                {
                    "role": msg.role.value,
                    "content": msg.content
                }
                for msg in messages
            ]

    async def save_message(
        self,
        conversation_id: int,
        user_id: int,
        role: MessageRole,
        content: str
    ) -> Message:
        """Save a message to the database.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            role: Message role (user or assistant)
            content: Message content

        Returns:
            Message: Saved message object
        """
        with Session(engine) as session:
            message = Message(
                user_id=user_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=datetime.utcnow()
            )
            session.add(message)

            # Update conversation timestamp
            conversation = session.get(Conversation, conversation_id)
            if conversation:
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)

            session.commit()
            session.refresh(message)
            return message

    async def execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        user_id: int
    ) -> str:
        """Execute a function call and return the result as a string.

        Args:
            function_name: Name of the function to execute
            arguments: Function arguments as a dictionary
            user_id: User ID for data isolation

        Returns:
            String result of the function execution
        """
        with Session(engine) as session:
            try:
                if function_name == "list_tasks":
                    tasks = TaskService.get_all_tasks(session, user_id)
                    if not tasks:
                        return "You have no tasks yet."

                    task_list = []
                    for task in tasks:
                        status = "✓" if task.completed else "○"
                        task_list.append(
                            f"{status} Task #{task.id}: {task.title}"
                            + (f"\n  Description: {task.description}" if task.description else "")
                        )
                    return "Your tasks:\n" + "\n".join(task_list)

                elif function_name == "add_task":
                    title = arguments.get("title", "")
                    description = arguments.get("description", "")

                    task_data = CreateTaskRequest(title=title, description=description)
                    task = TaskService.create_task(session, user_id, task_data)

                    return f"✓ Task created successfully: #{task.id} - {task.title}"

                elif function_name == "complete_task":
                    task_id = arguments.get("task_id")
                    task = TaskService.toggle_completion(session, task_id, user_id)

                    if not task:
                        return f"❌ Task #{task_id} not found."

                    status = "complete" if task.completed else "incomplete"
                    return f"✓ Task #{task_id} marked as {status}: {task.title}"

                elif function_name == "update_task":
                    task_id = arguments.get("task_id")
                    title = arguments.get("title")
                    description = arguments.get("description")

                    task_data = UpdateTaskRequest(title=title, description=description)
                    task = TaskService.update_task(session, task_id, user_id, task_data)

                    if not task:
                        return f"❌ Task #{task_id} not found."

                    return f"✓ Task #{task_id} updated successfully: {task.title}"

                elif function_name == "delete_task":
                    task_id = arguments.get("task_id")
                    deleted = TaskService.delete_task(session, task_id, user_id)

                    if not deleted:
                        return f"❌ Task #{task_id} not found."

                    return f"✓ Task #{task_id} deleted successfully."

                else:
                    return f"Unknown function: {function_name}"

            except Exception as e:
                return f"❌ Error executing {function_name}: {str(e)}"

    async def process_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[int] = None,
        language: str = "en"
    ) -> AsyncIterator[dict]:
        """Process a user message and stream the response.

        Args:
            user_id: User ID
            message: User message text
            conversation_id: Optional conversation ID (creates new if None)
            language: Language preference for responses (e.g., 'en', 'ur')

        Yields:
            dict: Response chunks with content
        """
        # Create or get conversation
        if conversation_id is None:
            conversation = await self.create_conversation(user_id)
            conversation_id = conversation.id
        else:
            conversation = await self.get_conversation(conversation_id, user_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

        # Save user message
        await self.save_message(
            conversation_id, user_id, MessageRole.USER, message
        )

        # Get conversation history
        history = await self.get_conversation_history(conversation_id, user_id)

        # Build system prompt with language instructions
        language_instructions = {
            "en": "Respond in English.",
            "ur": "Respond in Urdu (اردو میں جواب دیں). Use Pakistani Urdu script and natural conversational Urdu language."
        }

        language_instruction = language_instructions.get(language, language_instructions["en"])

        system_content = f"""You are a helpful task management assistant with access to task management functions.

You can help users:
- List tasks: Use list_tasks() to show all tasks
- Add tasks: Use add_task(title, description) to create new tasks
- Complete tasks: Use complete_task(task_id) to mark tasks complete/incomplete
- Update tasks: Use update_task(task_id, title, description) to modify tasks
- Delete tasks: Use delete_task(task_id) to remove tasks

When users ask about their tasks, ALWAYS call the appropriate function first to get current data.
Be conversational, friendly, and helpful. Confirm actions clearly.

IMPORTANT: {language_instruction} All your responses must be in this language."""

        # Add system message with instructions
        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ] + history + [
            {
                "role": "user",
                "content": message
            }
        ]

        # Keep track of function calls for this turn
        while True:
            # Stream response from OpenAI
            full_response = ""
            function_name = None
            function_args = ""

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.functions,
                function_call="auto",
                stream=True,
                temperature=0.7
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta

                # Handle text content
                if delta.content:
                    content = delta.content
                    full_response += content
                    yield {"content": content, "done": False}

                # Handle function call
                if delta.function_call:
                    if delta.function_call.name:
                        function_name = delta.function_call.name

                    if delta.function_call.arguments:
                        function_args += delta.function_call.arguments

            # If no function was called, we're done
            if not function_name:
                # Save assistant response
                await self.save_message(
                    conversation_id, user_id, MessageRole.ASSISTANT, full_response
                )

                # Send final message with metadata
                yield {
                    "content": "",
                    "done": True,
                    "conversation_id": conversation_id
                }
                break

            # Execute the function
            try:
                arguments = json.loads(function_args) if function_args else {}
                function_result = await self.execute_function(
                    function_name, arguments, user_id
                )

                # Add function call and result to messages for next iteration
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": function_args
                    }
                })
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": function_result
                })

                # Continue loop to get assistant's response about the function result

            except json.JSONDecodeError as e:
                error_msg = f"Error parsing function arguments: {str(e)}"
                yield {"content": error_msg, "done": False}

                # Save error message
                await self.save_message(
                    conversation_id, user_id, MessageRole.ASSISTANT, error_msg
                )

                yield {
                    "content": "",
                    "done": True,
                    "conversation_id": conversation_id
                }
                break


# Global service instance
chat_service = ChatService()
