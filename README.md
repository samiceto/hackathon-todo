# Hackathon Todo

**Progressive task management application** evolving from console app to cloud-native AI-powered system through 5 incremental phases.

---

## 🎯 Current Status

- ✅ **Step 1 Complete**: Console application with 97.44% test coverage (129 tests)
- ✅ **Step 2 Complete**: Full-stack web application with FastAPI + Next.js + PostgreSQL
- 📋 **Steps 3-5 Planned**: AI chatbot, Kubernetes deployment, cloud-native features

---

## 📁 Monorepo Structure

This project is organized as a monorepo to support gradual evolution:

```
hackathon-todo/                    # Root
├── backend/                       # Backend services
│   ├── console/                  # ✅ Step 1: Console app (COMPLETE)
│   │   ├── src/hackathon_todo/  # Console source code
│   │   ├── tests/               # 129 tests, 97.44% coverage
│   │   └── README.md            # Console app documentation
│   └── api/                      # ✅ Step 2: FastAPI web API (COMPLETE)
├── frontend/                      # ✅ Step 2: Next.js web app (COMPLETE)
├── specs/                         # Organized specifications
│   ├── features/                 # Feature specifications
│   ├── api/                      # API endpoint specs
│   ├── database/                 # Database schema specs
│   ├── ui/                       # UI component specs
│   ├── overview.md              # Project overview
│   └── architecture.md          # System architecture
├── .spec-kit/                     # Monorepo configuration
│   └── config.yaml               # Phase definitions, tech stack
├── history/                       # Development history (PHRs)
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Step 1: Console Application (Available Now) ✅

**Prerequisites**:
- Python 3.13 or higher
- [UV](https://docs.astral.sh/uv/) package manager

**Installation & Run**:
```bash
# Clone repository
git clone <repository-url>
cd hackathon-todo

# Navigate to console app
cd backend/console

# Install dependencies
uv sync

# Run application
uv run hackathon-todo
# OR
uv run python -m hackathon_todo.main
```

**Testing**:
```bash
cd backend/console

# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src/hackathon_todo --cov-report=html

# Verbose output
uv run pytest -v
```

### Step 2: Full-Stack Web Application (Available Now) ✅

**Prerequisites**:
- Python 3.13 or higher + [UV](https://docs.astral.sh/uv/)
- Node.js 20+ and npm 10+
- Neon PostgreSQL database

**Backend Setup**:
```bash
# Navigate to backend API
cd backend/api

# Copy environment file
cp .env.example .env
# Edit .env with your DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start backend server (http://localhost:8000)
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup** (in a new terminal):
```bash
# Navigate to frontend
cd frontend

# Copy environment file
cp .env.local.example .env.local
# Edit .env.local with BETTER_AUTH_SECRET, DATABASE_URL, NEXT_PUBLIC_API_URL

# Install dependencies
npm install

# Start frontend server (http://localhost:3000)
npm run dev
```

**Access the Application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📚 Console Application Features (Step 1)

The current working console application includes:

### Core Features
- ✅ **Add Tasks** - Create tasks with title and optional description
- ✅ **View Tasks** - See all tasks in formatted list with status indicators
- ✅ **Mark Complete** - Toggle tasks between complete (✓) and incomplete (○)
- ✅ **Update Tasks** - Edit task titles and descriptions
- ✅ **Delete Tasks** - Remove tasks from your list
- ✅ **Interactive Menu** - Easy-to-use menu-driven interface
- ✅ **Error Handling** - Robust validation and retry logic
- ✅ **Graceful Exit** - Clean shutdown with Ctrl+C support

### Usage Example

```
==================================================
Welcome to Hackathon Todo!
Your simple command-line task manager
==================================================

==============================
=== Hackathon Todo Menu ===
==============================
1. Add Task
2. View Tasks
3. Mark Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit
==============================

Enter your choice (1-6): 1

Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Milk, eggs, bread

Task added successfully! (ID: 1)
Title: Buy groceries
Description: Milk, eggs, bread
```

**Full console app documentation**: See [backend/console/README.md](backend/console/README.md)

---

## 🗺️ Roadmap

### Step 1: Console Application ✅ **COMPLETE**
**Status**: Implementation complete, all tests passing

**Deliverables**:
- Python 3.13+ console application
- In-memory task storage
- 5 core CRUD features
- 97.44% test coverage (129 tests)
- Clean architecture (data → storage → UI → application)

**Tech Stack**: Python 3.13+, UV, pytest, in-memory storage

---

### Step 2: Full-Stack Web Application ✅ **COMPLETE**
**Status**: Full-stack web application implemented and tested

**Features**:
- RESTful API with FastAPI
- Next.js 16+ web frontend
- PostgreSQL database (Neon serverless)
- User authentication (Better Auth + JWT)
- Responsive web UI
- Docker containerization

**Tech Stack**:
- **Backend**: FastAPI, SQLModel, Neon PostgreSQL, Better Auth
- **Frontend**: Next.js 16+, React 19+, TypeScript, Tailwind CSS, shadcn/ui
- **Infrastructure**: Docker, Docker Compose

**Migration Path**:
- Console models → SQLModel ORM
- In-memory storage → PostgreSQL
- Console UI → Next.js components
- 129 console tests → API integration tests

---

### Step 3: AI-Powered Chatbot 📋 **PLANNED**
**Status**: Specifications planned, implementation future

**Planned Features**:
- OpenAI Agents SDK integration
- Model Context Protocol (MCP) server
- Conversational task management
- Natural language parsing
- Intelligent task suggestions

**Tech Stack**: OpenAI Agents SDK, MCP SDK, OpenAI API (GPT-4), WebSocket

