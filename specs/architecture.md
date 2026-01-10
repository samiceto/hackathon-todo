# Hackathon Todo - System Architecture

## Architecture Evolution

This document describes the system architecture across all 5 development phases, showing the progression from a simple console application to a cloud-native AI-powered system.

---

## Phase 1: Console Application Architecture ✅ **IMPLEMENTED**

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User (Terminal)                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Application Layer (main.py)                 │
│  - Menu loop                                            │
│  - User input routing                                   │
│  - Welcome/goodbye messages                             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                UI Layer (ui.py)                          │
│  - Input validation helpers                             │
│  - Task display formatting                              │
│  - Error message presentation                           │
│  - User interaction flows                               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Storage Layer (storage.py)                  │
│  - TaskStorage class                                    │
│  - CRUD operations                                      │
│  - ID generation (auto-increment)                       │
│  - Task collection management                           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│               Data Layer (models.py)                     │
│  - Task dataclass                                       │
│  - Field validation                                     │
│  - Type hints                                           │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Layered Architecture**: Each layer depends only on layers below it
2. **Separation of Concerns**: UI, storage, and data are isolated
3. **Dependency Flow**: Application → UI → Storage → Data (unidirectional)
4. **Testability**: Each layer can be tested in isolation
5. **Simplicity**: No external dependencies (stdlib only)

### Data Flow (Example: Add Task)

```
User Input: "Buy groceries"
    │
    ▼
main.py: Routes to add_task_ui()
    │
    ▼
ui.py: get_non_empty_input("Title: ") → validates input
    │
    ▼
storage.py: TaskStorage.add(title, description)
    │
    ▼
models.py: Task(id=1, title="Buy groceries", ...)
    │
    ▼
storage.py: Stores in self._tasks[1] = task
    │
    ▼
ui.py: Displays success message
    │
    ▼
main.py: Returns to menu loop
```

### Storage Pattern

**In-Memory Dictionary**:
```python
class TaskStorage:
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

**Characteristics**:
- Session-based (data lost on exit)
- O(1) lookups by ID
- Sequential ID assignment
- No persistence layer
- Perfect for MVP/prototype

---

## Phase 2: Full-Stack Web Architecture 📋 **PLANNED**

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      User (Browser)                      │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────┐
│                Frontend (Next.js)                        │
│  - React 19+ components                                 │
│  - TypeScript + Tailwind CSS                            │
│  - Better Auth client                                   │
│  - TanStack Query (API client)                          │
│  - Server + Client components                           │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/JSON
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 Backend (FastAPI)                        │
│  ┌───────────────────────────────────────────────────┐ │
│  │          API Layer (app/routes/)                  │ │
│  │  - Task endpoints (/api/{user_id}/tasks)         │ │
│  │  - Auth endpoints (/api/auth/*)                  │ │
│  │  - Request/response validation                   │ │
│  └─────────────────────┬─────────────────────────────┘ │
│                        │                                 │
│  ┌─────────────────────▼─────────────────────────────┐ │
│  │       Business Logic Layer (app/services/)        │ │
│  │  - Task service (CRUD operations)                │ │
│  │  - Auth service (JWT, user management)          │ │
│  └─────────────────────┬─────────────────────────────┘ │
│                        │                                 │
│  ┌─────────────────────▼─────────────────────────────┐ │
│  │        Data Access Layer (app/models.py)          │ │
│  │  - SQLModel ORM                                   │ │
│  │  - Database session management                   │ │
│  └─────────────────────┬─────────────────────────────┘ │
└────────────────────────┼─────────────────────────────────┘
                         │ SQL
                         ▼
┌─────────────────────────────────────────────────────────┐
│            Database (Neon PostgreSQL)                    │
│  - Users table                                          │
│  - Tasks table (foreign key to users)                   │
│  - Indexes on user_id, completed                        │
│  - Automatic timestamps (created_at, updated_at)        │
└─────────────────────────────────────────────────────────┘
```

### Component Architecture

#### Frontend (Next.js)

```
frontend/
├── app/                          # App Router
│   ├── (auth)/                   # Auth routes (public)
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/              # Dashboard routes (protected)
│   │   ├── layout.tsx           # Dashboard layout with auth check
│   │   └── page.tsx             # Main dashboard
│   └── layout.tsx               # Root layout
├── components/
│   ├── TaskList.tsx             # Server component (fetch tasks)
│   ├── TaskCard.tsx             # Client component (interactions)
│   └── TaskForm.tsx             # Client component (create/edit)
└── lib/
    ├── api.ts                   # Backend API client
    └── auth.ts                  # Better Auth config
```

**Component Flow**:
```
app/page.tsx (Server Component)
    │
    ├─> Fetches tasks from backend API
    │
    └─> Passes to TaskList (Server Component)
            │
            └─> Maps to TaskCard (Client Component)
                    │
                    ├─> User clicks "Edit" → TaskForm modal
                    └─> User clicks "Delete" → API call → revalidate
```

#### Backend (FastAPI)

