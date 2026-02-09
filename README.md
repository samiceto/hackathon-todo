# Hackathon Todo 🚀

A progressive task management application built in 5 incremental steps, evolving from a simple CLI tool to a cloud-deployed full-stack application with AI capabilities.

**Current Status**: Step 4 - Kubernetes Deployment ✅ (Phases 5-6 Complete)

## 📋 Project Overview

This project demonstrates Spec-Driven Development (SDD) by building a complete application through iterative evolution:

- **Step 1** ✅: Console Todo App (Python CLI with in-memory storage)
- **Step 2** ✅: Web Application (FastAPI backend + Next.js frontend + PostgreSQL)
- **Step 3** ✅: AI Chatbot Integration (OpenAI Agents SDK + ChatKit UI)
- **Step 4** 🔨: **Kubernetes Deployment** (Minikube + Helm Charts + Docker) - **IN PROGRESS**
- **Step 5** 📅: Cloud Deployment (CI/CD + Monitoring + Production)

## 🎯 Quick Start

### Step 4: Run on Kubernetes (Current)

Deploy the full-stack Todo Chatbot application to a local Kubernetes cluster using Minikube:

```bash
# Prerequisites: Docker Desktop 24+, Minikube 1.32+, kubectl 1.28+, Helm 3.x

# 1. Start Minikube cluster
minikube start --driver=docker --cpus=2 --memory=4096

# 2. Configure Docker environment
eval $(minikube docker-env)

# 3. Build Docker images
cd backend/api
docker build -t todo-backend:latest .

cd ../../frontend
docker build -t todo-frontend:latest .

# 4. Deploy with Helm
cd ..
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-dev.yaml \
  --set backend.secrets.openaiApiKey=$OPENAI_API_KEY \
  --set backend.secrets.betterAuthSecret=your-secret-here

# 5. Access the application
# Frontend: http://$(minikube ip):30000
# Backend: kubectl port-forward svc/todo-app-backend 8000:8000
minikube service todo-app-frontend
```

**Detailed Guide**: See [specs/004-k8s-deployment/quickstart.md](specs/004-k8s-deployment/quickstart.md)

### Step 3: Run Locally (Full-Stack with AI)

```bash
# Backend
cd backend/api
uv sync
cp .env.example .env  # Add your OpenAI API key and database URL
uv run uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.local.example .env.local  # Configure API URL
npm run dev

# Access: http://localhost:3000
```

### Step 1: Run Console App

```bash
cd backend/console
uv sync
uv run hackathon-todo
```

## 🏗️ Architecture

### Monorepo Structure

```
hackathon-todo/
├── backend/
│   ├── console/          # Step 1: Python CLI app
│   └── api/              # Steps 2-3: FastAPI application
│       ├── Dockerfile    # Step 4: Backend container
│       └── src/          # API, agents, MCP, auth
├── frontend/             # Steps 2-3: Next.js application
│   ├── Dockerfile        # Step 4: Frontend container
│   └── src/              # UI components, ChatKit
├── helm/                 # Step 4: Helm Charts
│   └── todo-app/         # Kubernetes deployment
│       ├── Chart.yaml
│       ├── values.yaml   # Production defaults
│       ├── values-dev.yaml  # Minikube overrides
│       └── templates/    # K8s resource templates
├── specs/                # Feature specifications
│   ├── 001-step-1-core-features/
│   ├── 003-step-3-ai-chatbot/
│   └── 004-k8s-deployment/
├── history/              # Prompt History Records (PHRs)
└── .specify/             # SDD templates & scripts
```

### Tech Stack

**Step 4 (Current - Kubernetes)**:
- **Container Runtime**: Docker 24+ (multi-stage builds)
- **Orchestration**: Kubernetes 1.28+ (via Minikube)
- **Package Manager**: Helm 3.x (declarative infrastructure)
- **Health Checks**: Liveness & readiness probes
- **Resource Management**: CPU/memory limits enforced

**Step 3 (AI Chatbot)**:
- **AI Framework**: OpenAI Agents SDK (Swarm multi-agent)
- **Frontend Chat**: OpenAI ChatKit (React components)
- **NLP**: OpenAI GPT-4 for task management
- **MCP Protocol**: Tool calling for database operations

**Steps 2-3 (Web Application)**:
- **Backend**: FastAPI, SQLModel, Uvicorn, Better Auth
- **Frontend**: Next.js 16+, React, Tailwind CSS
- **Database**: Neon Serverless PostgreSQL (external, not containerized)
- **Auth**: Better Auth with JWT verification

**Step 1 (Console)**:
- **Language**: Python 3.13+
- **Package Manager**: UV
- **Testing**: pytest (97.44% coverage)

## 🐳 Kubernetes Deployment (Step 4)

### Helm Chart Features

- **Zero-Downtime Updates**: Rolling update strategy (maxSurge: 1, maxUnavailable: 0)
- **Health Checks**: Liveness and readiness probes on all pods
- **Resource Limits**: CPU and memory constraints enforced
- **Configuration Management**: ConfigMaps (non-sensitive) + Secrets (API keys)
- **Auto-Scaling Ready**: HPA configuration (disabled for Minikube)
- **Environment-Specific Values**: values-dev.yaml (Minikube), values-prod.yaml (cloud)

### Deployed Components

| Component | Replicas | Resources (Requests/Limits) | Health Checks | Access |
|-----------|----------|----------------------------|---------------|--------|
| Backend (FastAPI) | 1 (dev) / 2 (prod) | CPU: 250m/500m, Memory: 256Mi/512Mi | /health endpoint | ClusterIP (NodePort in dev) |
| Frontend (Next.js) | 1 (dev) / 2 (prod) | CPU: 100m/200m, Memory: 128Mi/256Mi | / endpoint | NodePort (port 30000) |

