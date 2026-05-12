# Research: Local Kubernetes Deployment

**Feature**: 004-k8s-deployment
**Date**: 2026-01-24
**Phase**: Phase 0 - Research & Discovery

## Overview

This document captures research findings and architectural decisions for deploying the Todo Chatbot application to a local Kubernetes cluster using Minikube, Docker containers, and Helm Charts with AI-assisted DevOps tools.

---

## 1. Docker Multi-Stage Build Best Practices for Python FastAPI Applications

### Decision: Use Python 3.13-slim with Multi-Stage Build

**Rationale**:
- **python:3.13-slim**: Smaller footprint than full python:3.13 image (~120MB vs ~1GB)
- **Alpine considerations**: Rejected due to musl libc compatibility issues with some Python packages
- **Multi-stage build**: Separates build dependencies from runtime, reducing final image size by 50-70%

**Best Practices Applied**:

```dockerfile
# Stage 1: Build stage (install uv and dependencies)
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Stage 2: Runtime stage (minimal production image)
FROM python:3.13-slim
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Copy only necessary files from builder
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Security Considerations**:
- Non-root user (UID 1000) to prevent privilege escalation
- Minimal base image to reduce attack surface
- No build tools in final image

**References**:
- Docker Python Best Practices: https://docs.docker.com/language/python/
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/docker/

---

## 2. Docker Multi-Stage Build Best Practices for Next.js Applications

### Decision: Use Node 20-alpine with Next.js Standalone Output

**Rationale**:
- **node:20-alpine**: Minimal Node.js runtime (~170MB vs ~1.1GB for full node:20)
- **Standalone output**: Next.js 13+ feature that bundles only required dependencies (~80% smaller)
- **Multi-stage build**: Separates dependencies install, build, and runtime stages

**Best Practices Applied**:

```dockerfile
# Stage 1: Dependencies (install all dependencies including devDependencies)
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Builder (build Next.js application)
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Runner (minimal production runtime)
FROM node:20-alpine AS runner
WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only production build artifacts
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
```

**Next.js Configuration** (next.config.js):
```javascript
module.exports = {
  output: 'standalone', // Enable standalone mode
}
```

**References**:
- Next.js Docker Deployment: https://nextjs.org/docs/app/building-your-application/deploying/docker
- Next.js Standalone Output: https://nextjs.org/docs/app/api-reference/next-config-js/output

---

## 3. Kubernetes Deployment Strategies

### Decision: RollingUpdate Strategy with Proper Health Checks

**Rationale**:
- **RollingUpdate**: Default strategy, enables zero-downtime deployments
- **Recreate**: Alternative that terminates all old pods before creating new ones (downtime)
- **Choice**: RollingUpdate for production-ready zero-downtime updates

**Configuration**:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Maximum 1 extra pod during update
    maxUnavailable: 0  # No pods can be unavailable (zero downtime)
```

