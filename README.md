# Hackathon Todo 🚀

A progressive task management application built in 5 incremental steps, evolving from a simple CLI tool to a cloud-deployed full-stack application with AI capabilities.

**Current Status**: Step 5 - Advanced Cloud Deployment 🔨 (User Stories 1-9 Complete)

## 📋 Project Overview

This project demonstrates Spec-Driven Development (SDD) by building a complete application through iterative evolution:

- **Step 1** ✅: Console Todo App (Python CLI with in-memory storage)
- **Step 2** ✅: Web Application (FastAPI backend + Next.js frontend + PostgreSQL)
- **Step 3** ✅: AI Chatbot Integration (OpenAI Agents SDK + ChatKit UI)
- **Step 4** ✅: Kubernetes Deployment (Minikube + Helm Charts + Docker)
- **Step 5** 🔨: **Advanced Cloud Deployment** (Event-Driven + Dapr + AWS k3s) - **IN PROGRESS**

## 🎯 Quick Start

### Step 5: Deploy to AWS k3s (Current)

Deploy the full-stack Todo App with advanced features (recurring tasks, reminders, event-driven architecture) to AWS using k3s:

```bash
# Prerequisites: AWS account (free tier), Docker, kubectl, Helm 3.x, Dapr CLI

# 1. Provision AWS infrastructure (see cloud-provisioning.md)
# - Launch EC2 t2.medium instance
# - Install k3s
# - Configure security groups

# 2. Build and push Docker images to Docker Hub
docker login
docker build -t <your-username>/todo-backend:latest ./backend/api
docker build -t <your-username>/todo-frontend:latest ./frontend
docker build -t <your-username>/todo-reminder-service:latest ./backend/reminder-service
docker push <your-username>/todo-backend:latest
docker push <your-username>/todo-frontend:latest
docker push <your-username>/todo-reminder-service:latest

# 3. Configure kubectl for AWS k3s
export KUBECONFIG=~/.kube/config-aws

# 4. Install Dapr
dapr init -k

# 5. Deploy application
./scripts/deploy-to-aws.sh

# 6. Access the application
# Frontend: http://<ELASTIC_IP>:30000
# Backend: http://<ELASTIC_IP>:30001
```

**Detailed Guides**:
- [Cloud Provisioning Guide](specs/005-step-5-cloud-deployment/design/cloud-provisioning.md)
- [Cloud Deployment Guide](specs/005-step-5-cloud-deployment/design/cloud-deployment.md)

### Step 5: Run on Minikube (Local Development)

Deploy the complete Step 5 stack locally with Minikube:

```bash
# Prerequisites: Docker, Minikube 1.30+, kubectl, Helm 3.x, Dapr CLI

# 1. Setup Minikube
./scripts/setup-minikube.sh

# 2. Install Dapr
./scripts/install-dapr-minikube.sh

# 3. Build images
./scripts/build-local-images.sh

# 4. Deploy application
./scripts/deploy-to-minikube.sh

# 5. Run end-to-end tests
./scripts/e2e-test-minikube.sh

# 6. Access the application
minikube service todo-app-frontend
```

**Detailed Guide**: [Minikube Quickstart](specs/005-step-5-cloud-deployment/design/quickstart.md)