```
backend/api/
├── app/
│   ├── main.py                  # FastAPI app, CORS, middleware
│   ├── routes/
│   │   ├── tasks.py            # Task CRUD endpoints
│   │   └── auth.py             # Authentication endpoints
│   ├── models.py               # SQLModel ORM models
│   ├── db.py                   # Database connection
│   ├── auth.py                 # JWT middleware
│   └── config.py               # Environment config
└── tests/
    └── test_api_tasks.py       # API integration tests
```

**Request Flow** (Example: GET /api/{user_id}/tasks):
```
1. HTTP Request
   GET /api/user-123/tasks
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJh...

2. FastAPI Middleware
   ├─> CORS check
   ├─> JWT validation (auth.py)
   └─> Extract user_id from token

3. Route Handler (routes/tasks.py)
   @router.get("/api/{user_id}/tasks")
   async def get_tasks(user_id, current_user)
   ├─> Verify user_id matches authenticated user
   └─> Query database

4. Database Query (models.py via SQLModel)
   SELECT * FROM tasks WHERE user_id = 'user-123'

5. Response
   [
     {"id": 1, "title": "Buy groceries", ...},
     {"id": 2, "title": "Write report", ...}
   ]
```

### Database Schema

```sql
-- Users table (managed by Better Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

### Authentication Flow

```
1. User Registration
   POST /api/auth/signup
   { email, password, name }
       │
       ▼
   Better Auth creates user → hashes password → stores in DB
       │
       ▼
   Returns: { user, session, tokens }

2. User Login
   POST /api/auth/login
   { email, password }
       │
       ▼
   Better Auth validates credentials → generates JWT
       │
       ▼
   Returns: { accessToken, refreshToken }

3. Authenticated Request
   GET /api/{user_id}/tasks
   Authorization: Bearer <accessToken>
       │
       ▼
   FastAPI middleware validates JWT → extracts user_id
       │
       ▼
   Route handler checks user_id matches token → executes query
```

### API Contract

**Base URL**: `http://localhost:8000` (dev), `https://api.example.com` (prod)

**Authentication**: All endpoints require `Authorization: Bearer <jwt_token>` header

**Endpoints**:
```
GET    /api/{user_id}/tasks           # List all user tasks
POST   /api/{user_id}/tasks           # Create new task
GET    /api/{user_id}/tasks/{id}      # Get single task
PUT    /api/{user_id}/tasks/{id}      # Update task
DELETE /api/{user_id}/tasks/{id}      # Delete task
PATCH  /api/{user_id}/tasks/{id}/complete  # Toggle completion
```

**Error Format**:
```json
{
  "detail": "Task not found",
  "status_code": 404,
  "timestamp": "2026-01-05T22:30:00Z"
}
```

---

## Phase 3: AI Chatbot Architecture 📋 **PLANNED**

### Extended System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      User (Browser)                      │
└────────┬────────────────────────────────────┬───────────┘
         │                                    │
         │ Traditional UI                     │ Chat Interface
         ▼                                    ▼
┌──────────────────────┐          ┌──────────────────────┐
│   Task Dashboard     │          │   Chatbot Widget     │
│   (Next.js)          │          │   (WebSocket)        │
└──────────┬───────────┘          └──────────┬───────────┘
           │                                  │
           │ REST API                         │ WebSocket
           ▼                                  ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌────────────────────┐      ┌─────────────────────┐   │
│  │   Task API         │      │   Chat API          │   │
│  │   (REST)           │      │   (WebSocket)       │   │
│  └────────────────────┘      └──────────┬──────────┘   │
│                                          │               │
│         ┌────────────────────────────────▼──────────┐   │
│         │      OpenAI Agents SDK Layer             │   │
│         │  - Natural language processing           │   │
│         │  - Intent classification                 │   │
│         │  - Task parsing ("Buy milk" → Task)     │   │
│         └────────────────────┬───────────────────────┘   │
│                              │                           │
│         ┌────────────────────▼───────────────────────┐   │
│         │      MCP Server (Model Context)           │   │
│         │  - Task context for AI                    │   │
│         │  - User history and preferences           │   │
│         │  - Tool calling (create_task, list_tasks) │   │
│         └────────────────────┬───────────────────────┘   │
└──────────────────────────────┼───────────────────────────┘
                               │
      ┌────────────────────────┼────────────────────────┐
      │                        │                        │
      ▼                        ▼                        ▼
┌──────────┐          ┌─────────────┐        ┌──────────────┐
│PostgreSQL│          │  OpenAI API │        │ Vector DB    │
│(Tasks)   │          │  (GPT-4)    │        │ (Embeddings) │
└──────────┘          └─────────────┘        └──────────────┘
```

### Chat Interaction Flow

```
User: "Add task: Buy groceries tomorrow at 3pm"
    │
    ▼
Frontend WebSocket → Backend Chat API
    │
    ▼