### Helm Commands

```bash
# Install/Upgrade
helm upgrade --install todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml

# Rollback
helm rollback todo-app

# View history
helm history todo-app

# Uninstall
helm uninstall todo-app
```

### Kubernetes Operations

```bash
# Check pods
kubectl get pods -l app.kubernetes.io/instance=todo-app

# View logs
kubectl logs -f -l app.kubernetes.io/component=backend

# Check resource usage (requires metrics-server)
kubectl top pods -l app.kubernetes.io/instance=todo-app

# Port forward backend
kubectl port-forward svc/todo-app-backend 8000:8000

# Access frontend via Minikube
minikube service todo-app-frontend
```

## 🧪 Testing

### Step 4: Kubernetes Deployment Tests

```bash
# Health checks
kubectl get pods  # All pods should be Ready 1/1

# Backend API
kubectl port-forward svc/todo-app-backend 8000:8000
curl http://localhost:8000/health  # Should return {"status": "healthy"}

# Frontend UI
minikube service todo-app-frontend  # Opens browser

# Rolling update (zero downtime)
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
kubectl get pods -w  # Watch rolling update

# Auto-restart (self-healing)
kubectl delete pod -l app.kubernetes.io/component=backend
kubectl get pods  # New pod should be created automatically
```

### Step 1: Console App Tests

```bash
cd backend/console
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest --cov             # Coverage report (97.44%)
```

## 📚 Documentation

### Step 4: Kubernetes Deployment

- **Quickstart Guide**: [specs/004-k8s-deployment/quickstart.md](specs/004-k8s-deployment/quickstart.md) - Complete deployment walkthrough (30 minutes)
- **Architecture Plan**: [specs/004-k8s-deployment/plan.md](specs/004-k8s-deployment/plan.md) - Technical decisions and structure
- **Implementation Tasks**: [specs/004-k8s-deployment/tasks.md](specs/004-k8s-deployment/tasks.md) - Detailed task breakdown (97 tasks)
- **Data Model**: [specs/004-k8s-deployment/data-model.md](specs/004-k8s-deployment/data-model.md) - Container specifications
- **Contracts**: [specs/004-k8s-deployment/contracts/](specs/004-k8s-deployment/contracts/) - Kubernetes resource specs

### Step 3: AI Chatbot

- **Feature Spec**: [specs/003-step-3-ai-chatbot/spec.md](specs/003-step-3-ai-chatbot/spec.md)
- **Implementation Plan**: [specs/003-step-3-ai-chatbot/plan.md](specs/003-step-3-ai-chatbot/plan.md)

### Step 1: Console App

- **Console README**: [backend/console/README.md](backend/console/README.md)
- **Feature Spec**: [specs/001-step-1-core-features/spec.md](specs/001-step-1-core-features/spec.md)

### Project-Level

- **Constitution**: [.specify/memory/constitution.md](.specify/memory/constitution.md) - Development principles
- **CLAUDE.md**: [CLAUDE.md](CLAUDE.md) - AI assistant context and guidelines

## 🎓 Development Workflow

This project uses **Spec-Driven Development (SDD)** with AI assistance:

1. **Specify** (`/sp.specify`): Define requirements in natural language
2. **Plan** (`/sp.plan`): Create technical implementation plan
3. **Tasks** (`/sp.tasks`): Break down into testable tasks
4. **Implement** (`/sp.implement`): Execute tasks with TDD approach
5. **Validate**: Verify all acceptance criteria met

All development sessions are documented in [history/prompts/](history/prompts/) as Prompt History Records (PHRs).

## 🔧 Troubleshooting

### Kubernetes Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name>  # Check events
kubectl logs <pod-name>          # Check application logs
```

**Metrics-server not ready:**
```bash
# Image pull can take time
kubectl get pods -n kube-system -l k8s-app=metrics-server
# Wait for pod to reach Running status
```

**Cannot access frontend:**
```bash
# Check NodePort service
kubectl get svc todo-app-frontend
# Get Minikube IP
minikube ip
# Access: http://<minikube-ip>:30000
```

**Health checks failing:**
```bash
# Check probe configuration
kubectl describe pod <pod-name> | grep -A 10 "Liveness"
# Port-forward and test manually
kubectl port-forward svc/todo-app-backend 8000:8000
curl http://localhost:8000/health
```

### Database Connection Issues

The Neon database is external (not containerized). Ensure:
- Database URL is correct in values-dev.yaml
- Network connectivity from Minikube to Neon (should work by default)

### Image Pull Issues

Images are built locally using Minikube's Docker daemon:
```bash
# Configure Docker to use Minikube
eval $(minikube docker-env)

# Verify images exist
docker images | grep todo

# Rebuild if needed
docker build -t todo-backend:latest backend/api/
docker build -t todo-frontend:latest frontend/
```

## 🤝 Contributing

This is a demonstration project for Spec-Driven Development. To contribute:

1. Follow the SDD workflow (specify → plan → tasks → implement)
2. Create PHRs for all development sessions
3. Maintain test coverage >90%
4. Update documentation alongside code changes

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built with:
- [OpenAI Agents SDK](https://github.com/openai/swarm) - Multi-agent orchestration
- [OpenAI ChatKit](https://github.com/openai/chatkit) - Chat UI components
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Helm](https://helm.sh/) - Kubernetes package manager
- [Neon](https://neon.tech/) - Serverless PostgreSQL

---

**Last Updated**: 2026-01-25 (Step 4 - Phases 5-6 Complete: Helm Lifecycle + Health Checks)