**Example Interactions**:
- "Add task: Buy groceries tomorrow at 3pm" → Parses and creates task
- "What should I work on next?" → AI-powered prioritization
- "Summarize my week" → Task completion analysis

---

### Step 4: Local Kubernetes Deployment 📋 **PLANNED**
**Status**: Planned for future implementation

**Planned Features**:
- Dockerized multi-service application
- Kubernetes manifests (Deployments, Services, Ingress)
- Helm charts for orchestration
- Minikube local cluster

**Tech Stack**: Docker, Minikube, Kubernetes, Helm

---

### Step 5: Advanced Cloud Deployment 📋 **PLANNED**
**Status**: Planned for future implementation

**Planned Features**:
- CI/CD pipeline (GitHub Actions)
- Event-driven architecture (Kafka + Dapr)
- Monitoring (Prometheus + Grafana)
- AIOps with kubectl-ai

**Tech Stack**: GitHub Actions, Kafka, Dapr, Prometheus, Grafana, kubectl-ai

---

## 🏗️ Architecture

### Current: Console Application (Step 1)

**Layered Architecture**:
```
Application Layer (main.py)     ← Menu loop, routing
       ↓
UI Layer (ui.py)                ← User interaction, formatting
       ↓
Storage Layer (storage.py)      ← CRUD operations
       ↓
Data Layer (models.py)          ← Task entity, validation
```

**Storage**: In-memory dictionary (session-based, data lost on exit)

**Full architecture documentation**: See [specs/architecture.md](specs/architecture.md)

### Future: Full-Stack Web Application (Step 2+)

**High-Level System**:
```
Browser → Next.js Frontend → FastAPI Backend → PostgreSQL Database
                                    ↓
                            OpenAI Agents (Step 3+)
```

**Detailed architecture diagrams**: See [specs/architecture.md](specs/architecture.md)

---

## 📖 Documentation

### Core Documents
- **[specs/overview.md](specs/overview.md)** - Comprehensive project overview, all 5 phases
- **[specs/architecture.md](specs/architecture.md)** - Detailed architecture for all phases
- **[.spec-kit/config.yaml](.spec-kit/config.yaml)** - Monorepo configuration, phase definitions

### Component-Specific
- **[backend/console/README.md](backend/console/README.md)** - Console app documentation (Step 1)
- **[CLAUDE.md](CLAUDE.md)** - Root development context
- **[backend/CLAUDE.md](backend/CLAUDE.md)** - Backend development context
- **[frontend/CLAUDE.md](frontend/CLAUDE.md)** - Frontend development context (placeholder)

### Specifications
- **[specs/features/](specs/features/)** - Feature specifications
- **[specs/api/](specs/api/)** - API endpoint specifications (planned)
- **[specs/database/](specs/database/)** - Database schema specifications (planned)
- **[specs/ui/](specs/ui/)** - UI component specifications (planned)

### Historical Reference
- **[specs/001-step-1-core-features/](specs/001-step-1-core-features/)** - Original Step 1 specs
- **[history/prompts/](history/prompts/)** - Prompt History Records (PHRs)

---

## 🧪 Testing

### Console Application (Step 1)

**Coverage**: 97.44% (129 tests passing)

```bash
cd backend/console

# Run all tests
uv run pytest

# With coverage report
uv run pytest --cov=src/hackathon_todo --cov-report=html

# Specific test file
uv run pytest tests/test_models.py

# Verbose output
uv run pytest -v
```

**Test Organization**:
- `test_models.py` - Task dataclass tests
- `test_storage.py` - CRUD operation tests
- `test_ui.py` - UI function tests
- `test_integration.py` - End-to-end workflow tests

---

## 🛠️ Development Methodology

### Spec-Driven Development (SDD)

**Core Principle**: Specifications define *what* to build; Claude Code generates *how* to build it.

**Workflow**:
1. **Specify** - Define requirements in `specs/<type>/<feature>.md`
2. **Plan** - Create implementation plan with architecture decisions
3. **Tasks** - Break down into testable, actionable tasks
4. **Implement** - Execute via Claude Code using TDD
5. **Validate** - Verify acceptance criteria met

**Benefits**:
- Forces clear thinking about requirements before implementation
- Creates reusable intelligence for future projects
- Ensures traceability and documentation
- Enables AI-assisted development at scale

### Quality Standards

**Testing**:
- Minimum 90% code coverage (current: 97.44%)
- Test-Driven Development (TDD)
- Unit, integration, and E2E tests

**Code Quality**:
- Type hints (Python), TypeScript (frontend)
- Clean architecture principles
- Separation of concerns
- Comprehensive documentation

---

## 🤝 Contributing

This is a hackathon project demonstrating Spec-Driven Development methodology.

### Development Process

1. Review specifications in `specs/`
2. Follow TDD approach (write tests first)
3. Maintain >90% test coverage
4. Document changes in Prompt History Records (PHRs)
5. Adhere to clean architecture principles

**See**: [CLAUDE.md](CLAUDE.md) for detailed development guidelines

---

## 📝 License

[Specify license here]

---

## 🙏 Acknowledgments

**Built with**:
- Python 3.13, UV package manager, pytest
- Spec-Driven Development methodology
- Claude Code for implementation

**Part of**: Hackathon II - The Evolution of Todo

---

## 📞 Support

For questions or issues:
- Open an issue in the repository
- Review documentation in `specs/` directory
- Check `history/prompts/` for development history

---

**Made with ❤️ for the Hackathon**

**Last Updated**: 2026-01-09 (Step 2 Complete - Full-stack web application)
