# Technology Research: Full-Stack Web Application

**Feature**: 002-step-2-web-app
**Date**: 2026-01-08
**Purpose**: Research and document technology choices, best practices, and integration patterns for transforming the console app into a full-stack web application.

## Research Questions

1. How should Better Auth integrate with FastAPI for JWT verification?
2. What's the best way to structure SQLModel models for multi-user data isolation?
3. How should Neon PostgreSQL connection pooling be configured?
4. What's the recommended approach for CORS configuration in FastAPI?
5. How should Next.js 16 App Router handle authentication state?

---

## 1. Better Auth + FastAPI JWT Integration

### Decision

Better Auth will run on the Next.js frontend and issue JWT tokens. FastAPI backend will verify these tokens using PyJWT with the shared `BETTER_AUTH_SECRET`.

### Rationale

- **Separation of Concerns**: Better Auth handles user session management on frontend
- **Stateless Backend**: FastAPI doesn't need session storage, only JWT verification
- **Standard Pattern**: JWT in `Authorization: Bearer <token>` header is industry standard
- **Scalability**: Stateless auth enables horizontal scaling of backend

### Implementation Approach

**Frontend (Better Auth)**:
```typescript
// src/lib/auth/auth-config.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    // Better Auth needs its own database connection
    // Uses same Neon database as backend
    type: "postgres",
    url: process.env.DATABASE_URL
  },
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [
    jwt({
      expiresIn: "7d"  // 7-day token expiration
    })
  ]
})
```

**Backend (FastAPI JWT Verification)**:
```python
# src/api/deps.py
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> dict:
    try:
        payload = jwt.decode(
            token.credentials,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401)
```

### Alternatives Considered

1. **Session-based auth**: Rejected - requires shared session store, not stateless
2. **Custom JWT implementation**: Rejected - Better Auth provides battle-tested JWT
3. **OAuth2 Password Flow**: Rejected - adds complexity, Better Auth sufficient

### Security Considerations

- Secret must be at least 32 characters (user provided: 32 chars ✓)
- Tokens should expire (7 days configured)
- HTTPS required in production
- Token should be stored in httpOnly cookie (XSS protection)

---

## 2. SQLModel Multi-User Data Isolation

### Decision

All tables will include `user_id` foreign key with explicit filtering in all queries. Database-level enforcement via row-level security (RLS) is optional but recommended for defense-in-depth.

### Rationale

- **Application-Level**: SQLModel queries always filter by `user_id`
- **Database-Level (Optional)**: PostgreSQL RLS provides additional security layer
- **Performance**: Index on `user_id` for fast filtering
- **Simplicity**: Application-level filtering is easier to debug and test

### Implementation Approach

**Task Model**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)  # INDEXED
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: "User" = Relationship(back_populates="tasks")
```

**Query Pattern** (always filter by user_id):
```python
# Example: Get all tasks for authenticated user
def get_user_tasks(db: Session, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id).all()
```

### Alternatives Considered

1. **Schema per user**: Rejected - doesn't scale, complex migrations
2. **Separate databases per user**: Rejected - massive overhead
3. **No foreign key, just integer field**: Rejected - loses referential integrity

### Index Strategy

- Primary index on `tasks.id`
- Secondary index on `tasks.user_id` (for filtering)
- Composite index on `(user_id, created_at)` if sorting by date

---

## 3. Neon PostgreSQL Connection Pooling

### Decision

Use Neon's built-in connection pooling via the pooler URL provided by user. SQLModel/SQLAlchemy will use default pool settings with minor tuning.

### Rationale

- **Neon Pooling**: User's DATABASE_URL includes `-pooler` endpoint (managed pooling)
- **Application Pooling**: SQLAlchemy's QueuePool for local connection reuse
- **Simplicity**: Default settings work well for <1000 concurrent connections

### Implementation Approach

**Database Configuration**:
```python
# src/db/session.py
from sqlmodel import create_engine, Session
from src.config import settings

# Neon pooler URL (from user)
# postgresql://...@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/...
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL logging in dev
    pool_pre_ping=True,   # Verify connections before use
    pool_size=5,          # Max 5 connections in pool
    max_overflow=10       # Allow 10 additional connections during peaks
)

def get_session():
    with Session(engine) as session:
        yield session
