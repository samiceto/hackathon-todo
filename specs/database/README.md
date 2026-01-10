# Database Specifications

This directory contains database schema, migration, and data model specifications.

## Organization

Database specs define:
- Table schemas and relationships
- Indexes and constraints
- Migration strategies
- Data retention policies
- Backup and recovery procedures

## Planned Specifications

### Step 2: PostgreSQL Schema
- **schema.md** - Database schema for tasks, users (planned)
- **migrations.md** - Migration strategy from in-memory to PostgreSQL (planned)

### Step 3+: Extended Schema
- **chatbot-context-schema.md** - AI conversation history (planned)

## Current Status

**Not yet implemented** - Specifications will be created when migrating from in-memory storage to Neon PostgreSQL in Step 2.

## Current Storage (Step 1)

The console app uses in-memory storage:
- **Type**: Python dictionaries and dataclasses
- **Location**: `backend/console/src/hackathon_todo/storage.py`
- **Persistence**: None (session-based, data lost on exit)

## Migration Path

**Step 1 → Step 2 Migration**:
```
In-memory Dictionary           →  PostgreSQL Tables
--------------------              ------------------
TaskStorage._tasks (dict)      →  tasks table
Task dataclass                 →  SQLModel ORM
Sequential ID (int)            →  SERIAL PRIMARY KEY
No user isolation              →  user_id foreign key
```

## Database Design Principles

When creating database specs, follow these guidelines:
- Normalize to 3NF (Third Normal Form)
- Use appropriate data types
- Define foreign key constraints
- Create indexes for query optimization
- Document migration strategies
- Consider data retention and archival
