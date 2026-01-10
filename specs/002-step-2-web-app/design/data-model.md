# Data Model: Full-Stack Web Application

**Feature**: 002-step-2-web-app
**Date**: 2026-01-08
**Purpose**: Define database schema, entity relationships, and validation rules for multi-user task management.

## Overview

The application uses two primary entities:
1. **User** - Represents authenticated user accounts
2. **Task** - Represents todo items owned by users

**Relationship**: One User → Many Tasks (one-to-many)

---

## Entity: User

### Purpose
Stores user account information and authentication credentials.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Unique user identifier |
| `email` | String(255) | UNIQUE, NOT NULL | User's email address (login) |
| `hashed_password` | String(255) | NOT NULL | Bcrypt hashed password |
| `created_at` | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation time |
| `updated_at` | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

- **Primary**: `id` (automatic)
- **Unique**: `email` (for login lookups)

### Validation Rules

- **email**:
  - Must be valid email format (regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
  - Case-insensitive (store lowercase)
  - Max length: 255 characters

- **password** (before hashing):
  - Minimum 8 characters
  - Must contain at least one letter and one number (recommended)
  - No maximum length (will be hashed to fixed length)

- **hashed_password**:
  - Bcrypt hash (60 characters: $2b$12$...)
  - Never expose in API responses

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)
```

### Security Notes

- **Never** return `hashed_password` in API responses
- Use `passlib[bcrypt]` for password hashing
- Email should be unique constraint at database level
- Consider adding `is_active` field for soft account deletion (future)

---

## Entity: Task

### Purpose
Stores todo items with title, description, and completion status. Each task belongs to exactly one user.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL, INDEX | Owner of the task |
| `title` | String(500) | NOT NULL | Task title (required) |
| `description` | Text | NULLABLE | Task description (optional) |
| `completed` | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation time |
| `updated_at` | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

- **Primary**: `id` (automatic)
- **Foreign Key**: `user_id` (indexed for filtering)
- **Composite** (optional): `(user_id, created_at DESC)` for sorted queries

### Validation Rules

- **title**:
  - Required (NOT NULL)
  - Minimum 1 character (non-empty after trim)
  - Maximum 500 characters
  - Leading/trailing whitespace trimmed

- **description**:
  - Optional (can be empty string or NULL)
  - Maximum 5000 characters
  - Leading/trailing whitespace trimmed

- **completed**:
  - Boolean only (true/false)
  - Defaults to false (new tasks are incomplete)

- **user_id**:
  - Must reference valid user in `users` table
  - Cannot be NULL
  - Enforced by foreign key constraint

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional["User"] = Relationship(back_populates="tasks")
```

### Data Isolation Rules

**Critical Security Requirement**: All queries MUST filter by `user_id` to ensure data isolation.

```python
# ✅ CORRECT: Filter by authenticated user
tasks = db.query(Task).filter(Task.user_id == current_user.id).all()

# ❌ WRONG: Returns all users' tasks
tasks = db.query(Task).all()
```

---

## Relationships

### User → Tasks (One-to-Many)

- One user can have zero or more tasks
- Each task belongs to exactly one user
- Deleting a user deletes all their tasks (CASCADE)

**Foreign Key**:
```sql
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user_id
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;
```

**Cascade Delete**: When a user is deleted, all their tasks are automatically deleted.

---

## Database Schema (PostgreSQL)

### Create Tables SQL

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL CHECK (length(trim(title)) > 0),
    description TEXT DEFAULT '',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

---

## Alembic Migrations

### Initial Migration

Alembic will generate migration scripts from SQLModel models:

```bash
# Initialize Alembic
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema: users and tasks"

# Apply migration
alembic upgrade head
```

### Migration File Structure

```
backend/api/alembic/versions/
└── 001_initial_schema_users_and_tasks.py
```

---

## Sample Data

### User

```json
{
  "id": 1,
  "email": "user@example.com",
  "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYjLx.Y9K2i",
  "created_at": "2026-01-08T12:00:00Z",
  "updated_at": "2026-01-08T12:00:00Z"
}
```

### Task

```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete Step 2 implementation",
  "description": "Build full-stack web app with auth and database",
  "completed": false,
  "created_at": "2026-01-08T12:30:00Z",
  "updated_at": "2026-01-08T12:30:00Z"
}
```

---

## Validation Summary

| Entity | Field | Validation | Error Message |
|--------|-------|------------|---------------|
| User | email | Valid email format | "Invalid email address" |
| User | email | Unique | "Email already registered" |
| User | password | Min 8 chars | "Password must be at least 8 characters" |
| Task | title | Required, min 1 char | "Title cannot be empty" |
| Task | title | Max 500 chars | "Title cannot exceed 500 characters" |
| Task | description | Max 5000 chars | "Description cannot exceed 5000 characters" |
| Task | user_id | Valid foreign key | "Invalid user" |

---

## Performance Considerations

### Indexes

1. **users.email** - Speeds up login queries
2. **tasks.user_id** - Essential for filtering user's tasks
3. **tasks(user_id, created_at)** - Optimizes sorted task lists

### Query Optimization

```python
# ✅ OPTIMIZED: Uses index on user_id
tasks = (
    db.query(Task)
    .filter(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
    .all()
)

# ❌ SLOW: Full table scan
tasks = db.query(Task).all()  # Don't do this
```

### Connection Pooling

- Use Neon pooler URL (provided by user)
- SQLAlchemy pool_size: 5, max_overflow: 10
- Enable pool_pre_ping for connection health checks

---

## Future Enhancements (Out of Scope for Step 2)

- **User.is_active** - Soft delete for user accounts
- **Task.priority** - Priority levels (low, medium, high)
- **Task.due_date** - Task deadlines
- **Task.tags** - Many-to-many relationship for categorization
- **TaskHistory** - Audit log for task changes
- **User.email_verified** - Email verification status

---

## Database Connection

### Environment Variables

```bash
# Backend .env
DATABASE_URL=postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Frontend .env.local (for Better Auth)
DATABASE_URL=postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Note**: Both frontend (Better Auth) and backend (FastAPI) connect to the same Neon database.

---

## Conclusion

This data model provides:
- **Security**: Data isolation via user_id filtering
- **Simplicity**: Two tables, one relationship
- **Performance**: Proper indexes for common queries
- **Scalability**: Foreign keys with cascade delete
- **Extensibility**: Easy to add fields in future migrations
