# Hackathon Todo - Backend API

FastAPI backend for the Hackathon Todo full-stack web application (Step 2).

## Technology Stack

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT (python-jose)
- **Password Hashing**: passlib with bcrypt
- **Migrations**: Alembic
- **Server**: Uvicorn
- **Testing**: pytest, pytest-asyncio, httpx

## Project Structure

```
backend/api/
├── src/
│   ├── models/       # SQLModel database models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── api/          # API route handlers
│   ├── services/     # Business logic
│   ├── db/           # Database configuration
│   ├── config.py     # Environment settings
│   └── main.py       # FastAPI application entry point
├── tests/            # Pytest test suite
├── alembic/          # Database migrations
├── .env.example      # Example environment variables
├── pyproject.toml    # Python dependencies
└── alembic.ini       # Alembic configuration
```

## Setup

### Prerequisites

- Python 3.13+
- UV (Python package manager)
- Neon PostgreSQL database

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend/api
   ```

2. **Copy environment variables**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and add your credentials**:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: 32+ character secret (must match frontend)
   - `CORS_ORIGINS`: `["http://localhost:3000"]` for development

4. **Install dependencies**:
   ```bash
   uv sync
   ```

5. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

6. **Start the development server**:
   ```bash
   uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Server will be available at: http://localhost:8000

7. **View API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Testing

Run tests with coverage:

```bash
uv run pytest
```

Run specific test file:

```bash
uv run pytest tests/test_auth.py -v
```

Generate HTML coverage report:

```bash
uv run pytest --cov=src --cov-report=html
```

## API Endpoints

### Authentication (Public)
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Sign in with email and password

### Tasks (JWT Required)
- `GET /api/{user_id}/tasks` - List all user's tasks
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get task details
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion status

## Database Migrations

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Rollback one migration:

```bash
uv run alembic downgrade -1
```

## Development

The backend uses:
- **FastAPI** for the web framework with automatic OpenAPI documentation
- **SQLModel** for ORM and schema validation (combines SQLAlchemy + Pydantic)
- **JWT tokens** for stateless authentication
- **Alembic** for database schema migrations
- **pytest** for testing with async support

All endpoints (except auth) require JWT authentication via `Authorization: Bearer <token>` header.

## Security

- Passwords are hashed with bcrypt (12 rounds)
- JWT tokens expire after 7 days
- CORS is configured to allow only specific origins
- All database queries filter by authenticated user ID
- SQL injection prevented by SQLModel ORM parameterized queries

## Related Documentation

- [API Endpoint Contracts](../../specs/002-step-2-web-app/contracts/api-endpoints.md)
- [Authentication Flow](../../specs/002-step-2-web-app/contracts/auth-flow.md)
- [Data Model](../../specs/002-step-2-web-app/design/data-model.md)
- [Quickstart Guide](../../specs/002-step-2-web-app/design/quickstart.md)
