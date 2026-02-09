# Minikube Deployment Quickstart Guide

**Step 5: Advanced Cloud Deployment - Local Development Environment**

This guide walks you through deploying the complete Todo App stack (backend, frontend, reminder-service) with Dapr, Kafka/Redpanda, and Redis on a local Minikube cluster.

---

## Prerequisites

### Required Tools

1. **Minikube** (v1.30+)
   ```bash
   # Install on Linux
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube

   # Install on macOS
   brew install minikube

   # Install on Windows
   choco install minikube
   ```

2. **kubectl** (v1.27+)
   ```bash
   # Install on Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

   # Install on macOS
   brew install kubectl

   # Install on Windows
   choco install kubernetes-cli
   ```

3. **Helm** (v3.12+)
   ```bash
   # Install on Linux/macOS
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

   # Install on Windows
   choco install kubernetes-helm
   ```

4. **Docker** (v24.0+)
   - Required for building images
   - Minikube will use Docker as the container runtime

5. **Dapr CLI** (v1.12+)
   ```bash
   # Install on Linux/macOS
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

   # Install on Windows
   powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
   ```

### System Requirements

- **CPU**: 2+ cores (4+ recommended)
- **Memory**: 4GB+ RAM (8GB+ recommended)
- **Disk**: 20GB+ free space
- **OS**: Linux, macOS, or Windows with WSL2

---

## Quick Start (5 Steps)

### Step 1: Setup Minikube

Start Minikube with sufficient resources:

```bash
./scripts/setup-minikube.sh
```

This script will:
- Start Minikube with 4 CPUs and 8GB RAM
- Enable required addons (ingress, metrics-server)
- Configure Docker environment

**Manual alternative:**
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server
```

**Verify Minikube is running:**
```bash
minikube status
kubectl cluster-info
```

Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

### Step 2: Install Dapr

Install Dapr runtime on Minikube:

```bash
./scripts/install-dapr-minikube.sh
```

This script will:
- Initialize Dapr on Kubernetes
- Deploy Dapr control plane components
- Verify Dapr installation

**Manual alternative:**
```bash
dapr init -k
```

**Verify Dapr installation:**
```bash
kubectl get pods -n dapr-system
```

Expected output (3 pods running):
```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-dashboard-xxxxx                     1/1     Running   0          1m
dapr-operator-xxxxx                      1/1     Running   0          1m
dapr-placement-server-0                  1/1     Running   0          1m
dapr-sentry-xxxxx                        1/1     Running   0          1m
dapr-sidecar-injector-xxxxx              1/1     Running   0          1m
```

---

### Step 3: Build Docker Images

Build all application images in Minikube's Docker daemon:

```bash
./scripts/build-local-images.sh
```

This script will:
- Connect to Minikube's Docker daemon
- Build backend image (FastAPI)
- Build frontend image (Next.js)
- Build reminder-service image (FastAPI)

**Manual alternative:**
```bash
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend/api
docker build -t todo-frontend:latest ./frontend
docker build -t todo-reminder-service:latest ./backend/reminder-service
```

**Verify images are built:**
```bash
eval $(minikube docker-env)
docker images | grep todo
```

Expected output:
```
todo-backend              latest    xxxxx    2 minutes ago   287MB
todo-frontend             latest    xxxxx    1 minute ago    206MB
todo-reminder-service     latest    xxxxx    30 seconds ago  250MB
```

---

### Step 4: Deploy Dependencies

Deploy Kafka (Redpanda) and Redis:

```bash
kubectl apply -f helm/todo-app/dependencies/redpanda.yaml
kubectl apply -f helm/todo-app/dependencies/redis.yaml
```

**Wait for dependencies to be ready:**
```bash
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=180s
kubectl wait --for=condition=ready pod -l app=redis --timeout=180s
```

**Verify dependencies:**
```bash
kubectl get pods -l app=redpanda
kubectl get pods -l app=redis
```

Expected output:
```
NAME         READY   STATUS    RESTARTS   AGE
redpanda-0   1/1     Running   0          2m
redis-0      1/1     Running   0          2m
```

---

### Step 5: Deploy Todo App

Deploy the complete application stack using Helm:

```bash
./scripts/deploy-to-minikube.sh
```

This script will:
- Deploy backend, frontend, and reminder-service
- Create Dapr components (Pub/Sub, State Store, Cron, Secrets)
- Configure services and networking
- Wait for all pods to be ready

**Manual alternative:**
```bash
helm install todo-app ./helm/todo-app -f ./helm/todo-app/values-dev.yaml --wait
```

**Verify deployment:**
```bash
kubectl get pods -l app.kubernetes.io/instance=todo-app
```

Expected output (3 pods running, each with 2 containers - app + Dapr sidecar):
```
NAME                                      READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxxx                    2/2     Running   0          2m
todo-app-frontend-xxxxx                   2/2     Running   0          2m
todo-app-reminder-service-xxxxx           2/2     Running   0          2m
```

---

## Accessing the Application

### Get Minikube IP

```bash
minikube ip
```

Example output: `192.168.49.2`

### Access URLs

- **Frontend**: `http://<minikube-ip>:30000`
- **Backend API**: `http://<minikube-ip>:30001`
- **Backend Health**: `http://<minikube-ip>:30001/health`

