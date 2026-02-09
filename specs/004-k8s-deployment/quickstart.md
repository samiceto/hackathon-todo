# Quickstart Guide: Deploy Todo Chatbot to Minikube

**Feature**: 004-k8s-deployment
**Date**: 2026-01-24
**Phase**: Phase 1 - Design & Contracts
**Estimated Time**: 30 minutes (first-time setup)

## Overview

This guide walks you through deploying the Todo Chatbot application to a local Kubernetes cluster using Minikube and Helm Charts. By the end, you'll have a fully functional application running in containers with proper orchestration, health checks, and configuration management.

---

## Prerequisites

### Required Software

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | 24+ | https://www.docker.com/products/docker-desktop |
| Minikube | 1.32+ | https://minikube.sigs.k8s.io/docs/start/ |
| kubectl | 1.28+ | Included with Docker Desktop or standalone |
| Helm | 3.x | https://helm.sh/docs/intro/install/ |

### Optional AI DevOps Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| Docker AI (Gordon) | AI-assisted Docker operations | Enable in Docker Desktop Beta features |
| kubectl-ai | AI-assisted Kubernetes operations | `npm install -g kubectl-ai` |
| Kagent | Advanced cluster analysis | See Kagent documentation |

### Required Credentials

- **OpenAI API Key**: For chatbot functionality (`sk-...`)
- **Better Auth Secret**: Shared secret for JWT verification
- **Neon Database URL**: PostgreSQL connection string
- **OpenAI Domain Key**: For ChatKit frontend (optional for localhost)

---

## Step 1: Verify Prerequisites

### Check Docker Installation

```bash
docker --version
# Expected: Docker version 24.0.0 or higher

docker ps
# Should list running containers (or be empty)
```

### Check Minikube Installation

```bash
minikube version
# Expected: minikube version: v1.32.0 or higher
```

### Check kubectl Installation

```bash
kubectl version --client
# Expected: Client Version: v1.28.0 or higher
```

### Check Helm Installation

```bash
helm version
# Expected: version.BuildInfo{Version:"v3.x.x"}
```

---

## Step 2: Start Minikube Cluster

### Start Cluster with Recommended Configuration

```bash
# Start Minikube with Docker driver, 2 CPUs, 4GB RAM
minikube start --driver=docker --cpus=2 --memory=4096 --disk-size=20g

# Expected output:
# 😄  minikube v1.32.0 on Linux
# ✨  Using the docker driver based on user configuration
# 👍  Starting control plane node minikube in cluster minikube
# 🚜  Pulling base image ...
# 🔥  Creating docker container (CPUs=2, Memory=4096MB) ...
# 🐳  Preparing Kubernetes v1.28.0 on Docker 24.0.0 ...
# 🔎  Verifying Kubernetes components...
# 🌟  Enabled addons: storage-provisioner, default-storageclass
# 🏄  Done! kubectl is now configured to use "minikube" cluster
```

### Verify Cluster Status

```bash
minikube status
# Expected:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured

kubectl cluster-info
# Expected:
# Kubernetes control plane is running at https://127.0.0.1:xxxxx
```

### Optional: Enable Addons

```bash
# Ingress controller (for advanced routing - optional)
minikube addons enable ingress

# Metrics server (for resource monitoring - optional)
minikube addons enable metrics-server

# Dashboard (for web UI - optional)
minikube addons enable dashboard
```

---

## Step 3: Configure Docker to Use Minikube's Docker Daemon

This step allows you to build Docker images directly in Minikube's environment, avoiding the need to push to a registry.

```bash
# Configure shell to use Minikube's Docker daemon
eval $(minikube docker-env)

# Verify configuration
docker ps
# Should now show Minikube's containers (kube-proxy, coredns, etc.)
```

**Note**: This configuration is session-specific. You'll need to run `eval $(minikube docker-env)` in each new terminal session.

---

## Step 4: Build Container Images

### Build Backend Image

```bash
# Navigate to backend directory
cd backend/api

# Build Docker image
docker build -t todo-backend:latest .

# Verify image was created
docker images | grep todo-backend
# Expected: todo-backend   latest   <image-id>   <time>   ~250MB
```

**Using Gordon (Docker AI) - Optional**:

```bash
# Get Dockerfile suggestions
docker ai "Review my Dockerfile for best practices"

# Build with optimization suggestions
docker ai "Build an optimized image for my FastAPI app"
```

### Build Frontend Image

```bash
# Navigate to frontend directory
cd ../../frontend

# Build Docker image
docker build -t todo-frontend:latest .

# Verify image was created
docker images | grep todo-frontend
# Expected: todo-frontend   latest   <image-id>   <time>   ~200MB
```

### Verify Both Images

