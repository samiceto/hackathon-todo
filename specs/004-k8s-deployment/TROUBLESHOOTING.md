# Kubernetes Deployment Troubleshooting Guide

**Feature**: 004-k8s-deployment
**Date**: 2026-01-25
**Status**: Step 4 - Kubernetes deployment with Minikube and Helm

## Table of Contents

1. [Minikube Issues](#minikube-issues)
2. [Docker Image Issues](#docker-image-issues)
3. [Helm Deployment Issues](#helm-deployment-issues)
4. [Pod Issues](#pod-issues)
5. [Networking Issues](#networking-issues)
6. [Health Check Issues](#health-check-issues)
7. [Resource Issues](#resource-issues)
8. [Database Connection Issues](#database-connection-issues)
9. [Configuration Issues](#configuration-issues)
10. [Common Error Messages](#common-error-messages)

---

## Minikube Issues

### Minikube won't start

**Symptoms**:
```
minikube start
❌  Exiting due to PROVIDER_DOCKER_NOT_RUNNING: ...
```

**Solutions**:
```bash
# 1. Ensure Docker Desktop is running
docker ps  # Should list containers

# 2. Restart Docker Desktop
# (via GUI or system tray)

# 3. Delete and recreate Minikube cluster
minikube delete
minikube start --driver=docker --cpus=2 --memory=4096
```

### Minikube is slow or unresponsive

**Symptoms**:
- Commands hang or take >30 seconds
- Pods stuck in ContainerCreating

**Solutions**:
```bash
# 1. Check system resources
docker stats  # Verify Docker has enough CPU/memory

# 2. Increase Minikube resources
minikube stop
minikube delete
minikube start --driver=docker --cpus=4 --memory=8192

# 3. Restart Docker service (may help on WSL)
# Exit all terminals, restart Docker Desktop
```

### Cannot access Minikube IP

**Symptoms**:
```bash
minikube ip
# Returns nothing or unreachable IP
```

**Solutions**:
```bash
# 1. Verify Minikube is running
minikube status

# 2. Restart Minikube
minikube stop
minikube start

# 3. Use minikube service instead
minikube service todo-app-frontend  # Handles port-forwarding automatically
```

---

## Docker Image Issues

### Images not found (ImagePullBackOff)

**Symptoms**:
```bash
kubectl get pods
# NAME                                 READY   STATUS             RESTARTS   AGE
# todo-app-backend-xxxxx-xxxxx         0/1     ImagePullBackOff   0          30s
```

**Root Cause**: Kubernetes trying to pull images from registry instead of using local images

**Solutions**:
```bash
# 1. Verify images exist in Minikube's Docker environment
minikube ssh "docker images" | grep todo

# Expected output:
# todo-backend   latest   xxxxx   X hours ago   287MB
# todo-frontend  latest   xxxxx   X hours ago   206MB

# 2. If images missing, rebuild with Minikube Docker daemon
eval $(minikube docker-env)
cd backend/api
docker build -t todo-backend:latest .
cd ../../frontend
docker build -t todo-frontend:latest .

# 3. Verify values-dev.yaml has imagePullPolicy: Never
# backend.image.pullPolicy: Never
# frontend.image.pullPolicy: Never

# 4. Delete failing pods to force recreation
kubectl delete pod -l app.kubernetes.io/instance=todo-app
```

### Docker build fails

**Symptoms**:
```
ERROR [internal] load metadata for docker.io/library/python:3.13-slim
```

**Solutions**:
```bash
# 1. Check Docker daemon is running
docker ps

# 2. Ensure Minikube Docker env is configured
eval $(minikube docker-env)
echo $DOCKER_HOST  # Should show minikube path

# 3. Pull base images explicitly
docker pull python:3.13-slim
docker pull node:20-alpine

# 4. Retry build
docker build -t todo-backend:latest backend/api/
```

### Wrong Docker environment

**Symptoms**:
- Images built but not found in Minikube
- `docker images` shows images but Kubernetes can't find them

**Root Cause**: Built images in host Docker instead of Minikube Docker

**Solutions**:
```bash
# 1. Configure shell to use Minikube Docker
eval $(minikube docker-env)

# 2. Verify environment
echo $DOCKER_HOST  # Should show: tcp://127.0.0.1:xxxxx
docker context ls  # Should show: minikube

# 3. Rebuild images
docker build -t todo-backend:latest backend/api/
docker build -t todo-frontend:latest frontend/

# 4. Verify in Minikube
minikube ssh "docker images" | grep todo
```

---

## Helm Deployment Issues

### Helm install fails with validation errors

**Symptoms**:
```
Error: INSTALLATION FAILED: unable to build kubernetes objects from release manifest: ...
```

**Solutions**:
```bash
# 1. Validate Helm chart syntax
helm lint ./helm/todo-app

# 2. Dry-run to see generated manifests
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-dev.yaml \
  --dry-run --debug | less

# 3. Check for required secrets
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-dev.yaml \
  --set backend.secrets.openaiApiKey=$OPENAI_API_KEY \
  --set backend.secrets.betterAuthSecret=your-secret

# 4. Verify values files exist
ls -la helm/todo-app/values*.yaml
```

### Helm upgrade fails

**Symptoms**:
```
Error: UPGRADE FAILED: another operation (install/upgrade/rollback) is in progress
```

**Solutions**:
```bash
# 1. Check release status
helm list

# 2. If stuck in pending state
helm rollback todo-app

# 3. If still stuck, delete and reinstall
helm uninstall todo-app
helm install todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml \
  --set backend.secrets.openaiApiKey=$OPENAI_API_KEY \
  --set backend.secrets.betterAuthSecret=your-secret
```

### Helm rollback doesn't work

**Symptoms**:
- Rollback completes but configuration not restored
- Wrong revision restored

**Solutions**:
```bash
# 1. Check revision history
helm history todo-app

# 2. Rollback to specific revision
helm rollback todo-app 5  # Replace 5 with desired revision number

# 3. Verify rollback
kubectl get configmap todo-app-backend-config -o yaml
```

---

## Pod Issues

### Pods stuck in Pending

**Symptoms**:
```bash
kubectl get pods
# NAME                                 READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxxxx-xxxxx         0/1     Pending   0          2m
```

**Solutions**:
```bash
# 1. Check pod events
kubectl describe pod <pod-name>

# Look for:
# - "Insufficient cpu" → Reduce resource requests
# - "Insufficient memory" → Reduce resource requests or increase Minikube memory

# 2. Check resource requests vs Minikube capacity
kubectl describe node minikube | grep -A 5 "Allocated resources"

# 3. Reduce resource requests in values-dev.yaml temporarily
# backend.resources.requests.cpu: "100m"  # Down from 250m
# backend.resources.requests.memory: "128Mi"  # Down from 256Mi

# 4. Upgrade deployment
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

### Pods crash looping (CrashLoopBackOff)

**Symptoms**:
```bash
kubectl get pods
# NAME                                 READY   STATUS             RESTARTS   AGE
# todo-app-backend-xxxxx-xxxxx         0/1     CrashLoopBackOff   5          5m
```

**Solutions**:
```bash
# 1. Check pod logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # If pod already restarted

# 2. Common causes:
# - Missing environment variables
# - Database connection failed
# - Application startup error

# 3. Check environment variables
kubectl exec <pod-name> -- env | grep -E "(DATABASE|OPENAI|CORS)"

# 4. Check ConfigMap and Secret
kubectl get configmap todo-app-backend-config -o yaml
kubectl get secret todo-app-backend-secrets -o yaml

# 5. Fix configuration and upgrade
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml \
  --set backend.secrets.openaiApiKey=$OPENAI_API_KEY
```

### Pods not Ready (0/1)

**Symptoms**:
```bash
kubectl get pods
# NAME                                 READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxxxx-xxxxx         0/1     Running   0          2m
```

**Root Cause**: Readiness probe failing

**Solutions**:
```bash
# 1. Check readiness probe details
kubectl describe pod <pod-name> | grep -A 10 "Readiness"

# 2. Check pod logs for startup errors
kubectl logs <pod-name>

# 3. Test health endpoint manually
kubectl port-forward <pod-name> 8000:8000
curl http://localhost:8000/health  # Should return {"status": "healthy"}

# 4. Increase initialDelaySeconds if app needs more startup time
# Edit helm/todo-app/templates/backend-deployment.yaml
# readinessProbe.initialDelaySeconds: 30  # Up from 10
```

---

## Networking Issues

### Cannot access frontend via NodePort

**Symptoms**:
```bash
curl http://$(minikube ip):30000
# Connection refused or timeout
```

**Solutions**:
```bash
# 1. Verify service exists and has NodePort
kubectl get svc todo-app-frontend
# Should show: TYPE=NodePort, PORT(S)=3000:30000/TCP

# 2. Check if pod is ready
kubectl get pods -l app.kubernetes.io/component=frontend
# READY should be 1/1

# 3. Use minikube service helper (recommended)
minikube service todo-app-frontend  # Auto-handles port-forwarding

# 4. Check firewall (WSL2 on Windows)
# Add Windows Firewall rule for port 30000 if needed

# 5. Port-forward as alternative
kubectl port-forward svc/todo-app-frontend 3000:3000
# Access: http://localhost:3000
```

### Backend cannot reach database

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions**:
```bash
# 1. Verify database URL in ConfigMap
kubectl get configmap todo-app-backend-config -o yaml | grep DATABASE_URL

# 2. Test connectivity from pod
kubectl exec <backend-pod-name> -- nc -zv <neon-host> 5432
# Should return: succeeded!

# 3. Check if Neon database is accessible
# - Verify database URL is correct
# - Check Neon dashboard for connection limits
# - Verify SSL mode: sslmode=require

# 4. Update DATABASE_URL if needed
# Edit helm/todo-app/values-dev.yaml
# backend.config.databaseUrl: "postgresql://..."
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

### Frontend cannot reach backend

**Symptoms**:
- Frontend loads but API calls fail
- Browser console shows: `ERR_CONNECTION_REFUSED`

**Solutions**:
```bash
# 1. Check frontend config
kubectl get configmap todo-app-frontend-config -o yaml | grep NEXT_PUBLIC_API_URL

# 2. For WSL/Windows, use localhost with port-forward
# Edit helm/todo-app/values-dev.yaml:
# frontend.config.nextPublicApiUrl: "http://localhost:8000"

# 3. Port-forward backend
kubectl port-forward svc/todo-app-backend 8000:8000

# 4. Reload frontend
# Ctrl+Shift+R in browser
```

---

## Health Check Issues

### Liveness probe failing (pod restarts frequently)

**Symptoms**:
```bash
kubectl get pods
# NAME                                 READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxxxx-xxxxx         1/1     Running   15         10m
# ^^^ High RESTARTS count
```

**Solutions**:
```bash
# 1. Check pod events
kubectl describe pod <pod-name> | grep -A 20 "Events"
# Look for: "Liveness probe failed"

# 2. Test health endpoint manually
kubectl exec <pod-name> -- curl -f http://localhost:8000/health

# 3. Check probe timing
kubectl describe pod <pod-name> | grep -A 10 "Liveness"
# If app needs more startup time:
# - Increase initialDelaySeconds
# - Increase timeoutSeconds

# 4. Check application logs for errors
kubectl logs <pod-name>
```

### Readiness probe never succeeds

**Symptoms**:
- Pod shows Running but READY is 0/1
- Service not routing traffic to pod

**Solutions**:
```bash
# 1. Check readiness probe configuration
kubectl describe pod <pod-name> | grep -A 10 "Readiness"

# 2. Test endpoint manually
kubectl exec <pod-name> -- curl -f http://localhost:8000/health

# 3. Common causes:
# - Application not listening on correct port
# - Health endpoint not implemented
# - Database connection blocking startup

# 4. Check application logs
kubectl logs <pod-name>

# 5. Temporarily disable readiness probe to debug
# Comment out readinessProbe in Deployment template
# Deploy and check if pod becomes ready
```

---

## Resource Issues

### Pods killed due to OOMKilled

**Symptoms**:
```bash
kubectl get pods
# NAME                                 READY   STATUS      RESTARTS   AGE
# todo-app-backend-xxxxx-xxxxx         0/1     OOMKilled   3          5m
```

**Root Cause**: Pod exceeded memory limit

**Solutions**:
```bash
# 1. Check memory usage
kubectl top pod <pod-name>

# 2. Increase memory limits
# Edit helm/todo-app/values-dev.yaml:
# backend.resources.limits.memory: "1Gi"  # Up from 512Mi

# 3. Upgrade deployment
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml

# 4. Investigate memory leak
kubectl logs <pod-name> --previous
# Look for excessive database connections or memory growth
```

### CPU throttling

**Symptoms**:
- Application slow to respond
- High latency on API calls

**Solutions**:
```bash
# 1. Check CPU usage
kubectl top pod <pod-name>

# 2. Increase CPU limits
# Edit helm/todo-app/values-dev.yaml:
# backend.resources.limits.cpu: "1000m"  # Up from 500m

# 3. Upgrade deployment
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

### Metrics-server not working

**Symptoms**:
```bash
kubectl top pods
# error: Metrics API not available
```

**Solutions**:
```bash
# 1. Check metrics-server addon status
minikube addons list | grep metrics-server

# 2. Enable if disabled
minikube addons enable metrics-server

# 3. Wait for metrics-server pod to start
kubectl get pods -n kube-system -l k8s-app=metrics-server
# Wait for READY 1/1

# 4. Image pull can take time (5-10 minutes on slow connections)
kubectl describe pod -n kube-system -l k8s-app=metrics-server

# 5. Alternative: use kubectl describe for resource info
kubectl describe pod <pod-name> | grep -A 5 "Limits"
```

---

## Database Connection Issues

### Connection pool exhausted

**Symptoms**:
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Solutions**:
```bash
# 1. Check active connections in Neon dashboard

# 2. Reduce number of replicas temporarily
# Edit helm/todo-app/values-dev.yaml:
# backend.replicas: 1  # Down from 2

# 3. Increase connection pool (if using Step 3 backend)
# Edit backend/api/src/config.py:
# DB_POOL_SIZE = 10  # Up from 5

# 4. Rebuild backend image
docker build -t todo-backend:latest backend/api/

# 5. Restart deployment
kubectl rollout restart deployment/todo-app-backend
```

### SSL/TLS errors

**Symptoms**:
```
SSL error: certificate verify failed
```

**Solutions**:
```bash
# 1. Verify DATABASE_URL has sslmode parameter
kubectl get configmap todo-app-backend-config -o yaml | grep DATABASE_URL
# Should include: ?sslmode=require

# 2. Update if missing
# Edit helm/todo-app/values-dev.yaml:
# backend.config.databaseUrl: "postgresql://...?sslmode=require&channel_binding=require"

# 3. Upgrade deployment
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

---

## Configuration Issues

### Secret not found

**Symptoms**:
```
Error: secret "todo-app-backend-secrets" not found
```

**Solutions**:
```bash
# 1. Verify secrets provided during install/upgrade
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml \
  --set backend.secrets.openaiApiKey=$OPENAI_API_KEY \
  --set backend.secrets.betterAuthSecret=your-secret-here

# 2. Check if secret exists
kubectl get secret todo-app-backend-secrets

# 3. If missing, reinstall
helm uninstall todo-app
helm install todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml \
  --set backend.secrets.openaiApiKey=$OPENAI_API_KEY \
  --set backend.secrets.betterAuthSecret=your-secret
```

### Environment variables not set

**Symptoms**:
```bash
kubectl exec <pod-name> -- env | grep DATABASE_URL
# Returns nothing
```

**Solutions**:
```bash
# 1. Check ConfigMap exists
kubectl get configmap todo-app-backend-config -o yaml

# 2. Check if pod references ConfigMap
kubectl describe pod <pod-name> | grep -A 5 "Environment"

# 3. Restart pod to reload config
kubectl delete pod <pod-name>
# Deployment will recreate pod
```

---

## Common Error Messages

### "Error from server (NotFound): services 'todo-app-backend' not found"

**Cause**: Helm release not installed or service name mismatch

**Solution**:
```bash
# Check all services
kubectl get svc

# Reinstall Helm chart
helm install todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

### "The connection to the server localhost:8080 was refused"

**Cause**: kubectl not configured to use Minikube

**Solution**:
```bash
# Configure kubectl context
kubectl config use-context minikube

# Verify
kubectl cluster-info
```

### "context deadline exceeded"

**Cause**: Kubernetes API server slow or unresponsive

**Solution**:
```bash
# Restart Minikube
minikube stop
minikube start

# Or increase timeout
kubectl get pods --request-timeout=30s
```

---

## General Debugging Workflow

When encountering any issue:

1. **Check pod status**:
   ```bash
   kubectl get pods -l app.kubernetes.io/instance=todo-app
   ```

2. **Describe problematic pod**:
   ```bash
   kubectl describe pod <pod-name>
   ```

3. **Check logs**:
   ```bash
   kubectl logs <pod-name>
   kubectl logs <pod-name> --previous  # If restarted
   ```

4. **Check events**:
   ```bash
   kubectl get events --sort-by='.lastTimestamp' | tail -20
   ```

5. **Verify configuration**:
   ```bash
   kubectl get configmap -o yaml
   kubectl get secret -o yaml
   ```

6. **Test connectivity**:
   ```bash
   kubectl exec <pod-name> -- curl http://localhost:8000/health
   kubectl exec <pod-name> -- env
   ```

7. **Recreate pod**:
   ```bash
   kubectl delete pod <pod-name>
   # Or rollout restart:
   kubectl rollout restart deployment/todo-app-backend
   ```

---

## Getting Help

If issues persist:

1. **Collect diagnostic information**:
   ```bash
   # Save to file
   kubectl get all -o yaml > k8s-state.yaml
   kubectl describe pods > pods-describe.txt
   kubectl logs -l app.kubernetes.io/instance=todo-app > app-logs.txt
   helm list -o yaml > helm-releases.yaml
   ```

2. **Check Minikube logs**:
   ```bash
   minikube logs
   ```

3. **Review documentation**:
   - Quickstart: `specs/004-k8s-deployment/quickstart.md`
   - Plan: `specs/004-k8s-deployment/plan.md`
   - Tasks: `specs/004-k8s-deployment/tasks.md`

4. **Clean slate** (last resort):
   ```bash
   # Delete everything and start fresh
   helm uninstall todo-app
   minikube delete
   minikube start --driver=docker --cpus=2 --memory=4096
   # Then follow quickstart guide
   ```

---

**Last Updated**: 2026-01-25
**Maintained By**: Step 4 implementation team
**Related Docs**: quickstart.md, plan.md, tasks.md
