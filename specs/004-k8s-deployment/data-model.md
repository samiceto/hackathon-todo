# Container Specifications: Data Model

**Feature**: 004-k8s-deployment
**Date**: 2026-01-24
**Phase**: Phase 1 - Design & Contracts

## Overview

For Step 4 (Kubernetes deployment), the "data model" represents container image specifications rather than database entities. This document defines the structure, build process, and runtime configuration for both backend and frontend Docker containers.

---

## Container Image Entities

### 1. Backend Container Image

**Image Name**: `todo-backend:latest`
**Base Image**: `python:3.13-slim`
**Build Strategy**: Multi-stage (builder + runtime)
**Purpose**: Containerized FastAPI application with OpenAI Agents SDK, MCP server, and Better Auth JWT verification

#### Build Stages

**Stage 1: Builder**

| Aspect | Details |
|--------|---------|
| Base Image | `python:3.13-slim AS builder` |
| Working Directory | `/app` |
| Package Manager | `uv` (installed via pip) |
| Dependencies Source | `pyproject.toml`, `uv.lock` |
| Build Command | `uv sync --frozen --no-dev` |
| Output | Virtual environment in `/app/.venv` |

**Stage 2: Runtime**

| Aspect | Details |
|--------|---------|
| Base Image | `python:3.13-slim` |
| Working Directory | `/app` |
| User | `appuser` (UID 1000, non-root) |
| Copied Artifacts | `.venv` (from builder), `src/` directory |
| Environment Variables | `PATH="/app/.venv/bin:$PATH"` |
| Exposed Port | `8000` |
| Health Check Endpoint | `/health` (returns 200 OK) |
| Startup Command | `uvicorn src.main:app --host 0.0.0.0 --port 8000` |

#### Dockerfile Structure

```dockerfile
# Stage 1: Build stage
FROM python:3.13-slim AS builder
WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev dependencies)
RUN uv sync --frozen --no-dev

# Stage 2: Runtime stage
FROM python:3.13-slim
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ /app/src/

# Set PATH to include virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose application port
EXPOSE 8000

# Health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Start FastAPI application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Environment
.env
.env.local
.env.*.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Docs
README.md
docs/
specs/
history/

# Tests
tests/
```

#### Runtime Environment Variables (Injected by Kubernetes)

| Variable | Source | Example Value |
|----------|--------|---------------|
| `DATABASE_URL` | ConfigMap | `postgresql://user:pass@neon-host/db` |
| `CORS_ORIGINS` | ConfigMap | `http://todo-frontend:3000` |
| `LOG_LEVEL` | ConfigMap | `info` |
| `OPENAI_API_KEY` | Secret | `sk-...` |
| `BETTER_AUTH_SECRET` | Secret | `<secret-value>` |

#### Build Command

```bash
# From repository root
docker build -t todo-backend:latest -f backend/api/Dockerfile backend/api
```

#### Test Command (Local)

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENAI_API_KEY="sk-..." \
  -e BETTER_AUTH_SECRET="..." \
  -e CORS_ORIGINS="http://localhost:3000" \
  todo-backend:latest
```

---

### 2. Frontend Container Image

**Image Name**: `todo-frontend:latest`
**Base Image**: `node:20-alpine`
**Build Strategy**: Multi-stage (deps + builder + runtime)
**Purpose**: Containerized Next.js application with OpenAI ChatKit and Better Auth

#### Build Stages

**Stage 1: Dependencies**

| Aspect | Details |
|--------|---------|
| Base Image | `node:20-alpine AS deps` |
| Working Directory | `/app` |
| Package Manager | `npm` |
| Dependencies Source | `package.json`, `package-lock.json` |
| Install Command | `npm ci` |
| Output | `node_modules/` directory |

**Stage 2: Builder**

| Aspect | Details |
|--------|---------|
| Base Image | `node:20-alpine AS builder` |
| Working Directory | `/app` |
| Copied Artifacts | `node_modules` (from deps), all source files |
| Build Command | `npm run build` |
| Output | `.next/standalone`, `.next/static`, `public/` |

**Stage 3: Runtime**

| Aspect | Details |
|--------|---------|
| Base Image | `node:20-alpine` |
| Working Directory | `/app` |
| User | `nextjs` (UID 1001, non-root) |
| Copied Artifacts | `public/`, `.next/standalone`, `.next/static` |
| Exposed Port | `3000` |
| Startup Command | `node server.js` |

#### Dockerfile Structure

```dockerfile
# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Stage 2: Build application
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source files
COPY . .

# Build Next.js application (standalone output)
RUN npm run build

# Stage 3: Production runtime
FROM node:20-alpine AS runner
WORKDIR /app

# Set production environment
ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Copy standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose application port
EXPOSE 3000

# Set port environment variable
ENV PORT=3000