```bash
docker images | grep todo
# Expected output:
# todo-backend    latest   xxxxx   X minutes ago   ~250MB
# todo-frontend   latest   xxxxx   X minutes ago   ~200MB
```

---

## Step 5: Prepare Helm Chart Values

### Create Secrets File (DO NOT COMMIT TO GIT)

Create a file `helm/todo-app/secrets.yaml` with your actual secret values:

```yaml
# secrets.yaml - DO NOT COMMIT THIS FILE
backend:
  secrets:
    openaiApiKey: "sk-proj-..."  # Your OpenAI API key
    betterAuthSecret: "your-shared-secret-here"  # Generate a secure random string

frontend:
  config:
    openaiDomainKey: "your-openai-domain-key"  # Get from OpenAI platform
```

**Generate Better Auth Secret**:

```bash
# Generate a secure random secret
openssl rand -base64 32
# Copy the output to betterAuthSecret in secrets.yaml
```

### Review Development Values

Check `helm/todo-app/values-dev.yaml` for Minikube-specific settings:

```yaml
backend:
  replicas: 1  # Reduced for local development
  config:
    corsOrigins: "http://localhost:30000"
    databaseUrl: "postgresql://user:pass@your-neon-host/todo_db"

frontend:
  replicas: 1  # Reduced for local development
  service:
    type: NodePort
    nodePort: 30000  # Access frontend at http://<minikube-ip>:30000
```

**Update Database URL**: Replace with your Neon PostgreSQL connection string.

---

## Step 6: Deploy with Helm

### Install Helm Chart

```bash
# From repository root
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-dev.yaml \
  -f helm/todo-app/secrets.yaml

# Expected output:
# NAME: todo-app
# LAST DEPLOYED: <timestamp>
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
# [Post-install instructions will appear here]
```

**Alternative: Using --set Flags** (more secure, no secrets file):

```bash
helm install todo-app ./helm/todo-app \
  --set backend.secrets.openaiApiKey="sk-..." \
  --set backend.secrets.betterAuthSecret="..." \
  --set frontend.config.openaiDomainKey="..." \
  -f helm/todo-app/values-dev.yaml
```

### Using kubectl-ai (Optional)

```bash
kubectl-ai "deploy the todo application with 1 replica for backend and frontend"
```

---

## Step 7: Verify Deployment

### Check Pods Status

```bash
kubectl get pods

# Expected output (after ~30-60 seconds):
# NAME                                READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxxxxxxxx-xxxxx    1/1     Running   0          45s
# todo-app-frontend-xxxxxxxxx-xxxxx   1/1     Running   0          45s
```

**If pods are not Running**, check logs:

```bash
# Get pod name
kubectl get pods

# View logs for troubleshooting
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

**Using kubectl-ai for troubleshooting**:

```bash
kubectl-ai "why are my pods not running?"
```

**Using Kagent for analysis**:

```bash
kagent "analyze cluster health"
```

### Check Services

```bash
kubectl get svc

# Expected output:
# NAME                   TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
# todo-app-backend       ClusterIP   10.96.xxx.xxx    <none>        8000/TCP         1m
# todo-app-frontend      NodePort    10.96.xxx.xxx    <none>        3000:30000/TCP   1m
```

### Test Backend Health Endpoint

```bash
# Port forward to access backend
kubectl port-forward svc/todo-app-backend 8000:8000

# In another terminal, test health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Test Frontend Access

```bash
# Get Minikube IP
minikube ip
# Example: 192.168.49.2

# Open frontend in browser (using Minikube service helper)
minikube service todo-app-frontend

# This will automatically open your browser to http://<minikube-ip>:30000
```

**Manual access**:

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Open in browser
open http://$MINIKUBE_IP:30000
# Or visit http://192.168.49.2:30000 manually
```

---

## Step 8: Test Application Features

### Test Tasks (Traditional UI)

1. Navigate to `http://<minikube-ip>:30000/tasks`
2. Create a new task
3. Mark task as complete
4. Update task details
5. Delete task

### Test Chatbot (AI Interface)

1. Navigate to `http://<minikube-ip>:30000/chat`
2. Send message: "Add a task to buy groceries"
3. Verify task was created: "Show me all my tasks"
4. Mark complete: "Mark task 1 as complete"
5. Delete task: "Delete the groceries task"

---

## Step 9: Monitor Resources

### View Resource Usage

```bash
# Enable metrics server (if not already enabled)
minikube addons enable metrics-server

# Wait 1 minute for metrics to collect, then:
kubectl top pods

# Expected output:
# NAME                                CPU(cores)   MEMORY(bytes)
# todo-app-backend-xxxxxxxxx-xxxxx    50m          256Mi
# todo-app-frontend-xxxxxxxxx-xxxxx   20m          128Mi
```

### Check Resource Limits