OpenAI Agents SDK
    ├─> Intent: create_task
    ├─> Extract: title="Buy groceries", due_date="2026-01-06 15:00"
    └─> Call tool: create_task(...)
        │
        ▼
    MCP Server provides task context
        │
        ▼
    Database: INSERT INTO tasks (...)
        │
        ▼
    Response: "Task created: Buy groceries (due tomorrow 3pm)"
        │
        ▼
Frontend: Display in chat + update task list
```

---

## Phase 4: Kubernetes Architecture 📋 **PLANNED**

### Minikube Cluster Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Minikube Cluster                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │           Ingress Controller                   │     │
│  │  hackathon-todo.local → routes to services    │     │
│  └─────────┬──────────────────────────┬──────────┘     │
│            │                           │                 │
│  ┌─────────▼────────┐      ┌──────────▼──────────┐     │
│  │  Frontend Pod    │      │   Backend Pod       │     │
│  │  (Next.js)       │      │   (FastAPI)         │     │
│  │  Replicas: 2     │      │   Replicas: 3       │     │
│  └─────────┬────────┘      └──────────┬──────────┘     │
│            │                           │                 │
│  ┌─────────▼────────────────────────────▼──────────┐   │
│  │            Service (ClusterIP)                  │   │
│  │  - frontend-service (port 3000)                │   │
│  │  - backend-service (port 8000)                 │   │
│  └─────────────────────┬───────────────────────────┘   │
│                        │                                │
│  ┌─────────────────────▼───────────────────────────┐   │
│  │      PostgreSQL StatefulSet                     │   │
│  │  - Persistent Volume (PVC)                      │   │
│  │  - Headless Service                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           ConfigMaps & Secrets                   │  │
│  │  - Database credentials                          │  │
│  │  - API keys                                      │  │
│  │  - Environment configuration                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 5: Cloud-Native Architecture 📋 **PLANNED**

### Production System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Repository                      │
└────────────────────────┬────────────────────────────────┘
                         │ push
                         ▼
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions CI/CD                        │
│  - Lint, test, build                                    │
│  - Docker image creation                                │
│  - Security scanning                                    │
│  - Deploy to Kubernetes                                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Production)             │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Frontend Pods (auto-scaling: 2-10)             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Backend Pods (auto-scaling: 3-20)              │   │
│  │  ┌──────────────────────────────────────┐       │   │
│  │  │   Kafka Consumer (Dapr sidecar)      │       │   │
│  │  └──────────────────────────────────────┘       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Kafka Cluster (Event Bus)               │   │
│  │  - task.created events                           │   │
│  │  - task.updated events                           │   │
│  │  - user.action events                            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │    Prometheus (Metrics) + Grafana (Dashboards)   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Design Decisions & Rationale

### Why FastAPI for Backend?
- **Async/Await**: Native async support for high concurrency
- **Type Safety**: Pydantic validation, automatic OpenAPI docs
- **Performance**: Comparable to Node.js, faster than Flask/Django
- **Developer Experience**: Auto-generated API docs, easy testing

### Why Next.js for Frontend?
- **App Router**: Server + client components for optimal performance
- **SEO**: Server-side rendering out of the box
- **Developer Experience**: File-based routing, TypeScript support
- **Ecosystem**: React 19+, Tailwind CSS, shadcn/ui integration

### Why SQLModel for ORM?
- **Pydantic Integration**: Shares validation with FastAPI
- **Type Safety**: Full type hints, IDE autocomplete
- **SQLAlchemy Core**: Mature, battle-tested ORM foundation
- **Developer Experience**: Define models once, use everywhere

### Why Neon PostgreSQL?
- **Serverless**: Auto-scaling, pay-per-use
- **Performance**: Fast cold starts, global deployment
- **Developer Experience**: Easy branching, instant restore
- **Cost**: Free tier for development, affordable scaling

### Why Better Auth?
- **Framework Agnostic**: Works with FastAPI + Next.js
- **Features**: Email/password, OAuth, 2FA, session management
- **Type Safety**: Full TypeScript support
- **Developer Experience**: Simple setup, comprehensive docs

---

## Non-Functional Requirements

### Performance Targets

**Frontend**:
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1

**Backend**:
- API Response Time (p95): < 200ms
- Database Query Time (p95): < 50ms
- Throughput: > 1000 requests/second

### Scalability

**Horizontal Scaling**:
- Frontend pods: 2-10 (auto-scale based on CPU)
- Backend pods: 3-20 (auto-scale based on requests/second)
- Database: Neon auto-scaling (serverless)

### Security

- HTTPS/TLS for all connections
- JWT with short expiration (15 min) + refresh tokens
- SQL injection protection (parameterized queries)
- XSS protection (React auto-escaping)
- CORS configuration (whitelist frontend domain)
- Rate limiting (100 requests/minute per user)

### Reliability

- **Availability**: 99.9% uptime target
- **Backup**: Daily automated backups (Neon)
- **Monitoring**: Prometheus metrics + Grafana dashboards
- **Alerting**: Critical errors → on-call notifications
- **Rollback**: Kubernetes rolling updates with quick rollback

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-05
**Status**: Phase 1 complete, Phase 2 in planning