```

### Configuration Values

- `pool_size=5`: Keep 5 connections alive
- `max_overflow=10`: Allow bursts up to 15 total connections
- `pool_pre_ping=True`: Check connection health before use
- `pool_recycle=3600`: Recycle connections every hour

### Alternatives Considered

1. **No pooling**: Rejected - new connection per request is slow
2. **PgBouncer**: Rejected - Neon already provides pooling
3. **Async SQLAlchemy**: Considered for future optimization

---

## 4. FastAPI CORS Configuration

### Decision

Configure CORS to allow `http://localhost:3000` in development and production frontend URL in production. Use specific origins, not `*`.

### Rationale

- **Security**: Wildcard `*` allows any origin (insecure)
- **Development**: Need to allow localhost:3000 for local dev
- **Production**: Only allow production frontend domain
- **Credentials**: CORS must allow credentials for JWT cookies

### Implementation Approach

**CORS Middleware**:
```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:3000"]
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)
```

**Environment Configuration**:
```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]  # Default

    class Config:
        env_file = ".env"
```

**Production .env**:
```
CORS_ORIGINS=["https://your-app.vercel.app"]
```

### Alternatives Considered

1. **Allow all origins (`*`)**: Rejected - security risk
2. **No CORS**: Rejected - frontend can't make requests
3. **Proxy frontend through backend**: Rejected - adds complexity

### Security Notes

- Never use `allow_origins=["*"]` with `allow_credentials=True` (browsers reject)
- Update CORS_ORIGINS when deploying to production
- Consider environment-specific configuration

---

## 5. Next.js 16 App Router Authentication State

### Decision

Use Better Auth's built-in React hooks and server components for authentication state management. Store JWT in httpOnly cookies, not localStorage.

### Rationale

- **App Router**: Server components can access cookies directly
- **httpOnly Cookies**: Immune to XSS attacks (JavaScript can't read them)
- **Better Auth Hooks**: Provides `useSession()`, `signIn()`, `signOut()` utilities
- **Server-Side**: Can check auth on server before rendering pages

### Implementation Approach

**Auth Client Setup**:
```typescript
// src/lib/auth/auth-client.ts
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"
})

export const { useSession, signIn, signOut } = authClient
```

**Protected Server Component**:
```typescript
// src/app/tasks/page.tsx
import { redirect } from "next/navigation"
import { auth } from "@/lib/auth/auth-config"

export default async function TasksPage() {
  const session = await auth.api.getSession()

  if (!session) {
    redirect("/signin")
  }

  return <TaskList user={session.user} />
}
```

**Client Component with Hooks**:
```typescript
// src/components/auth/SignoutButton.tsx
"use client"
import { signOut } from "@/lib/auth/auth-client"

export function SignoutButton() {
  return (
    <button onClick={() => signOut()}>
      Sign Out
    </button>
  )
}
```

### Alternatives Considered

1. **localStorage for JWT**: Rejected - vulnerable to XSS
2. **Context API for state**: Rejected - Better Auth provides better DX
3. **Redux for auth state**: Rejected - overkill for simple auth
4. **Pages Router**: Rejected - App Router is Next.js 16 standard

### Token Storage Strategy

- **Development**: httpOnly cookie on `localhost`
- **Production**: httpOnly cookie on production domain with `secure` flag
- **API Calls**: Cookie automatically sent with requests (same domain)
- **Cross-Origin**: Use `credentials: 'include'` in fetch

---

## Summary of Decisions

| Topic | Decision | Primary Benefit |
|-------|----------|----------------|
| **Auth Integration** | Better Auth (frontend) + PyJWT (backend) | Stateless, scalable |
| **Data Isolation** | user_id foreign key + query filtering | Simple, performant |
| **Connection Pool** | Neon pooler + SQLAlchemy QueuePool | Managed + local optimization |
| **CORS** | Specific origins, credentials enabled | Secure, functional |
| **Auth State** | Better Auth hooks + httpOnly cookies | XSS-resistant, DX-friendly |

---

## Implementation Dependencies

**Backend**:
```toml
[project]
dependencies = [
    "fastapi>=0.100.0",
    "sqlmodel>=0.0.14",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "uvicorn[standard]>=0.23.0",
    "alembic>=1.12.0",
    "psycopg2-binary>=2.9.9",
    "python-dotenv>=1.0.0",
]
```

**Frontend**:
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.0.0",
    "better-auth": "^1.0.0",
    "tailwindcss": "^3.0.0",
    "axios": "^1.6.0"
  }
}
```

---

## Next Steps

1. ✅ Create data-model.md (database schema)
2. ✅ Create API contracts (endpoint specifications)
3. ✅ Create quickstart.md (setup guide)
4. → Proceed to `/sp.tasks` for task breakdown
