"""Tag Service

Business logic for task tag operations.
Handles adding, removing, and retrieving tags for tasks.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session, select

from ..models.task import Task
from ..models.task_tag import TaskTag


class TagService:
    """Service for task tag management.

    Enforces business rules:
    - Maximum 10 tags per task
    - Tag names are case-insensitive (stored lowercase)
    - Tag names are trimmed (no leading/trailing whitespace)
    - Tag names must be 1-50 characters
    - Duplicate tags are prevented
    """

    MAX_TAGS_PER_TASK = 10
    MIN_TAG_LENGTH = 1
    MAX_TAG_LENGTH = 50

    @staticmethod
    def validate_tag_name(tag_name: str) -> str:
        """
        Validate and normalize a tag name.

        Args:
            tag_name: Raw tag name from user input

        Returns:
            Normalized tag name (lowercase, trimmed)

        Raises:
            ValueError: If tag name is invalid
        """
        if not tag_name or not isinstance(tag_name, str):
            raise ValueError("Tag name is required")

        # Trim whitespace
        tag_name = tag_name.strip()

        # Check length
        if len(tag_name) < TagService.MIN_TAG_LENGTH:
            raise ValueError("Tag name cannot be empty")
        if len(tag_name) > TagService.MAX_TAG_LENGTH:
            raise ValueError(f"Tag name must be {TagService.MAX_TAG_LENGTH} characters or less")

        # Normalize to lowercase for case-insensitive comparison
        return tag_name.lower()

    @staticmethod
    def add_tag(session: Session, task_id: int, tag_name: str) -> TaskTag:
        """
        Add a tag to a task.

        Args:
            session: Database session
            task_id: ID of the task
            tag_name: Tag name to add

        Returns:
            Created TaskTag object

        Raises:
            ValueError: If tag is invalid or max tags exceeded
        """
        # Validate and normalize tag name
        normalized_tag = TagService.validate_tag_name(tag_name)

        # Check if task exists
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Check if tag already exists for this task
        existing_tag = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_name == normalized_tag
            )
        ).first()

        if existing_tag:
            # Tag already exists, return it (idempotent)
            return existing_tag

        # Check max tags limit
        current_tags_count = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()

        if len(current_tags_count) >= TagService.MAX_TAGS_PER_TASK:
            raise ValueError(
                f"Cannot add more than {TagService.MAX_TAGS_PER_TASK} tags per task"
            )

        # Create new tag
        new_tag = TaskTag(
            task_id=task_id,
            tag_name=normalized_tag,
            created_at=datetime.now(timezone.utc),
        )

        session.add(new_tag)
        session.commit()
        session.refresh(new_tag)

        return new_tag

    @staticmethod
    def remove_tag(session: Session, task_id: int, tag_name: str) -> bool:
        """
        Remove a tag from a task.

        Args:
            session: Database session
            task_id: ID of the task
            tag_name: Tag name to remove

        Returns:
            True if tag was removed, False if tag didn't exist
        """
        # Normalize tag name for comparison
        normalized_tag = TagService.validate_tag_name(tag_name)

        # Find and delete the tag
        tag = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_name == normalized_tag
            )
        ).first()

        if not tag:
            return False

        session.delete(tag)
        session.commit()

        return True

    @staticmethod
    def get_tags_for_task(session: Session, task_id: int) -> List[TaskTag]:
        """
        Get all tags for a task.

        Args:
            session: Database session
            task_id: ID of the task

        Returns:
            List of TaskTag objects, ordered by creation date (oldest first)
        """
        tags = session.exec(
            select(TaskTag)
            .where(TaskTag.task_id == task_id)
            .order_by(TaskTag.created_at.asc())
        ).all()

        return list(tags)

    @staticmethod
    def get_all_tags_for_user(session: Session, user_id: int) -> List[str]:
        """
        Get all unique tag names used by a user across all their tasks.

        Useful for autocomplete/suggestions in the UI.

        Args:
            session: Database session
            user_id: ID of the user

        Returns:
            List of unique tag names (sorted alphabetically)
        """
        # Join TaskTag with Task to filter by user_id
        statement = (
            select(TaskTag.tag_name)
            .join(Task, TaskTag.task_id == Task.id)
            .where(Task.user_id == user_id)
            .distinct()
            .order_by(TaskTag.tag_name.asc())
        )

        tag_names = session.exec(statement).all()

        return list(tag_names)

    @staticmethod
    def bulk_add_tags(session: Session, task_id: int, tag_names: List[str]) -> List[TaskTag]:
        """
        Add multiple tags to a task at once.

        Args:
            session: Database session
            task_id: ID of the task
            tag_names: List of tag names to add

        Returns:
            List of TaskTag objects (newly created + existing)

        Raises:
            ValueError: If any tag is invalid or total would exceed max tags

        Note:
            This is more efficient than calling add_tag() multiple times
            as it performs validation and limit checks before creating any tags.
        """
        # Validate all tag names first
        normalized_tags = []
        for tag_name in tag_names:
            normalized_tag = TagService.validate_tag_name(tag_name)
            if normalized_tag not in normalized_tags:  # Remove duplicates
                normalized_tags.append(normalized_tag)

        # Check if task exists
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Get existing tags
        existing_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()

        existing_tag_names = {tag.tag_name for tag in existing_tags}
        new_tag_names = [tag for tag in normalized_tags if tag not in existing_tag_names]

        # Check max tags limit
        total_tags = len(existing_tags) + len(new_tag_names)
        if total_tags > TagService.MAX_TAGS_PER_TASK:
            raise ValueError(
                f"Cannot add {len(new_tag_names)} tags. "
                f"Task already has {len(existing_tags)} tags. "
                f"Maximum is {TagService.MAX_TAGS_PER_TASK} tags per task."
            )

        # Create new tags
        new_tags = []
        for tag_name in new_tag_names:
            new_tag = TaskTag(
                task_id=task_id,
                tag_name=tag_name,
                created_at=datetime.now(timezone.utc),
            )
            session.add(new_tag)
            new_tags.append(new_tag)

        session.commit()

        # Refresh all new tags
        for tag in new_tags:
            session.refresh(tag)

        # Return all tags (existing + new)
        return list(existing_tags) + new_tags

    @staticmethod
    def replace_tags(session: Session, task_id: int, tag_names: List[str]) -> List[TaskTag]:
        """
        Replace all tags for a task with a new set of tags.

        Args:
            session: Database session
            task_id: ID of the task
            tag_names: List of tag names to set (replaces existing)

        Returns:
            List of TaskTag objects (newly created)

        Raises:
            ValueError: If any tag is invalid or count exceeds max tags

        Note:
            This removes all existing tags and creates new ones.
            More efficient than remove + add when replacing all tags.
        """
        # Validate tag count
        if len(tag_names) > TagService.MAX_TAGS_PER_TASK:
            raise ValueError(
                f"Cannot set {len(tag_names)} tags. "
                f"Maximum is {TagService.MAX_TAGS_PER_TASK} tags per task."
            )

        # Validate and normalize all tag names
        normalized_tags = []
        for tag_name in tag_names:
            normalized_tag = TagService.validate_tag_name(tag_name)
            if normalized_tag not in normalized_tags:  # Remove duplicates
                normalized_tags.append(normalized_tag)

        # Check if task exists
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Delete all existing tags
        existing_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()

        for tag in existing_tags:
            session.delete(tag)

        # Create new tags
        new_tags = []
        for tag_name in normalized_tags:
            new_tag = TaskTag(
                task_id=task_id,
                tag_name=tag_name,
                created_at=datetime.now(timezone.utc),
            )
            session.add(new_tag)
            new_tags.append(new_tag)

        session.commit()

        # Refresh all new tags
        for tag in new_tags:
            session.refresh(tag)

        return new_tags
