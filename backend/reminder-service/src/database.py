"""Database connection and session management for Reminder Service."""

from sqlmodel import Session, create_engine

from .config import settings

# Create database engine
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def get_session() -> Session:
    """Get database session.

    Yields:
        SQLModel Session for database operations
    """
    with Session(engine) as session:
        yield session
