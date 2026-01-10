# Quickstart Guide: Full-Stack Web Application

**Feature**: 002-step-2-web-app
**Date**: 2026-01-08
**Purpose**: Step-by-step setup instructions for running the full-stack todo application locally.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** (matches Step 1 requirement)
- **UV** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Node.js 20+** and **npm** or **pnpm**
- **Git** (for version control)
- **WSL 2** (if on Windows)
- **PostgreSQL client** (optional, for database inspection): `psql`

**Verify installations**:
```bash
python --version    # Should be 3.13+
uv --version        # Should show UV version
node --version      # Should be 20+
npm --version       # Should be 10+
```

---

## Project Structure Overview

```
hackathon-todo/
├── backend/
│   ├── console/          # Step 1 - Console app (preserved)
│   └── api/              # Step 2 - FastAPI backend (NEW)
├── frontend/             # Step 2 - Next.js frontend (NEW)
└── specs/                # Specifications and planning
```

---

## Setup Step 1: Clone and Navigate

```bash
# If not already in the project directory
cd /path/to/hackathon-todo

# Verify you're on the correct branch
git branch
# Should show: * 002-step-2-web-app

# If not on correct branch
git checkout 002-step-2-web-app
```

---

## Setup Step 2: Backend API

### 2.1 Navigate to Backend Directory

```bash
cd backend/api
```

### 2.2 Create Environment File

Create a `.env` file with the following content:

```bash
# backend/api/.env

# Database
DATABASE_URL=postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Authentication
BETTER_AUTH_SECRET=uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Environment
DEBUG=True
```

**Security Note**: This `.env` file is gitignored. Never commit secrets to Git.

### 2.3 Install Dependencies

```bash
# Initialize UV project
uv sync
```

This will:
- Create a virtual environment
- Install all dependencies from `pyproject.toml`
- Install FastAPI, SQLModel, PyJWT, passlib, uvicorn, etc.

### 2.4 Initialize Database

```bash
# Run database migrations
uv run alembic upgrade head
```

This will:
- Create `users` and `tasks` tables
- Set up foreign key constraints
- Create necessary indexes

**Verify database**:
```bash
# Optional: Connect to Neon database to verify tables
psql "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Once connected, list tables
\dt

# Expected output:
#  Schema |  Name  | Type  |     Owner
# --------+--------+-------+----------------
#  public | users  | table | neondb_owner
#  public | tasks  | table | neondb_owner
```

### 2.5 Run Backend Server

```bash
# Start FastAPI server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Will watch for changes in these directories: ['/path/to/backend/api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify backend is running**:
```bash
# In a new terminal
curl http://localhost:8000/docs

# Should return FastAPI's auto-generated API documentation (Swagger UI)
```

**Keep this terminal open** - backend must stay running.

---

## Setup Step 3: Frontend Application

### 3.1 Navigate to Frontend Directory

Open a **new terminal** window/tab:

```bash
cd /path/to/hackathon-todo/frontend
```

### 3.2 Create Environment File

Create a `.env.local` file:

```bash
# frontend/.env.local

# Better Auth
BETTER_AUTH_SECRET=uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC
BETTER_AUTH_URL=http://localhost:3000

# Database (Better Auth needs this)
DATABASE_URL=postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: `NEXT_PUBLIC_*` variables are exposed to the browser. Never put secrets in these.

### 3.3 Install Dependencies

```bash
# Using npm
npm install

# Or using pnpm (faster)
pnpm install
```

This will:
- Install Next.js 16+, React 18+, Better Auth, Tailwind CSS
- Create `node_modules/` directory
- Generate `package-lock.json` or `pnpm-lock.yaml`

### 3.4 Run Frontend Server

```bash
# Using npm
npm run dev

# Or using pnpm
pnpm dev
```

**Expected output**:
```
  ▲ Next.js 16.0.0
  - Local:        http://localhost:3000
  - Network:      http://192.168.1.x:3000

 ✓ Ready in 2.3s
```

**Verify frontend is running**:
Open browser and navigate to http://localhost:3000

You should see the landing page with links to signup/signin.

**Keep this terminal open** - frontend must stay running.

---

## Setup Step 4: Verify Everything Works

### 4.1 Check Backend Health

**API Documentation**:
```
http://localhost:8000/docs
```
Should display FastAPI's interactive API docs (Swagger UI).

**Health Check** (if implemented):
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 4.2 Check Frontend Pages

Open browser and verify these pages load:
- **Landing**: http://localhost:3000
- **Signup**: http://localhost:3000/signup
- **Signin**: http://localhost:3000/signin
- **Tasks** (will redirect to signin if not authenticated): http://localhost:3000/tasks

### 4.3 Test End-to-End Flow

1. **Create Account**:
   - Go to http://localhost:3000/signup
   - Enter email: `test@example.com`
   - Enter password: `password123` (min 8 chars)
   - Click "Sign Up"
   - Should redirect to `/tasks`

