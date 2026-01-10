"""
Database Connection Test Script

Tests connectivity to the Neon PostgreSQL database.
Run this before running migrations to ensure credentials are correct.
"""

from src.config import settings
from src.db.session import engine
from sqlmodel import text


def test_connection():
    """
    Test database connection.

    Returns:
        bool: True if connection successful, False otherwise
    """
    print("Testing connection to Neon PostgreSQL database...")
    print(f"Database URL: {str(settings.DATABASE_URL).split('@')[1].split('/')[0]}...")  # Hide credentials
    print()

    try:
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()

            print("✅ Successfully connected to PostgreSQL!")
            print(f"📊 Version: {version}")
            print()

            # Check if tables exist
            result = conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print(f"📋 Existing tables: {', '.join(tables)}")
            else:
                print("📋 No tables found (expected before running migrations)")

            print()
            print("✅ Connection test PASSED")
            print()
            print("Next steps:")
            print("1. Run migrations: uv run alembic upgrade head")
            print("2. Start backend server: uv run uvicorn src.main:app --reload")

            return True

    except Exception as e:
        print(f"❌ Connection test FAILED")
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify DATABASE_URL in .env file is correct")
        print("2. Check if Neon database is active in the Neon console")
        print("3. Ensure your machine can access the internet")
        print("4. Verify firewall settings allow PostgreSQL connections")

        return False


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
