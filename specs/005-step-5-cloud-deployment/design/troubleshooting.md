# Troubleshooting Guide - Step 5 Deployment

**Step 5: Advanced Cloud Deployment - Common Issues and Solutions**

This guide covers common issues encountered during Minikube and AWS k3s deployment, along with step-by-step solutions.

---

## Table of Contents

1. [Minikube Issues](#minikube-issues)
2. [Dapr Issues](#dapr-issues)
3. [Docker Image Issues](#docker-image-issues)
4. [Helm Deployment Issues](#helm-deployment-issues)
5. [Pod Startup Issues](#pod-startup-issues)
6. [Networking Issues](#networking-issues)
7. [Database Connection Issues](#database-connection-issues)
8. [Kafka/Redpanda Issues](#kafkaredpanda-issues)
9. [Redis Issues](#redis-issues)
10. [AWS k3s Issues](#aws-k3s-issues)
11. [Performance Issues](#performance-issues)

---

## Minikube Issues

### Issue: Minikube won't start

**Symptoms:**
```
❌ Exiting due to PROVIDER_DOCKER_NOT_RUNNING: "docker version --format -" exit status 1
```

**Solution:**
```bash
# Check Docker is running
docker ps

# If not running, start Docker Desktop (Windows/Mac)
# Or start Docker daemon (Linux)
sudo systemctl start docker

# Restart Minikube
minikube delete
minikube start --cpus=4 --memory=8192
```

---

### Issue: Insufficient resources

**Symptoms:**
```
❌ Exiting due to RSRC_INSUFFICIENT_CORES: Requested cpu count 4 is greater than available cpus: 2
```

**Solution:**
```bash
# Reduce resource requirements
minikube start --cpus=2 --memory=4096

# Or increase Docker Desktop resources
# Docker Desktop → Settings → Resources → Increase CPU/Memory
```

---

### Issue: Minikube IP not accessible (WSL2)

**Symptoms:**
- Cannot access `http://$(minikube ip):30000` from Windows browser
- Connection timeout

**Solution:**
```bash
# Use port forwarding instead
kubectl port-forward svc/todo-app-frontend 3000:3000
kubectl port-forward svc/todo-app-backend 8000:8000

# Access via localhost
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## Dapr Issues

### Issue: Dapr not installed

**Symptoms:**
```
❌ Error: Dapr is not installed
```

**Solution:**
```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init -k

# Verify installation
kubectl get pods -n dapr-system
```

---

### Issue: Dapr sidecar not injected

**Symptoms:**
- Pods show `READY 1/1` instead of `READY 2/2`
- No `daprd` container in pod

**Solution:**
```bash
# Check Dapr annotations
kubectl get pod <pod-name> -o jsonpath='{.metadata.annotations}'

# Should include:
# dapr.io/enabled: "true"
# dapr.io/app-id: "backend"
# dapr.io/app-port: "8000"

# If missing, check Helm values
helm get values todo-app

# Verify dapr.enabled is true
# Redeploy if needed
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

---

### Issue: Dapr component not found

**Symptoms:**
```
error: component pubsub-kafka not found
```

**Solution:**
```bash
# Check Dapr components
kubectl get components

# If missing, check Helm templates
ls helm/todo-app/templates/dapr-*.yaml

# Verify dapr.enabled in values
grep -A 5 "dapr:" helm/todo-app/values-dev.yaml

# Redeploy Helm chart
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

---

## Docker Image Issues

### Issue: ImagePullBackOff

**Symptoms:**
```
Failed to pull image "todo-backend:latest": rpc error: code = Unknown desc = Error response from daemon: pull access denied
```

**Solution for Minikube:**
```bash
# Ensure using Minikube's Docker daemon
eval $(minikube docker-env)

# Verify environment
echo $DOCKER_HOST
# Should show: tcp://192.168.49.2:2376 (or similar)

# Rebuild images
./scripts/build-local-images.sh

# Verify images exist
docker images | grep todo

# Update Helm values to use Never pull policy
# values-dev.yaml should have:
# image:
#   pullPolicy: Never
```

**Solution for AWS k3s:**
```bash
# Check Docker Hub credentials
docker login

# Verify image exists on Docker Hub
docker pull <your-username>/todo-backend:latest

# Check image name in Helm values
grep "repository:" helm/todo-app/values-prod-aws.yaml

# Ensure it matches your Docker Hub username
```

---

### Issue: Image architecture mismatch

**Symptoms:**
```
exec format error
```

**Solution:**
```bash
# Build for correct architecture
docker build --platform linux/amd64 -t todo-backend:latest ./backend/api

# For multi-arch support
docker buildx build --platform linux/amd64,linux/arm64 -t todo-backend:latest ./backend/api
```

---

## Helm Deployment Issues

### Issue: Helm install fails with validation error

**Symptoms:**
```
Error: INSTALLATION FAILED: unable to build kubernetes objects from release manifest
```

**Solution:**
```bash
# Validate Helm chart
helm lint ./helm/todo-app

# Check template rendering
helm template todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml

# Fix any YAML syntax errors
# Common issues:
# - Missing quotes around values
# - Incorrect indentation
# - Invalid field names
```

---

### Issue: Placeholder values not replaced

**Symptoms:**
```
❌ Error: Please update Docker Hub username in values-prod-aws.yaml
```

**Solution:**
```bash
# Edit values file
nano helm/todo-app/values-prod-aws.yaml

# Replace all placeholders:
# <your-dockerhub-username> → your actual username
# <ELASTIC_IP> → your AWS Elastic IP
# <your-domain> → your domain (or remove if not using)

# Verify no placeholders remain
grep -r "<" helm/todo-app/values-prod-aws.yaml
```

---

## Pod Startup Issues

### Issue: CrashLoopBackOff

**Symptoms:**
```
NAME                          READY   STATUS             RESTARTS   AGE
todo-app-backend-xxxxx        1/2     CrashLoopBackOff   5          3m
```

**Solution:**
```bash
# Check pod logs
kubectl logs <pod-name> -c backend

# Common causes:

# 1. Database connection failure
# Check DATABASE_URL in ConfigMap/Secret
kubectl get configmap backend-config -o yaml
kubectl get secret backend-secret -o yaml

# 2. Missing environment variables
kubectl describe pod <pod-name>

# 3. Application error
# Check logs for Python traceback or error messages

# 4. Port already in use
# Check if port 8000 is exposed correctly in Dockerfile
```

---

### Issue: Pending pods

**Symptoms:**
```
NAME                          READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxxx        0/2     Pending   0          5m
```

**Solution:**
```bash
# Check pod events
kubectl describe pod <pod-name>

# Common causes:

# 1. Insufficient resources
kubectl top nodes
kubectl describe node

# Solution: Reduce resource requests in values.yaml
# Or increase cluster resources

# 2. PersistentVolumeClaim not bound
kubectl get pvc

# Solution: Check storage class availability
kubectl get storageclass

# 3. Node selector mismatch
# Check pod spec for nodeSelector
kubectl get pod <pod-name> -o yaml | grep -A 5 nodeSelector
```

---

## Networking Issues

### Issue: Cannot access NodePort service

**Symptoms:**
- `curl http://<minikube-ip>:30000` times out
- Browser cannot load frontend

**Solution:**
```bash
# Check service exists
kubectl get svc todo-app-frontend

# Verify NodePort
kubectl get svc todo-app-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Check Minikube IP
minikube ip

# Test from within cluster
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  curl http://todo-app-frontend:3000

# If internal works but external doesn't:
# Use minikube service command
minikube service todo-app-frontend

# Or use port forwarding
kubectl port-forward svc/todo-app-frontend 3000:3000
```

---

### Issue: CORS errors in browser

**Symptoms:**
```
Access to fetch at 'http://backend:8000/tasks' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
```bash
# Check CORS configuration in backend
kubectl logs -l app.kubernetes.io/component=backend -c backend | grep CORS

# Update CORS origins in Helm values
# values-dev.yaml:
backend:
  config:
    corsOrigins: "http://localhost:3000,http://$(minikube ip):30000"

# Redeploy
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml
```

---

## Database Connection Issues

### Issue: Cannot connect to Neon PostgreSQL

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Test connection from pod
kubectl run psql-test --image=postgres:15 --rm -it --restart=Never -- \
  psql "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# If connection fails:

# 1. Check Neon dashboard for database status
# Visit: https://console.neon.tech

# 2. Verify connection string
kubectl get configmap backend-config -o yaml | grep databaseUrl

# 3. Check SSL mode
# Neon requires sslmode=require

# 4. Check network connectivity
# Ensure cluster has internet access
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  curl -I https://neon.tech
```

---

## Kafka/Redpanda Issues

### Issue: Redpanda pod not starting

**Symptoms:**
```
NAME         READY   STATUS    RESTARTS   AGE
redpanda-0   0/1     Pending   0          5m
```

**Solution:**
```bash
# Check pod events
kubectl describe pod redpanda-0

# Common causes:

# 1. PVC not bound
kubectl get pvc

# Solution: Check if storage class exists
kubectl get storageclass

# 2. Insufficient resources
# Reduce resource requests in redpanda.yaml
resources:
  requests:
    cpu: 50m      # Reduced from 100m
    memory: 256Mi # Reduced from 512Mi

# Reapply
kubectl delete -f helm/todo-app/dependencies/redpanda.yaml
kubectl apply -f helm/todo-app/dependencies/redpanda.yaml
```

---

### Issue: Topics not created

**Symptoms:**
```
rpk topic list
# Shows empty or missing topics
```

**Solution:**
```bash
# Check if init job ran
kubectl get jobs

# Check job logs
kubectl logs job/redpanda-init-topics

# Manually create topics
REDPANDA_POD=$(kubectl get pods -l app=redpanda -o jsonpath='{.items[0].metadata.name}')

kubectl exec -it $REDPANDA_POD -- rpk topic create task.created --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create task.updated --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create task.completed --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create task.deleted --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create reminder.due --partitions 1 --replicas 1

# Verify
kubectl exec -it $REDPANDA_POD -- rpk topic list
```

---

## Redis Issues

### Issue: Redis pod not ready

**Symptoms:**
```
NAME      READY   STATUS    RESTARTS   AGE
redis-0   0/1     Running   0          2m
```

**Solution:**
```bash
# Check readiness probe
kubectl describe pod redis-0 | grep -A 10 "Readiness"

# Check logs
kubectl logs redis-0

# Test Redis manually
kubectl exec -it redis-0 -- redis-cli ping

# If PONG returned, probe may be misconfigured
# Check redis.yaml readiness probe settings
```

---

### Issue: Redis connection refused

**Symptoms:**
```
Error: dial tcp 10.43.x.x:6379: connect: connection refused
```

**Solution:**
```bash
# Check Redis service
kubectl get svc redis

# Test from another pod
kubectl run redis-test --image=redis:7-alpine --rm -it --restart=Never -- \
  redis-cli -h redis ping

# Check Redis is listening on correct port
kubectl exec -it redis-0 -- netstat -tlnp | grep 6379

# Verify Dapr statestore configuration
kubectl get component statestore-redis -o yaml
```

---

## AWS k3s Issues

### Issue: Cannot SSH into EC2 instance

**Symptoms:**
```
Permission denied (publickey)
```

**Solution:**
```bash
# Check key permissions
chmod 400 ~/.ssh/todo-app-key.pem

# Verify correct key
aws ec2 describe-instances --instance-ids <instance-id> \
  --query 'Reservations[0].Instances[0].KeyName'

# Check security group allows SSH
aws ec2 describe-security-groups --group-ids <sg-id> \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`22`]'

# Get correct public IP
aws ec2 describe-instances --instance-ids <instance-id> \
  --query 'Reservations[0].Instances[0].PublicIpAddress'
```

---

### Issue: k3s not starting on EC2

**Symptoms:**
```
Failed to start k3s
```

**Solution:**
```bash
# SSH into instance
ssh -i ~/.ssh/todo-app-key.pem ubuntu@<elastic-ip>

# Check k3s status
sudo systemctl status k3s

# View logs
sudo journalctl -u k3s -n 100

# Common fixes:

# 1. Restart k3s
sudo systemctl restart k3s

# 2. Check disk space
df -h

# 3. Check memory
free -h

# 4. Reinstall k3s
curl -sfL https://get.k3s.io | sh -
```

---

### Issue: kubectl cannot connect to k3s

**Symptoms:**
```
Unable to connect to the server: dial tcp <ip>:6443: i/o timeout
```

**Solution:**
```bash
# Check security group allows port 6443
aws ec2 describe-security-groups --group-ids <sg-id>

# Add rule if missing
aws ec2 authorize-security-group-ingress \
  --group-id <sg-id> \
  --protocol tcp \
  --port 6443 \
  --cidr 0.0.0.0/0

# Verify kubeconfig has correct IP
grep server ~/.kube/config-aws

# Should be: https://<ELASTIC_IP>:6443
```

---

## Performance Issues

### Issue: Pods using too much memory

**Symptoms:**
```
OOMKilled - container exceeded memory limit
```

**Solution:**
```bash
# Check current usage
kubectl top pods

# Increase memory limits in values.yaml
backend:
  resources:
    limits:
      memory: "1Gi"  # Increased from 512Mi

# Or reduce memory usage:
# - Reduce worker processes
# - Enable memory profiling
# - Check for memory leaks
```

---

### Issue: Slow response times

**Symptoms:**
- API requests take >5 seconds
- Frontend loads slowly

**Solution:**
```bash
# Check pod resources
kubectl top pods

# Check database query performance
# Add logging to backend
kubectl logs -l app.kubernetes.io/component=backend -c backend | grep "query"

# Check network latency
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  time curl http://todo-app-backend:8000/health

# Solutions:
# 1. Add database indexes
# 2. Enable caching (Redis)
# 3. Increase pod replicas
# 4. Optimize queries
```

---

## Getting Help

### Collect Diagnostic Information

```bash
# Save all pod logs
kubectl logs -l app.kubernetes.io/instance=todo-app --all-containers=true > logs.txt

# Get pod descriptions
kubectl describe pods -l app.kubernetes.io/instance=todo-app > pods.txt

# Get events
kubectl get events --sort-by='.lastTimestamp' > events.txt

# Get Helm values
helm get values todo-app > values.txt

# Create diagnostic bundle
tar -czf diagnostics.tar.gz logs.txt pods.txt events.txt values.txt
```

### Useful Debug Commands

```bash
# Interactive shell in pod
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh

# Run temporary debug pod
kubectl run debug --image=busybox --rm -it --restart=Never -- sh

# Check DNS resolution
kubectl run dns-test --image=busybox --rm -it --restart=Never -- nslookup todo-app-backend

# Test network connectivity
kubectl run netcat-test --image=busybox --rm -it --restart=Never -- \
  nc -zv todo-app-backend 8000

# View resource quotas
kubectl describe resourcequota

# Check node conditions
kubectl describe nodes
```

---

## Common Error Messages

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| `ImagePullBackOff` | Image not found or wrong pull policy | Check image name, rebuild, or fix pull policy |
| `CrashLoopBackOff` | Application error on startup | Check logs for error messages |
| `Pending` | Insufficient resources or PVC issues | Check node resources or storage |
| `ErrImagePull` | Cannot pull image from registry | Check registry credentials or network |
| `CreateContainerConfigError` | Invalid ConfigMap/Secret reference | Verify ConfigMap/Secret exists |
| `OOMKilled` | Container exceeded memory limit | Increase memory limit |
| `Error: UPGRADE FAILED` | Helm upgrade validation failed | Check Helm chart syntax |
| `connection refused` | Service not listening or wrong port | Check service configuration |

---

**Last Updated**: 2026-02-09
**Version**: Step 5 - Troubleshooting Guide