```bash
kubectl describe pod <backend-pod-name> | grep -A 5 "Limits"
# Expected:
#   Limits:
#     cpu:     500m
#     memory:  512Mi
#   Requests:
#     cpu:        250m
#     memory:     256Mi
```

---

## Step 9.1: Verify Health Checks

### Health Check Configuration

Both backend and frontend deployments are configured with liveness and readiness probes for automatic health monitoring and self-healing.

**Backend Health Checks** (`/health` endpoint):

```bash
# View backend liveness probe configuration
kubectl get deployment todo-app-backend -o yaml | grep -A 10 "livenessProbe:"

# Expected:
#   livenessProbe:
#     httpGet:
#       path: /health
#       port: 8000
#     initialDelaySeconds: 30
#     periodSeconds: 10
#     timeoutSeconds: 5
#     failureThreshold: 3
```

**Frontend Health Checks** (`/` endpoint):

```bash
# View frontend liveness probe configuration
kubectl get deployment todo-app-frontend -o yaml | grep -A 10 "livenessProbe:"

# Expected:
#   livenessProbe:
#     httpGet:
#       path: /
#       port: 3000
#     initialDelaySeconds: 30
#     periodSeconds: 10
#     timeoutSeconds: 5
#     failureThreshold: 3
```

### Test Auto-Restart (Liveness Probe)

Kubernetes automatically restarts pods that fail liveness checks:

```bash
# Delete a backend pod to simulate failure
kubectl delete pod -l app.kubernetes.io/component=backend

# Watch Kubernetes automatically recreate the pod
kubectl get pods -w -l app.kubernetes.io/component=backend

# Expected: New pod created and running within 30 seconds
# NAME                                READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxxxxxxxx-xxxxx    1/1     Running   0          15s
```

### Verify Readiness Probes

Readiness probes ensure traffic is only routed to healthy pods:

```bash
# Check readiness probe status
kubectl describe pod -l app.kubernetes.io/component=backend | grep "Readiness:"

# Expected:
# Readiness: http-get http://:http/health delay=10s timeout=3s period=5s #success=1 #failure=2
```

**What happens during deployment:**
1. New pod starts (READY: 0/1)
2. Readiness probe waits 10 seconds (initialDelaySeconds)
3. Probe checks `/health` every 5 seconds
4. After first success, pod is marked READY (1/1)
5. Service starts routing traffic to the pod

**What happens on failure:**
1. Readiness probe fails 2 consecutive times
2. Pod marked as not ready (READY: 0/1)
3. Service stops routing traffic to the pod
4. If liveness probe also fails 3 times, Kubernetes restarts the pod

### Verify Resource Limits

Resource limits prevent pods from consuming excessive resources:

```bash
# Check backend resource limits
kubectl describe pod -l app.kubernetes.io/component=backend | grep -A 5 "Limits:"

# Expected:
#   Limits:
#     cpu:     500m      # Maximum CPU usage
#     memory:  512Mi     # Maximum memory usage
#   Requests:
#     cpu:      250m     # Guaranteed CPU allocation
#     memory:   256Mi    # Guaranteed memory allocation

# Check frontend resource limits
kubectl describe pod -l app.kubernetes.io/component=frontend | grep -A 5 "Limits:"

# Expected:
#   Limits:
#     cpu:     200m      # Maximum CPU usage
#     memory:  256Mi     # Maximum memory usage
#   Requests:
#     cpu:      100m     # Guaranteed CPU allocation
#     memory:   128Mi    # Guaranteed memory allocation
```

**What resource limits do:**
- **Requests**: Kubernetes guarantees this amount of resources for the pod
- **Limits**: Pod is throttled (CPU) or killed/restarted (memory) if it exceeds this limit

### Monitor Real-Time Resource Usage

```bash
# Enable metrics-server (if not already enabled)
minikube addons enable metrics-server

# Wait 1-2 minutes for metrics to collect, then check usage
kubectl top pods -l app.kubernetes.io/instance=todo-app

# Expected output (example):
# NAME                                 CPU(cores)   MEMORY(bytes)
# todo-app-backend-xxxxxxxxx-xxxxx     45m          240Mi
# todo-app-frontend-xxxxxxxxx-xxxxx    18m          110Mi
```

**Verify resource usage is within limits:**
- Backend: CPU < 500m, Memory < 512Mi ✅
- Frontend: CPU < 200m, Memory < 256Mi ✅

**Note**: If metrics-server pod is slow to start (ContainerCreating status), wait a few minutes for the image to pull. This is normal on first-time setup.

---

## Step 10: Update Deployment

### Rolling Update Test

```bash
# Make a change to values (e.g., increase replicas in values-dev.yaml)
# backend.replicas: 2

# Upgrade deployment
helm upgrade todo-app ./helm/todo-app \
  -f helm/todo-app/values-dev.yaml \
  -f helm/todo-app/secrets.yaml

# Watch pods during rolling update
kubectl get pods -w

# Expected: New pods created, old pods terminated gracefully (zero downtime)
```

