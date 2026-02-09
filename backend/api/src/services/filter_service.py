"""
Filter Service

Builds dynamic queries for filtering tasks by multiple criteria.
Supports filtering by status, priority, tags, and due date ranges.
"""

from typing import List, Optional
from datetime import datetime, date
import logging

from sqlmodel import Session, select, and_, or_, col
from ..models.task import Task, PriorityLevel
from ..models.task_tag import TaskTag

logger = logging.getLogger(__name__)


class FilterService:
    """Service for building dynamic filter queries on tasks"""

    @staticmethod
    def filter_tasks(
        session: Session,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date_start: Optional[datetime] = None,
        due_date_end: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        Filter tasks by multiple criteria with dynamic query building.

        All filters are combined with AND logic (task must match all specified criteria).
        Multiple tags are combined with AND logic (task must have all specified tags).

        Args:
            session: Database session
            user_id: User ID to filter tasks (data isolation)
            status: Filter by completion status ("completed", "incomplete", or None for all)
            priority: Filter by priority level (low, medium, high, urgent, or None for all)
            tags: Filter by tag names (task must have ALL specified tags, or None for no tag filter)
            due_date_start: Filter tasks with due_date >= this date (or None for no lower bound)
            due_date_end: Filter tasks with due_date <= this date (or None for no upper bound)
            limit: Maximum number of results (default: 100)
            offset: Number of results to skip for pagination (default: 0)

        Returns:
            List of tasks matching all filter criteria, ordered by created_at desc

        Example:
            >>> tasks = FilterService.filter_tasks(
            ...     session, user_id=1, status="incomplete",
            ...     priority="high", tags=["urgent", "meeting"]
            ... )
            >>> # Returns incomplete tasks with priority=high AND both tags "urgent" and "meeting"
        """
        # Build base query - always filter by user_id for data isolation
        statement = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status is not None:
            if status == "completed":
                statement = statement.where(Task.completed == True)
            elif status == "incomplete":
                statement = statement.where(Task.completed == False)
            else:
                logger.warning(
                    f"Invalid status filter '{status}' for user_id={user_id}. "
                    f"Expected 'completed' or 'incomplete'. Ignoring filter."
                )

        # Apply priority filter
        if priority is not None:
            try:
                # Validate priority value
                priority_enum = PriorityLevel(priority)
                statement = statement.where(Task.priority == priority_enum)
            except ValueError:
                logger.warning(
                    f"Invalid priority filter '{priority}' for user_id={user_id}. "
                    f"Expected one of {[p.value for p in PriorityLevel]}. Ignoring filter."
                )

        # Apply due date range filters
        if due_date_start is not None:
            statement = statement.where(Task.due_date >= due_date_start)

        if due_date_end is not None:
            statement = statement.where(Task.due_date <= due_date_end)

        # Apply tag filters (task must have ALL specified tags)
        if tags and len(tags) > 0:
            # For each tag, task must have a matching TaskTag record
            # This creates a subquery for each tag to ensure ALL tags are present
            for tag_name in tags:
                tag_subquery = (
                    select(TaskTag.task_id)
                    .where(TaskTag.tag_name == tag_name)
                )
                statement = statement.where(col(Task.id).in_(tag_subquery))

        # Order by created_at descending (newest first)
        statement = statement.order_by(Task.created_at.desc())

        # Apply pagination
        statement = statement.offset(offset).limit(limit)

        # Execute query
        try:
            results = session.exec(statement).all()

            # Log filter operation
            filter_criteria = []
            if status:
                filter_criteria.append(f"status={status}")
            if priority:
                filter_criteria.append(f"priority={priority}")
            if tags:
                filter_criteria.append(f"tags={tags}")
            if due_date_start:
                filter_criteria.append(f"due_date>={due_date_start}")
            if due_date_end:
                filter_criteria.append(f"due_date<={due_date_end}")

            logger.info(
                f"Filter query for user_id={user_id} with criteria [{', '.join(filter_criteria)}] "
                f"returned {len(results)} results (limit={limit}, offset={offset})"
            )

            return list(results)

        except Exception as e:
            logger.error(
                f"Filter query failed for user_id={user_id}: {str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def validate_filter_params(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date_start: Optional[datetime] = None,
        due_date_end: Optional[datetime] = None
    ) -> dict:
        """
        Validate filter parameters before applying them.

        Returns a dictionary with validation results:
        - "valid": True if all params are valid
        - "errors": List of validation error messages

        Args:
            status: Status filter value
            priority: Priority filter value
            due_date_start: Start date for due date range
            due_date_end: End date for due date range

        Returns:
            Validation result dictionary with "valid" (bool) and "errors" (list)

        Example:
            >>> result = FilterService.validate_filter_params(status="invalid", priority="high")
            >>> print(result)
            {"valid": False, "errors": ["Invalid status: invalid. Expected 'completed' or 'incomplete'."]}
        """
        errors = []

        # Validate status
        if status is not None and status not in ["completed", "incomplete"]:
            errors.append(
                f"Invalid status: {status}. Expected 'completed' or 'incomplete'."
            )

        # Validate priority
        if priority is not None:
            try:
                PriorityLevel(priority)
            except ValueError:
                valid_priorities = [p.value for p in PriorityLevel]
                errors.append(
                    f"Invalid priority: {priority}. Expected one of {valid_priorities}."
                )

        # Validate due date range
        if due_date_start and due_date_end and due_date_start > due_date_end:
            errors.append(
                f"Invalid due date range: start date ({due_date_start}) "
                f"must be before or equal to end date ({due_date_end})."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