### Open Frontend in Browser

```bash
minikube service todo-app-frontend
```

This command automatically opens the frontend in your default browser.

### Port Forwarding (Alternative)

If NodePort access doesn't work (e.g., WSL2 networking issues):

```bash
# Forward backend
kubectl port-forward svc/todo-app-backend 8000:8000

# Forward frontend (in another terminal)
kubectl port-forward svc/todo-app-frontend 3000:3000
```

Then access:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

---

## Verification & Testing

### 1. Check Pod Status

```bash
kubectl get pods
```

All pods should show `READY 2/2` (application + Dapr sidecar).

### 2. Check Dapr Components

```bash
kubectl get components
```

Expected output:
```
NAME                       AGE
cron-reminder-processor    5m
kubernetes-secrets         5m
pubsub-kafka              5m
statestore-redis          5m
```

### 3. View Logs

**Backend logs:**
```bash
kubectl logs -f -l app.kubernetes.io/component=backend -c backend
```

**Frontend logs:**
```bash
kubectl logs -f -l app.kubernetes.io/component=frontend -c frontend
```

**Reminder service logs:**
```bash
kubectl logs -f -l app.kubernetes.io/component=reminder-service -c reminder-service
```

**Dapr sidecar logs:**
```bash
kubectl logs -f -l app.kubernetes.io/component=backend -c daprd
```

### 4. Test Backend Health

```bash
MINIKUBE_IP=$(minikube ip)
curl http://$MINIKUBE_IP:30001/health
```

Expected response:
```json
{"status": "healthy"}
```

### 5. Test Task Creation

```bash
MINIKUBE_IP=$(minikube ip)
curl -X POST http://$MINIKUBE_IP:30001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "Testing Minikube deployment"}'
```

### 6. Monitor Resources

```bash
kubectl top pods -l app.kubernetes.io/instance=todo-app
```

---

## Troubleshooting

### Pods Not Starting

**Check pod status:**
```bash
kubectl describe pod <pod-name>
```

**Common issues:**
- **ImagePullBackOff**: Images not built in Minikube's Docker daemon
  - Solution: Run `./scripts/build-local-images.sh` again
- **CrashLoopBackOff**: Application error or missing dependencies
  - Solution: Check logs with `kubectl logs <pod-name> -c <container-name>`

### Dapr Sidecar Not Injected

**Check annotations:**
```bash
kubectl get pod <pod-name> -o jsonpath='{.metadata.annotations}'
```

Should include `dapr.io/enabled: "true"`.

**Solution:** Verify Dapr is installed:
```bash
kubectl get pods -n dapr-system
```

### Dependencies Not Ready

