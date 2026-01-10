"""Database session management.

Configures SQLAlchemy engine and session for Neon PostgreSQL with connection pooling.
"""
from sqlmodel import create_engine, Session
from ..config import settings


# Create database engine with connection pooling
# Neon provides pooling at the database level, but we add local pooling for optimization
engine = create_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=5,  # Maximum number of database connections to maintain
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
)


def get_session() -> Session:
    """Get a database session.

    This is a FastAPI dependency that provides a database session
    and ensures it is properly closed after the request.

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            users = session.exec(select(User)).all()
            return users
    """
    with Session(engine) as session:
        yield session