2. **Create a Task**:
   - Click "Add Task" button
   - Title: "My first task"
   - Description: "Testing the app"
   - Click "Create"
   - Should see task in the list

3. **Mark Complete**:
   - Click checkbox next to task
   - Task should update visually (strikethrough or color change)

4. **Edit Task**:
   - Click "Edit" button
   - Change title to "My updated task"
   - Click "Save"
   - Should see updated title

5. **Delete Task**:
   - Click "Delete" button
   - Confirm in dialog
   - Task should disappear from list

6. **Sign Out**:
   - Click "Sign Out" button
   - Should redirect to `/signin`

7. **Sign In Again**:
   - Go to http://localhost:3000/signin
   - Enter same credentials
   - Should redirect to `/tasks`
   - Previous tasks should still be there (persistence verified)

---

## Running Tests

### Backend Tests

```bash
cd backend/api

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_auth.py -v

# View coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests (requires backend and frontend running)
npm run test:e2e

# Run tests in watch mode
npm test -- --watch
```

---

## Development Workflow

### Typical Development Session

**Terminal 1 - Backend**:
```bash
cd backend/api
uv run uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Terminal 3 - Commands**:
```bash
# Run tests, make git commits, etc.
```

### Hot Reload

- **Backend**: FastAPI auto-reloads on file changes (--reload flag)
- **Frontend**: Next.js auto-reloads on file changes (default in dev mode)

### Making Changes

1. Edit code in your IDE
2. Save file
3. Server automatically reloads
4. Refresh browser (or auto-refresh if Next.js Fast Refresh enabled)

---

## Common Issues and Solutions

### Issue 1: Port Already in Use

**Error**: `Address already in use: 0.0.0.0:8000`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
uvicorn src.main:app --reload --port 8001
```

### Issue 2: Database Connection Failed

**Error**: `could not connect to server`

**Solution**:
1. Verify DATABASE_URL is correct in `.env`
2. Check internet connection (Neon is cloud-hosted)
3. Verify Neon database is active (check Neon dashboard)
4. Test connection:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

### Issue 3: CORS Error in Browser

**Error**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**:
1. Verify `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
2. Restart backend server
3. Clear browser cache
4. Verify `app.add_middleware(CORSMiddleware, ...)` is configured in backend

### Issue 4: JWT Token Not Found

**Error**: `Not authenticated` when accessing `/tasks`

**Solution**:
1. Sign out and sign in again
2. Check browser dev tools → Application → Cookies
3. Verify `auth_token` cookie exists
4. Check `BETTER_AUTH_SECRET` matches in both `.env` files

### Issue 5: Dependencies Not Installing

**Error**: `uv: command not found` or `npm: command not found`

**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Install Node.js (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

---

## Environment Variables Reference

### Backend (`backend/api/.env`)

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://...` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | `uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC` | Shared secret for JWT (32+ chars) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |
| `DEBUG` | `True` or `False` | Enable debug logging |

### Frontend (`frontend/.env.local`)

| Variable | Value | Description |
|----------|-------|-------------|
| `BETTER_AUTH_SECRET` | `uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC` | Shared secret for JWT (must match backend) |
| `BETTER_AUTH_URL` | `http://localhost:3000` | Frontend URL |
| `DATABASE_URL` | `postgresql://...` | Neon PostgreSQL (for Better Auth) |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL (exposed to browser) |

---

## Database Management

### View All Users

```bash
psql "$DATABASE_URL" -c "SELECT id, email, created_at FROM users;"
```

### View All Tasks

```bash
psql "$DATABASE_URL" -c "SELECT id, user_id, title, completed FROM tasks;"
```

### Reset Database (Caution!)

```bash
cd backend/api

# Drop all tables
uv run alembic downgrade base

# Recreate all tables
uv run alembic upgrade head
```

---

## Next Steps

After verifying everything works:

1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:3000
3. ✅ Can signup, signin, create tasks, and persist data

**You're ready to start development!**

Proceed to:
- **`/sp.tasks`** - Generate task breakdown for implementation
- **`/sp.implement`** - Execute tasks phase by phase

---

## Production Deployment (Future)

Not covered in this quickstart (Step 2 scope is local development only). Future steps:

- Deploy backend to Railway, Render, or AWS
- Deploy frontend to Vercel or Netlify
- Use production DATABASE_URL from Neon
- Update CORS_ORIGINS to production frontend URL
- Enable HTTPS (required in production)
- Set secure environment variables in hosting platform

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **Better Auth Docs**: https://better-auth.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Neon Docs**: https://neon.tech/docs
- **Tailwind CSS Docs**: https://tailwindcss.com/docs

---

## Support

If you encounter issues not covered here:

1. Check the error logs in the terminal
2. Inspect browser console (F12)
3. Review the specification in `specs/002-step-2-web-app/spec.md`
4. Check the API contracts in `specs/002-step-2-web-app/contracts/`
5. Ask for help with specific error messages
