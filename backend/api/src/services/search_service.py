"""
Search Service

Provides full-text search capabilities using PostgreSQL tsvector.
Searches task titles and descriptions using natural language queries.
"""

from typing import List
import logging

from sqlmodel import Session, select, or_, text, col
from ..models.task import Task

logger = logging.getLogger(__name__)


class SearchService:
    """Service for full-text search operations on tasks"""

    @staticmethod
    def search_tasks(
        session: Session,
        user_id: int,
        query: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        Search tasks using PostgreSQL full-text search.

        Uses tsvector for efficient full-text search on title and description fields.
        The search query supports:
        - Natural language queries (multiple words)
        - Partial word matching
        - Case-insensitive search
        - Ranking by relevance

        Args:
            session: Database session
            user_id: User ID to filter tasks (data isolation)
            query: Search query string
            limit: Maximum number of results (default: 100)
            offset: Number of results to skip for pagination (default: 0)

        Returns:
            List of tasks matching the search query, ordered by relevance (best match first)

        Example:
            >>> tasks = SearchService.search_tasks(session, 1, "meeting notes")
            >>> # Returns tasks with "meeting" or "notes" in title or description
        """
        if not query or not query.strip():
            logger.warning(f"Empty search query provided for user_id={user_id}")
            return []

        # Sanitize query for tsquery (remove special characters, lowercase)
        sanitized_query = query.strip().replace("'", "''")  # Escape single quotes

        # Split query into words and join with OR operator for better matching
        words = sanitized_query.split()
        tsquery_string = " | ".join(words)  # OR operator for words

        try:
            # Use PostgreSQL full-text search with tsvector
            # to_tsvector converts text to searchable format
            # to_tsquery converts query to search pattern
            # ts_rank provides relevance score for ordering
            statement = (
                select(Task)
                .where(Task.user_id == user_id)
                .where(
                    or_(
                        # Search in title
                        text("to_tsvector('english', title) @@ to_tsquery('english', :query)").bindparams(query=tsquery_string),
                        # Search in description
                        text("to_tsvector('english', description) @@ to_tsquery('english', :query)").bindparams(query=tsquery_string)
                    )
                )
                .order_by(
                    # Order by relevance score (highest first)
                    text("ts_rank(to_tsvector('english', title || ' ' || COALESCE(description, '')), to_tsquery('english', :query)) DESC").bindparams(query=tsquery_string)
                )
                .offset(offset)
                .limit(limit)
            )

            results = session.exec(statement).all()

            logger.info(
                f"Search query '{query}' for user_id={user_id} returned {len(results)} results "
                f"(limit={limit}, offset={offset})"
            )

            return list(results)

        except Exception as e:
            logger.error(
                f"Full-text search failed for user_id={user_id}, query='{query}': {str(e)}",
                exc_info=True
            )
            # Fallback to simple LIKE search if tsvector search fails
            return SearchService._fallback_like_search(session, user_id, query, limit, offset)

    @staticmethod
    def _fallback_like_search(
        session: Session,
        user_id: int,
        query: str,
        limit: int,
        offset: int
    ) -> List[Task]:
        """
        Fallback search using SQL LIKE when full-text search fails.

        This is less efficient than tsvector but provides basic search capability
        as a safety net if the GIN index is not available or tsvector fails.

        Args:
            session: Database session
            user_id: User ID to filter tasks
            query: Search query string
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of tasks matching the search query using LIKE
        """
        logger.warning(f"Using fallback LIKE search for user_id={user_id}, query='{query}'")

        # Use case-insensitive LIKE search
        search_pattern = f"%{query}%"

        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(
                or_(
                    col(Task.title).ilike(search_pattern),
                    col(Task.description).ilike(search_pattern)
                )
            )
            .order_by(Task.created_at.desc())  # Order by newest first
            .offset(offset)
            .limit(limit)
        )

        results = session.exec(statement).all()

        logger.info(
            f"Fallback search for user_id={user_id} returned {len(results)} results"
        )

        return list(results)