# Health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start Next.js application
CMD ["node", "server.js"]
```

#### next.config.js (Required Configuration)

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output mode for Docker
  output: 'standalone',

  // Existing configuration (if any)
  // ...
}

module.exports = nextConfig
```

#### .dockerignore

```
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next/
out/

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Testing
coverage/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Docs
README.md
docs/
specs/
history/

# Misc
.DS_Store
Thumbs.db
```

#### Runtime Environment Variables (Injected by Kubernetes)

| Variable | Source | Example Value |
|----------|--------|---------------|
| `NEXT_PUBLIC_API_URL` | ConfigMap | `http://todo-backend:8000` |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | ConfigMap | `<domain-key>` |
| `BETTER_AUTH_SECRET` | Secret | `<secret-value>` |
| `DATABASE_URL` | Secret | `postgresql://user:pass@neon-host/db` |

#### Build Command

```bash
# From repository root
docker build -t todo-frontend:latest -f frontend/Dockerfile frontend
```

#### Test Command (Local)

```bash
docker run --rm -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  -e NEXT_PUBLIC_OPENAI_DOMAIN_KEY="..." \
  -e BETTER_AUTH_SECRET="..." \
  -e DATABASE_URL="postgresql://..." \
  todo-frontend:latest
```

---

## Container Specifications Summary

### Image Size Comparison

| Container | Base Image Size | Final Image Size (Estimated) | Reduction |
|-----------|----------------|------------------------------|-----------|
| Backend | ~120MB (python:3.13-slim) | ~250MB (with dependencies) | 75% vs full python:3.13 (1GB) |
| Frontend | ~170MB (node:20-alpine) | ~200MB (with build artifacts) | 82% vs full node:20 (1.1GB) |

### Security Posture

| Security Measure | Backend | Frontend |
|------------------|---------|----------|
| Non-root user | ✅ appuser (UID 1000) | ✅ nextjs (UID 1001) |
| Minimal base image | ✅ -slim variant | ✅ -alpine variant |
| Multi-stage build | ✅ 2 stages | ✅ 3 stages |
| No secrets in image | ✅ Environment variables | ✅ Environment variables |
| Health checks | ✅ /health endpoint | ✅ Root path check |

### Resource Requirements

| Container | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|------------|-----------|----------------|--------------|
| Backend | 250m | 500m | 256Mi | 512Mi |
| Frontend | 100m | 200m | 128Mi | 256Mi |

---

## Kubernetes Integration

### Deployment References

Both containers will be deployed via Kubernetes Deployments defined in:
- `helm/todo-app/templates/backend-deployment.yaml`
- `helm/todo-app/templates/frontend-deployment.yaml`

### Environment Variable Injection

Configuration injected from:
- **ConfigMaps**: `backend-configmap.yaml`, `frontend-configmap.yaml`
- **Secrets**: `backend-secret.yaml`

Example Deployment snippet:

```yaml
containers:
- name: backend
  image: todo-backend:latest
  ports:
  - containerPort: 8000
  env:
  - name: DATABASE_URL
    valueFrom:
      configMapKeyRef:
        name: todo-backend-config
        key: DATABASE_URL
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: todo-backend-secrets
        key: OPENAI_API_KEY
```

---

## Build and Deployment Workflow

### Local Build (Minikube)

```bash
# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
cd backend/api
docker build -t todo-backend:latest .

# Build frontend image
cd ../../frontend
docker build -t todo-frontend:latest .

# Verify images
docker images | grep todo
```

### Deployment via Helm

```bash
# Deploy to Minikube with development values
helm install todo-app ./helm/todo-app \
  --set backend.secrets.openaiApiKey="sk-..." \
  --set backend.secrets.betterAuthSecret="..." \
  --set frontend.config.openaiDomainKey="..." \
  -f helm/todo-app/values-dev.yaml
```

### Verification

```bash
# Check pod status
kubectl get pods

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# todo-backend-xxxxxxxxx-xxxxx      1/1     Running   0          30s
# todo-backend-xxxxxxxxx-xxxxx      1/1     Running   0          30s
# todo-frontend-xxxxxxxxx-xxxxx     1/1     Running   0          30s
# todo-frontend-xxxxxxxxx-xxxxx     1/1     Running   0          30s

# Check health endpoints
kubectl port-forward svc/todo-backend 8000:8000
curl http://localhost:8000/health  # Should return 200 OK

kubectl port-forward svc/todo-frontend 3000:3000
curl http://localhost:3000  # Should return 200 OK
```

---

## Next Steps

1. ✅ Data model (container specs) complete - **DONE**
2. ⏳ Create contracts/ directory - **NEXT**
3. ⏳ Create quickstart.md
4. ⏳ Generate tasks.md
5. ⏳ Implement Dockerfiles and Helm charts

---

**Data Model Complete**: 2026-01-24
**Reviewed By**: Claude Code (Spec-Driven Development)