### Rollback Test

```bash
# Rollback to previous version
helm rollback todo-app

# Verify rollback
helm history todo-app
```

---

## Common Operations

### View Logs

```bash
# View logs for specific pod
kubectl logs -f <pod-name>

# View logs for all backend pods
kubectl logs -l app.kubernetes.io/component=backend --all-containers=true

# View logs from previous container (if pod crashed)
kubectl logs <pod-name> --previous
```

### Restart Deployment

```bash
# Restart backend deployment
kubectl rollout restart deployment todo-app-backend

# Restart frontend deployment
kubectl rollout restart deployment todo-app-frontend
```

### Scale Deployment

```bash
# Scale backend to 3 replicas
kubectl scale deployment todo-app-backend --replicas=3

# Verify scaling
kubectl get pods
```

**Using kubectl-ai**:

```bash
kubectl-ai "scale the backend to 3 replicas"
```

### Access Dashboard (Optional)

```bash
# Start Kubernetes dashboard
minikube dashboard

# This will open a web browser with the Kubernetes dashboard
```

---

## Cleanup

### Delete Deployment

```bash
# Uninstall Helm release
helm uninstall todo-app

# Verify deletion
kubectl get pods
# Should show no todo-app pods
```

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes all data)
minikube delete
```

### Reset Docker Environment

```bash
# Unset Minikube Docker daemon
eval $(minikube docker-env -u)

# Verify back to host Docker
docker ps
# Should show host containers (not Minikube containers)
```

---

## Troubleshooting

### Pods Not Starting

**Symptom**: Pods stuck in `Pending`, `ImagePullBackOff`, or `CrashLoopBackOff`

**Solutions**:

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common issues:
# 1. ImagePullBackOff: Image not found in Minikube's Docker
#    Solution: Ensure you ran `eval $(minikube docker-env)` before building

# 2. CrashLoopBackOff: Container exiting on startup
#    Solution: Check logs with `kubectl logs <pod-name>`

# 3. Pending: Insufficient resources
#    Solution: Increase Minikube resources or reduce pod replicas
```

### Cannot Access Frontend

**Symptom**: Browser cannot reach `http://<minikube-ip>:30000`

**Solutions**:

```bash
# Verify NodePort service
kubectl get svc todo-app-frontend

# Check if Minikube is running
minikube status

# Use Minikube service helper
minikube service todo-app-frontend --url
# Open the returned URL in browser
```

### Database Connection Errors

**Symptom**: Backend logs show database connection failures

**Solutions**:

```bash
# Verify DATABASE_URL is correct
kubectl get configmap todo-app-backend-config -o yaml

# Test database connection from within pod
kubectl exec -it <backend-pod-name> -- python -c "import psycopg2; conn = psycopg2.connect('postgresql://...')"

# Check if Neon database is accessible from Minikube
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- <neon-host>
```

### Out of Memory Errors

**Symptom**: Pods being OOMKilled (Out Of Memory)

**Solutions**:

```bash
# Check memory usage
kubectl top pods

# Increase memory limits in values.yaml
# backend.resources.limits.memory: "1Gi"

# Upgrade deployment
helm upgrade todo-app ./helm/todo-app -f values-dev.yaml
```

---

## Next Steps

1. ✅ Application deployed to Minikube - **COMPLETE**
2. ⏳ Implement CI/CD pipelines (Step 5)
3. ⏳ Deploy to cloud Kubernetes (Step 5)
4. ⏳ Add monitoring and logging (Step 5)
5. ⏳ Implement auto-scaling (Step 5)

---

## Useful Commands Reference

```bash
# Minikube
minikube start --cpus=2 --memory=4096
minikube stop
minikube delete
minikube status
minikube dashboard
minikube service <service-name>

# Docker (with Minikube)
eval $(minikube docker-env)
docker build -t <image>:<tag> .
docker images

# kubectl
kubectl get pods
kubectl get svc
kubectl get deployments
kubectl logs -f <pod-name>
kubectl describe pod <pod-name>
kubectl exec -it <pod-name> -- /bin/sh
kubectl port-forward svc/<service-name> <local-port>:<service-port>

# Helm
helm install <release> <chart> -f values.yaml
helm upgrade <release> <chart>
helm rollback <release>
helm uninstall <release>
helm list
helm history <release>

# AI Tools (Optional)
docker ai "<prompt>"
kubectl-ai "<prompt>"
kagent "<prompt>"
```

---

**Quickstart Guide Complete**: 2026-01-24
**Reviewed By**: Claude Code (Spec-Driven Development)
**Estimated Completion Time**: 30 minutes