**Best Practices**:
- `maxUnavailable: 0` ensures always have at least `replicas` pods running
- `maxSurge: 1` controls resource usage during updates (don't spin up too many extra pods)
- Requires proper readiness probes to prevent traffic to new pods until ready

**Alternatives Considered**:
- **Recreate**: Simpler but causes downtime (rejected for production readiness)
- **Blue-Green**: Requires double resources and ingress switching (overkill for Step 4)
- **Canary**: Advanced pattern for Step 5 cloud deployment

**References**:
- Kubernetes Deployment Strategies: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

---

## 4. Health Check Implementation Patterns

### Decision: Separate Liveness and Readiness Probes

**Liveness Probe**: Detects if container is still running (restart if failing)
**Readiness Probe**: Detects if container is ready to serve traffic (remove from load balancer if failing)

**Backend Configuration**:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30  # Wait 30s after startup before first check
  periodSeconds: 10        # Check every 10 seconds
  timeoutSeconds: 5        # Timeout after 5 seconds
  failureThreshold: 3      # Restart after 3 consecutive failures

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10  # Start checking 10s after startup
  periodSeconds: 5         # Check every 5 seconds
  timeoutSeconds: 3        # Timeout after 3 seconds
  failureThreshold: 2      # Mark not ready after 2 consecutive failures
```

**Health Endpoint Requirements**:
- Backend: `/health` returns 200 OK with `{"status": "healthy"}` (already exists in FastAPI app)
- Frontend: Next.js health check via HTTP GET to root path `/` (returns 200 if server running)
- Database: External Neon (not part of health checks, but backend health check should verify DB connection)

**Best Practices**:
- Liveness probe has longer `initialDelaySeconds` to allow application startup
- Readiness probe starts earlier to quickly route traffic when ready
- Different failure thresholds: liveness is more conservative (3 failures) to avoid unnecessary restarts

**References**:
- Kubernetes Liveness/Readiness Probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

---

## 5. Resource Limits and Requests Tuning

### Decision: Conservative Requests, Realistic Limits

**Rationale**:
- **Requests**: Minimum guaranteed resources (used for scheduling)
- **Limits**: Maximum allowed resources (prevents runaway processes)
- **Tuning Strategy**: Start conservative, monitor, adjust based on actual usage

**Backend (FastAPI with OpenAI Agents SDK)**:

```yaml
resources:
  requests:
    memory: "256Mi"  # Minimum guaranteed memory
    cpu: "250m"      # Minimum guaranteed CPU (0.25 cores)
  limits:
    memory: "512Mi"  # Maximum memory (OOMKilled if exceeded)
    cpu: "500m"      # Maximum CPU (throttled if exceeded)
```

**Rationale**:
- FastAPI + Agents SDK + MCP server can be memory-intensive during AI operations
- 512Mi limit provides headroom for conversation processing
- 500m CPU allows responsive API responses while preventing CPU hogging

**Frontend (Next.js)**:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

**Rationale**:
- Next.js standalone output is lightweight
- 256Mi sufficient for serving static assets and SSR
- 200m CPU handles concurrent user requests

**Minikube Resource Requirements**:
- Total needed: 2 backend pods (2 × 512Mi = 1024Mi) + 2 frontend pods (2 × 256Mi = 512Mi) = **1.5Gi memory**
- Minikube configuration: `--memory=4096` provides **4Gi** with ~2.5Gi headroom for system processes

**Monitoring Strategy** (future enhancement):
```bash
kubectl top pods  # View actual resource usage
kubectl describe pod <pod-name>  # Check if pod is being throttled/OOMKilled
```

**References**:
- Kubernetes Resource Management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

---

## 6. Helm Chart Templating Best Practices

### Decision: Single Helm Chart with Modular Templates

**Chart Structure**:

```
helm/todo-app/
├── Chart.yaml              # Chart metadata (name, version, appVersion)
├── values.yaml             # Default configuration
├── values-dev.yaml         # Minikube overrides
├── values-prod.yaml        # Production overrides (future)
└── templates/
    ├── _helpers.tpl        # Template helper functions
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── backend-configmap.yaml
    ├── backend-secret.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── frontend-configmap.yaml
    └── NOTES.txt           # Post-install instructions
```

**Best Practices Applied**:

1. **Semantic Versioning**: Chart version independent of app version
   ```yaml
   # Chart.yaml
   version: 1.0.0        # Chart version
   appVersion: "4.0.0"   # Application version (Step 4)
   ```

2. **Template Helpers** (_helpers.tpl):
   ```yaml
   {{/* Generate full name */}}
   {{- define "todo-app.fullname" -}}
   {{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
   {{- end -}}

   {{/* Common labels */}}
   {{- define "todo-app.labels" -}}
   app.kubernetes.io/name: {{ .Chart.Name }}
   app.kubernetes.io/instance: {{ .Release.Name }}
   app.kubernetes.io/version: {{ .Chart.AppVersion }}
   {{- end -}}
   ```

3. **Values Hierarchy**:
   - `values.yaml`: Production defaults
   - `values-dev.yaml`: Development overrides (reduced replicas, NodePort service)
   - Runtime: `--set` flags for secrets

4. **Conditional Resources**:
   ```yaml
   {{- if .Values.ingress.enabled }}
   # Ingress resource
   {{- end }}
   ```

5. **Notes.txt** for user guidance after deployment

**References**:
- Helm Chart Best Practices: https://helm.sh/docs/chart_best_practices/
- Helm Template Guide: https://helm.sh/docs/chart_template_guide/

---

## 7. ConfigMap and Secret Management Strategies

### Decision: Separate ConfigMaps and Secrets per Service

**ConfigMaps** (non-sensitive configuration):

```yaml
# backend-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "todo-app.fullname" . }}-backend-config
data:
  CORS_ORIGINS: {{ .Values.backend.config.corsOrigins | quote }}
  DATABASE_URL: {{ .Values.backend.config.databaseUrl | quote }}
  LOG_LEVEL: {{ .Values.backend.config.logLevel | default "info" | quote }}
```

**Secrets** (sensitive data):

```yaml
# backend-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-app.fullname" . }}-backend-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: {{ .Values.backend.secrets.openaiApiKey | required "openaiApiKey is required" }}
  BETTER_AUTH_SECRET: {{ .Values.backend.secrets.betterAuthSecret | required "betterAuthSecret is required" }}
```

**Best Practices**:
- **Never commit secrets to Git**: Use `.helmignore` or provide via `--set` at deploy time
- **Required validation**: Use `{{ required }}` for mandatory secrets
- **Base64 encoding**: Kubernetes handles this automatically with `stringData`
- **Least privilege**: Each service gets only its required configuration

**Deployment Command**:
```bash
helm install todo-app ./helm/todo-app \
  --set backend.secrets.openaiApiKey="sk-..." \
  --set backend.secrets.betterAuthSecret="..." \
  --set frontend.config.openaiDomainKey="..." \
  -f values-dev.yaml
```

**Alternatives Considered**:
- **External Secrets Operator**: Too complex for Step 4 (consider for Step 5)
- **Sealed Secrets**: Overkill for local development
- **HashiCorp Vault**: Production-grade solution (future Step 5 enhancement)

**References**:
- Kubernetes Secrets: https://kubernetes.io/docs/concepts/configuration/secret/
- Helm Secrets Management: https://helm.sh/docs/chart_best_practices/data/

---

## 8. Minikube Setup and Configuration

### Decision: Docker Driver with 4GB RAM, 2 CPUs

**Minikube Start Command**:

```bash
minikube start \
  --driver=docker \
  --cpus=2 \
  --memory=4096 \
  --disk-size=20g \
  --kubernetes-version=v1.28.0
```

**Rationale**:
- **docker driver**: Best compatibility with Docker Desktop, faster than VM drivers
- **2 CPUs**: Sufficient for 4 pods (2 backend + 2 frontend) with headroom
- **4096Mi RAM**: Meets 1.5Gi application needs + system overhead (~2.5Gi)
- **20GB disk**: Enough for images, logs, and container layers
- **k8s v1.28**: Stable version with latest features

**Useful Addons**:

```bash
minikube addons enable ingress       # (Optional) Ingress controller
minikube addons enable metrics-server # (Optional) Resource monitoring
minikube addons enable dashboard     # (Optional) Web UI
```

**Docker Integration**:

```bash
# Use Minikube's Docker daemon (avoids pushing images to registry)
eval $(minikube docker-env)

# Now build images directly in Minikube
docker build -t todo-backend:latest ./backend/api
docker build -t todo-frontend:latest ./frontend
```

**Accessing Services**:

```bash
# NodePort service (frontend)
minikube service todo-frontend  # Opens browser automatically

# Port forwarding (backend ClusterIP)
kubectl port-forward svc/todo-backend 8000:8000

# Get Minikube IP
minikube ip  # Use with NodePort (e.g., http://192.168.49.2:30000)
```

**Troubleshooting Commands**:

```bash
minikube status          # Check cluster status
minikube logs            # View cluster logs
minikube ssh             # SSH into Minikube VM
minikube delete          # Delete cluster
minikube stop            # Stop cluster (preserves state)
```

**References**:
- Minikube Documentation: https://minikube.sigs.k8s.io/docs/
- Minikube Docker Driver: https://minikube.sigs.k8s.io/docs/drivers/docker/

---

## 9. AI DevOps Tool Usage: Gordon, kubectl-ai, Kagent

### Decision: Use AI Tools with Standard CLI Fallback

**Docker AI Agent (Gordon)**:

**Capabilities**:
- Dockerfile generation with best practices
- Image optimization suggestions
- Container troubleshooting
- Security vulnerability scanning

**Usage Examples**:
```bash
docker ai "Create a production Dockerfile for FastAPI app with uv"
docker ai "Optimize my Next.js Dockerfile for smallest image size"
docker ai "Why is my container failing to start?"
docker ai "Scan my image for security vulnerabilities"
```

**Availability**: Requires Docker Desktop with Beta features enabled

**Fallback**: Standard `docker build`, manually crafted Dockerfiles based on research

---

**kubectl-ai**:

**Capabilities**:
- Natural language Kubernetes operations
- Manifest generation
- Quick deployments
- Troubleshooting assistance

**Usage Examples**:
```bash
kubectl-ai "deploy the todo frontend with 2 replicas and NodePort service"
kubectl-ai "scale the backend to 3 replicas"
kubectl-ai "why are my pods failing?"
kubectl-ai "create a configmap from this env file"
```

**Installation**:
```bash
# Install kubectl-ai (Node.js required)
npm install -g kubectl-ai
```

**Availability**: Requires OpenAI API key

**Fallback**: Standard `kubectl` commands and manually written YAML manifests

---

**Kagent**:

**Capabilities**:
- Advanced cluster analysis
- Resource optimization suggestions
- Performance bottleneck identification
- Multi-resource insights

**Usage Examples**:
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation for my deployments"
kagent "find performance bottlenecks"
kagent "suggest improvements for my todo-app deployment"
```

**Installation** (varies by implementation):
```bash
# Check Kagent documentation for installation
```

**Availability**: May require separate installation and configuration

**Fallback**: Standard `kubectl top`, `kubectl describe`, manual analysis

---

**AI Tool Strategy**:

| Task | Primary Tool | Fallback |
|------|--------------|----------|
| Dockerfile creation | Gordon | Manual + research.md best practices |
| Image optimization | Gordon | Multi-stage builds (manual) |
| Kubernetes manifest generation | kubectl-ai | Manual YAML + templates |
| Deployment | Helm (standard) | Helm (no AI needed) |
| Troubleshooting | kubectl-ai / Kagent | kubectl logs, describe, events |
| Cluster analysis | Kagent | kubectl top, describe nodes |

**Documentation Requirement**: All AI tool usage MUST be documented in PHRs with:
- Exact prompt used
- AI-generated output
- Manual modifications (if any)
- Success/failure outcome

**References**:
- Docker AI Documentation: https://docs.docker.com/desktop/
- kubectl-ai GitHub: https://github.com/sozercan/kubectl-ai
- Kagent Documentation: (varies by implementation)

---

## 10. Container Security Best Practices

### Decision: Multi-Layered Security Approach

**1. Non-Root Users**:

```dockerfile
# Backend
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Frontend
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
USER nextjs
```

**2. Minimal Base Images**:
- Use `python:3.13-slim` (not full `python:3.13`)
- Use `node:20-alpine` (not full `node:20`)
- Avoid unnecessary packages and build tools in final stage

**3. No Secrets in Images**:
- All secrets via Kubernetes Secrets (environment variables)
- `.dockerignore` excludes `.env` files
- Multi-stage builds exclude source code with secrets

**4. Image Scanning** (future enhancement):
```bash
# Scan images for vulnerabilities
docker scan todo-backend:latest
docker scan todo-frontend:latest
```

**5. Read-Only Filesystem** (optional hardening):
```yaml
securityContext:
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
```

**6. Resource Limits** (prevent DoS):
- CPU limits prevent CPU exhaustion attacks
- Memory limits prevent memory exhaustion attacks

**7. Network Policies** (future enhancement for Step 5):
- Restrict pod-to-pod communication
- Only backend can access database
- Only frontend can access backend

**References**:
- OWASP Docker Security: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- Kubernetes Security Best Practices: https://kubernetes.io/docs/concepts/security/

---

## Summary of Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Backend Base Image | python:3.13-slim | Balance of size and compatibility |
| Frontend Base Image | node:20-alpine | Minimal size, Next.js compatible |
| Build Strategy | Multi-stage builds | Security + reduced image size |
| Deployment Strategy | RollingUpdate | Zero-downtime updates |
| Health Checks | Separate liveness/readiness | Proper restart vs traffic routing |
| Resource Limits | Backend: 512Mi/500m, Frontend: 256Mi/200m | Conservative with headroom |
| Helm Structure | Single chart, modular templates | Atomic deployments |
| Configuration | ConfigMaps + Secrets | Security separation |
| Minikube Config | 2 CPUs, 4GB RAM, docker driver | Sufficient resources |
| AI Tools | Gordon + kubectl-ai + Kagent (optional) | Accelerate workflows |
| Security | Non-root users, minimal images | Defense in depth |

---

## Next Steps

1. ✅ Research complete - **DONE**
2. ⏳ Create data-model.md - **NEXT**
3. ⏳ Create contracts/ specifications
4. ⏳ Create quickstart.md
5. ⏳ Generate tasks.md via `/sp.tasks`
6. ⏳ Implement via `/sp.implement`

---

**Research Complete**: 2026-01-24
**Reviewed By**: Claude Code (Spec-Driven Development)
