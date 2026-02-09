"""
ChatKit Store Implementation for PostgreSQL/SQLModel.

Provides data persistence for ChatKit conversations using existing
Conversation and Message SQLModel models.

Architecture:
- ThreadMetadata ↔ Conversation model
- ThreadItem ↔ Message model (serialized as JSON in content field)
- Uses SQLModel Session for database operations
- Stateless - loads data fresh on each request
"""
from typing import Optional, Any
from datetime import datetime
from uuid import uuid4

from chatkit.store import Store
from chatkit.types import (
    ThreadMetadata,
    ThreadItem,
    UserMessageItem,
    AssistantMessageItem,
    Page,
)
from sqlmodel import Session, select
from sqlalchemy import desc, asc

from ..models import Conversation, Message, MessageRole
from ..db.session import engine


# Type alias for request context (contains user_id for access control)
RequestContext = dict[str, Any]


class ChatKitStore(Store[RequestContext]):
    """
    ChatKit Store implementation using SQLModel and PostgreSQL.

    Maps ChatKit concepts to database models:
    - Thread → Conversation
    - ThreadItem → Message (with JSON serialization)

    Context must contain 'user_id' (int) for access control.
    """

    def generate_thread_id(self, context: RequestContext) -> str:
        """Generate a unique thread ID.

        Args:
            context: Request context (contains user_id)

        Returns:
            str: UUID-based thread ID with 'thread_' prefix
        """
        return f"thread_{uuid4().hex}"

    def generate_item_id(
        self,
        item_type: str,
        thread: ThreadMetadata,
        context: RequestContext
    ) -> str:
        """Generate a unique item ID.

        Args:
            item_type: Type of item ('message', 'widget', etc.)
            thread: Thread metadata
            context: Request context

        Returns:
            str: UUID-based item ID with type prefix
        """
        return f"{item_type}_{uuid4().hex}"

    async def load_thread(
        self,
        thread_id: str,
        context: RequestContext
    ) -> ThreadMetadata:
        """Load thread metadata from database.

        Args:
            thread_id: Thread ID (format: 'thread_<uuid>')
            context: Request context with user_id

        Returns:
            ThreadMetadata: Thread metadata

        Raises:
            ValueError: If thread not found or access denied
        """
        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id required in context")

        # Extract numeric ID from thread_id
        db_id = self._thread_id_to_db(thread_id)

        with Session(engine) as session:
            conversation = session.get(Conversation, db_id)

            if not conversation:
                raise ValueError(f"Thread {thread_id} not found")

            if conversation.user_id != user_id:
                raise ValueError(f"Access denied to thread {thread_id}")

            return ThreadMetadata(
                id=thread_id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                metadata={}  # Can store custom metadata if needed
            )

    async def save_thread(
        self,
        thread: ThreadMetadata,
        context: RequestContext
    ) -> None:
        """Save or update thread metadata in database.

        Args:
            thread: Thread metadata to save
            context: Request context with user_id
        """
        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id required in context")

        db_id = self._thread_id_to_db(thread.id)

        with Session(engine) as session:
            conversation = session.get(Conversation, db_id)

            if conversation:
                # Update existing
                conversation.updated_at = thread.updated_at
                session.add(conversation)
            else:
                # Create new
                conversation = Conversation(
                    id=db_id,
                    user_id=user_id,
                    created_at=thread.created_at,
                    updated_at=thread.updated_at
                )
                session.add(conversation)

            session.commit()

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str],
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Page[ThreadItem]:
        """Load paginated thread items (messages) from database.

        Args:
            thread_id: Thread ID
            after: Item ID to start after (for pagination)
            limit: Maximum number of items to return
            order: Sort order ('asc' or 'desc')
            context: Request context with user_id

        Returns:
            Page[ThreadItem]: Paginated list of thread items
        """
        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id required in context")

        db_id = self._thread_id_to_db(thread_id)

        with Session(engine) as session:
            # Build query
            query = select(Message).where(
                Message.conversation_id == db_id,
                Message.user_id == user_id
            )

            # Apply pagination (after)
            if after:
                after_db_id = self._item_id_to_db(after)
                if order == "asc":
                    query = query.where(Message.id > after_db_id)
                else:
                    query = query.where(Message.id < after_db_id)

            # Apply ordering
            if order == "asc":
                query = query.order_by(asc(Message.created_at))
            else:
                query = query.order_by(desc(Message.created_at))

            # Apply limit (+1 to check if there are more)
            query = query.limit(limit + 1)

            # Execute query
            messages = session.exec(query).all()

            # Check if there are more items
            has_more = len(messages) > limit
            items = messages[:limit]

            # Convert to ThreadItems
            thread_items = [self._message_to_thread_item(msg) for msg in items]

            return Page(
                items=thread_items,
                has_more=has_more
            )

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: RequestContext,
    ) -> None:
        """Add a new item (message) to a thread.

        Args:
            thread_id: Thread ID
            item: Thread item to add
            context: Request context with user_id
        """
        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id required in context")

        db_thread_id = self._thread_id_to_db(thread_id)

        with Session(engine) as session:
            # Determine message role based on item type
            if isinstance(item, UserMessageItem):
                role = MessageRole.USER
            elif isinstance(item, AssistantMessageItem):
                role = MessageRole.ASSISTANT
            else:
                # For other types, store as assistant message with JSON serialization
                role = MessageRole.ASSISTANT

            # Extract content (handle both string and list of content parts)
            if isinstance(item, (UserMessageItem, AssistantMessageItem)):
                if isinstance(item.content, list):
                    # Concatenate text parts
                    content_text = " ".join(
                        part.text if hasattr(part, "text") else str(part)
                        for part in item.content
                    )
                else:
                    content_text = item.content
            else:
                # For other item types, serialize to JSON
                content_text = item.model_dump_json()

            message = Message(
                user_id=user_id,
                conversation_id=db_thread_id,
                role=role,
                content=content_text,
                created_at=item.created_at
            )

            session.add(message)
            session.commit()

            # Update conversation timestamp
            conversation = session.get(Conversation, db_thread_id)
            if conversation:
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()

    async def update_thread_item(
        self,
        thread_id: str,
        item_id: str,
        update: dict,
        context: RequestContext,
    ) -> None:
        """Update an existing thread item.

        Args:
            thread_id: Thread ID
            item_id: Item ID to update
            update: Fields to update
            context: Request context with user_id
        """
        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id required in context")

        db_item_id = self._item_id_to_db(item_id)

        with Session(engine) as session:
            message = session.get(Message, db_item_id)

            if not message:
                raise ValueError(f"Item {item_id} not found")

            if message.user_id != user_id:
                raise ValueError(f"Access denied to item {item_id}")

            # Update allowed fields
            if "content" in update:
                message.content = update["content"]

            session.add(message)
            session.commit()

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: RequestContext,
    ) -> None:
        """Delete a thread item.

        Args:
            thread_id: Thread ID
            item_id: Item ID to delete
            context: Request context with user_id
        """
        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id required in context")

        db_item_id = self._item_id_to_db(item_id)

        with Session(engine) as session:
            message = session.get(Message, db_item_id)

            if not message:
                raise ValueError(f"Item {item_id} not found")

            if message.user_id != user_id:
                raise ValueError(f"Access denied to item {item_id}")

            session.delete(message)
            session.commit()

    # Helper methods for ID conversion

    def _thread_id_to_db(self, thread_id: str) -> int:
        """Convert ChatKit thread ID to database ID.

        Args:
            thread_id: ChatKit thread ID (format: 'thread_<uuid>')

        Returns:
            int: Database conversation ID

        Raises:
            ValueError: If thread_id format is invalid
        """
        # For now, we'll use a simple hash-based approach
        # In production, you might want to maintain a mapping table
        # or use a different ID strategy
        if not thread_id.startswith("thread_"):
            raise ValueError(f"Invalid thread_id format: {thread_id}")

        # Extract UUID part and convert to int
        # This is a simplified approach - in production you'd want a mapping table
        uuid_part = thread_id.replace("thread_", "")
        return int(uuid_part[:16], 16) % (2**31 - 1)  # Keep it within int range

    def _item_id_to_db(self, item_id: str) -> int:
        """Convert ChatKit item ID to database ID.

        Args:
            item_id: ChatKit item ID (format: '<type>_<uuid>')

        Returns:
            int: Database message ID
        """
        # Similar approach as thread_id
        parts = item_id.split("_", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid item_id format: {item_id}")

        uuid_part = parts[1]
        return int(uuid_part[:16], 16) % (2**31 - 1)

    def _db_to_thread_id(self, db_id: int) -> str:
        """Convert database ID to ChatKit thread ID.

        Args:
            db_id: Database conversation ID

        Returns:
            str: ChatKit thread ID
        """
        # Simple conversion - in production use a mapping table
        return f"thread_{db_id:016x}"

    def _db_to_item_id(self, db_id: int, item_type: str = "message") -> str:
        """Convert database ID to ChatKit item ID.

        Args:
            db_id: Database message ID
            item_type: Type of item

        Returns:
            str: ChatKit item ID
        """
        return f"{item_type}_{db_id:016x}"

    def _message_to_thread_item(self, message: Message) -> ThreadItem:
        """Convert database Message to ChatKit ThreadItem.

        Args:
            message: Database message model

        Returns:
            ThreadItem: ChatKit thread item
        """
        item_id = self._db_to_item_id(message.id)
        thread_id = self._db_to_thread_id(message.conversation_id)

        if message.role == MessageRole.USER:
            return UserMessageItem(
                id=item_id,
                thread_id=thread_id,
                created_at=message.created_at,
                content=message.content
            )
        else:  # ASSISTANT
            return AssistantMessageItem(
                id=item_id,
                thread_id=thread_id,
                created_at=message.created_at,
                content=message.content
            )