### Step 4: Run on Kubernetes (Previous)

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
│   ├── api/              # Steps 2-5: FastAPI application
│   │   ├── Dockerfile    # Step 4-5: Backend container
│   │   └── src/          # API, agents, MCP, auth
│   └── reminder-service/ # Step 5: Event-driven reminder processor
│       ├── Dockerfile    # Reminder service container
│       └── src/          # Event consumers, cron processor
├── frontend/             # Steps 2-5: Next.js application
│   ├── Dockerfile        # Step 4-5: Frontend container
│   └── src/              # UI components, ChatKit
├── helm/                 # Steps 4-5: Helm Charts
│   └── todo-app/         # Kubernetes deployment
│       ├── Chart.yaml
│       ├── values.yaml          # Production defaults
│       ├── values-dev.yaml      # Minikube overrides
│       ├── values-prod-aws.yaml # AWS k3s production
│       ├── templates/           # K8s resource templates
│       └── dependencies/        # Redpanda, Redis YAMLs
├── scripts/              # Step 5: Deployment automation
│   ├── setup-minikube.sh
│   ├── install-dapr-minikube.sh
│   ├── build-local-images.sh
│   ├── deploy-to-minikube.sh
│   ├── deploy-to-aws.sh
│   └── e2e-test-minikube.sh
├── specs/                # Feature specifications
│   ├── 001-step-1-core-features/
│   ├── 003-step-3-ai-chatbot/
│   ├── 004-k8s-deployment/
│   └── 005-step-5-cloud-deployment/
├── history/              # Prompt History Records (PHRs)
└── .specify/             # SDD templates & scripts
```

### Tech Stack

**Step 5 (Current - Advanced Cloud Deployment)**:
- **Event Streaming**: Kafka (Redpanda for local/self-hosted)
- **State Management**: Redis (self-hosted in cluster)
- **Distributed Runtime**: Dapr 1.12+ (Pub/Sub, State Store, Cron, Secrets)
- **Reminder Service**: FastAPI microservice with event consumers
- **Cloud Platform**: AWS EC2 with k3s (free tier compatible)
- **Advanced Features**: Recurring tasks, due dates, reminders, priorities, tags, search/filter/sort

**Step 4 (Kubernetes)**:
- **Container Runtime**: Docker 24+ (multi-stage builds)
- **Orchestration**: Kubernetes 1.28+ (via Minikube or k3s)
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

## 🚀 Step 5: Advanced Features

### Event-Driven Architecture

**Pub/Sub Pattern with Dapr**:
- Task lifecycle events (created, updated, completed, deleted)
- Reminder events published when due
- Asynchronous processing via Kafka topics
- Decoupled microservices communication

**Components**:
- **Backend API**: Publishes events on task operations
- **Reminder Service**: Consumes events, schedules reminders, publishes reminder.due events
- **Kafka (Redpanda)**: Message broker for event streaming
- **Redis**: State store for Dapr actors and caching

### Advanced Task Management

**Recurring Tasks**:
- RRULE-based recurrence patterns (daily, weekly, monthly)
- Automatic task instance generation
- Human-readable recurrence display

**Due Dates & Reminders**:
- Set task deadlines with date/time
- Configurable reminder offsets (e.g., 30 minutes before)
- Reminder events published to Kafka for notification services

**Priorities & Tags**:
- Priority levels: urgent, high, medium, low
- Multiple tags per task (max 10)
- Color-coded priority badges

**Search, Filter & Sort**:
- Full-text search on title and description (PostgreSQL tsvector)
- Multi-criteria filtering (status, priority, tags, due date ranges)
- Flexible sorting (created_at, due_date, priority, title)

### Deployment Options

**Minikube (Local Development)**:
- Single-command deployment scripts
- Self-hosted Kafka (Redpanda) and Redis
- NodePort services for easy access
- End-to-end test automation

**AWS k3s (Production - Free Tier)**:
- Lightweight Kubernetes on EC2 t2.medium
- Neon PostgreSQL (free tier, external)
- Self-hosted Redpanda and Redis in cluster
- Cost: $0/month within AWS free tier (first 12 months)

## 🐳 Kubernetes Deployment (Steps 4-5)

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
| Reminder Service (Step 5) | 1 | CPU: 100m/200m, Memory: 128Mi/256Mi | /health endpoint | ClusterIP (internal only) |
| Redpanda (Kafka - Step 5) | 1 | CPU: 100m/500m, Memory: 512Mi/1Gi | rpk cluster health | ClusterIP (internal only) |
| Redis (Step 5) | 1 | CPU: 50m/200m, Memory: 128Mi/256Mi | redis-cli ping | ClusterIP (internal only) |

### Dapr Components (Step 5)

| Component | Type | Purpose | Configuration |
|-----------|------|---------|---------------|
| pubsub-kafka | pubsub.kafka | Event streaming | Redpanda broker at redpanda:9092 |
| statestore-redis | state.redis | State management | Redis at redis:6379 |
| cron-reminder-processor | bindings.cron | Scheduled tasks | Every 1 minute trigger |
| kubernetes-secrets | secretstores.kubernetes | Secret management | K8s native secrets |

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

### Step 5: End-to-End Tests

```bash
# Minikube deployment tests
./scripts/e2e-test-minikube.sh

# Manual tests
# 1. Create recurring task
curl -X POST http://$(minikube ip):30001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Daily Standup","recurrence_rule":"FREQ=DAILY","priority":"high"}'

# 2. Create task with reminder
curl -X POST http://$(minikube ip):30001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Meeting","due_date":"2026-02-10T14:00:00Z","reminder_offset":1800}'

# 3. Check Kafka topics
kubectl exec -it redpanda-0 -- rpk topic list

# 4. Check Redis connectivity
kubectl exec -it redis-0 -- redis-cli ping

# 5. View reminder service logs
kubectl logs -f -l app.kubernetes.io/component=reminder-service -c reminder-service
```

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

### Step 5: Advanced Cloud Deployment

- **Minikube Quickstart**: [specs/005-step-5-cloud-deployment/design/quickstart.md](specs/005-step-5-cloud-deployment/design/quickstart.md) - Complete local deployment guide
- **Cloud Provisioning**: [specs/005-step-5-cloud-deployment/design/cloud-provisioning.md](specs/005-step-5-cloud-deployment/design/cloud-provisioning.md) - AWS k3s infrastructure setup
- **Cloud Deployment**: [specs/005-step-5-cloud-deployment/design/cloud-deployment.md](specs/005-step-5-cloud-deployment/design/cloud-deployment.md) - Application deployment to AWS
- **Feature Spec**: [specs/005-step-5-cloud-deployment/spec.md](specs/005-step-5-cloud-deployment/spec.md) - 11 user stories with acceptance scenarios
- **Implementation Plan**: [specs/005-step-5-cloud-deployment/plan.md](specs/005-step-5-cloud-deployment/plan.md) - Technical decisions and architecture
- **Implementation Tasks**: [specs/005-step-5-cloud-deployment/tasks.md](specs/005-step-5-cloud-deployment/tasks.md) - Detailed task breakdown

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
- [Dapr](https://dapr.io/) - Distributed application runtime
- [Redpanda](https://redpanda.com/) - Kafka-compatible event streaming
- [OpenAI Agents SDK](https://github.com/openai/swarm) - Multi-agent orchestration
- [OpenAI ChatKit](https://github.com/openai/chatkit) - Chat UI components
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Helm](https://helm.sh/) - Kubernetes package manager
- [k3s](https://k3s.io/) - Lightweight Kubernetes
- [Neon](https://neon.tech/) - Serverless PostgreSQL

---

**Last Updated**: 2026-02-09 (Step 5 - User Stories 1-9 Complete: Advanced Features + Event-Driven Architecture + Cloud Deployment)