**Check Redpanda:**
```bash
kubectl logs -l app=redpanda
kubectl exec -it redpanda-0 -- rpk cluster info
```

**Check Redis:**
```bash
kubectl logs -l app=redis
kubectl exec -it redis-0 -- redis-cli ping
```

### Cannot Access Frontend

**WSL2 users:** Minikube IP may not be accessible from Windows host.

**Solution:** Use port forwarding:
```bash
kubectl port-forward svc/todo-app-frontend 3000:3000
```

Then access `http://localhost:3000`.

### Database Connection Issues

**Check backend logs:**
```bash
kubectl logs -l app.kubernetes.io/component=backend -c backend | grep -i database
```

**Verify DATABASE_URL secret:**
```bash
kubectl get secret backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Dapr Component Errors

**Check component status:**
```bash
kubectl describe component pubsub-kafka
kubectl describe component statestore-redis
```

**Verify Dapr logs:**
```bash
kubectl logs -l app.kubernetes.io/component=backend -c daprd
```

---

## Useful Commands

### Deployment Management

```bash
# Check Helm release status
helm status todo-app

# View Helm values
helm get values todo-app

# Upgrade deployment
helm upgrade todo-app ./helm/todo-app -f ./helm/todo-app/values-dev.yaml

# Rollback deployment
helm rollback todo-app

# Uninstall application
helm uninstall todo-app
```

### Pod Management

```bash
# Get all pods
kubectl get pods

# Get pods with labels
kubectl get pods -l app.kubernetes.io/instance=todo-app

# Describe pod
kubectl describe pod <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh

# View pod events
kubectl get events --sort-by='.lastTimestamp'
```

### Service Management

```bash
# Get all services
kubectl get svc

# Get service details
kubectl describe svc todo-app-frontend

# Test service connectivity
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl http://todo-app-backend:8000/health
```

### Logs & Debugging

```bash
# Stream logs from all backend pods
kubectl logs -f -l app.kubernetes.io/component=backend --all-containers=true

# Get logs from previous container (after crash)
kubectl logs <pod-name> -c <container-name> --previous

# View logs from last 1 hour
kubectl logs <pod-name> -c <container-name> --since=1h

# Save logs to file
kubectl logs <pod-name> -c <container-name> > pod-logs.txt
```

### Resource Monitoring

```bash
# View resource usage
kubectl top pods
kubectl top nodes

# Watch pod status
watch kubectl get pods

# View cluster info
kubectl cluster-info
kubectl get nodes
```

---

## Cleanup

### Uninstall Application

```bash
helm uninstall todo-app
```

### Delete Dependencies

```bash
kubectl delete -f helm/todo-app/dependencies/redpanda.yaml
kubectl delete -f helm/todo-app/dependencies/redis.yaml
```

### Uninstall Dapr

```bash
dapr uninstall -k
```

### Stop Minikube

```bash
minikube stop
```

### Delete Minikube Cluster

```bash
minikube delete
```

This removes all data and frees up disk space.

---

## Next Steps

After successfully deploying to Minikube:

1. **Test Advanced Features**:
   - Create recurring tasks
   - Set due dates and reminders
   - Add priorities and tags
   - Test search and filtering

2. **Explore Event-Driven Architecture**:
   - Monitor Kafka topics: `kubectl exec -it redpanda-0 -- rpk topic list`
   - View event flow in Dapr dashboard: `dapr dashboard -k`

3. **Performance Testing**:
   - Load test with multiple concurrent users
   - Monitor resource usage with `kubectl top pods`

4. **Prepare for Cloud Deployment**:
   - Review cloud provisioning guide: `specs/005-step-5-cloud-deployment/design/cloud-provisioning.md`
   - Set up CI/CD pipeline: `specs/005-step-5-cloud-deployment/design/cicd-pipeline.md`

---

## Additional Resources

- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Dapr Documentation**: https://docs.dapr.io/
- **Helm Documentation**: https://helm.sh/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/

---

**Last Updated**: 2026-02-09
**Version**: Step 5 - User Story 8 (Minikube Deployment)
