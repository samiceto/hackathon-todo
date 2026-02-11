# Step 5 Deployment Testing Guide

**Complete guide for testing Minikube and AWS k3s deployments**

---

## Quick Start Testing Workflow

### Phase 1: Setup Prerequisites (One-time)

**1. Enable Docker Desktop WSL Integration**
```bash
# On Windows:
# 1. Open Docker Desktop
# 2. Settings → Resources → WSL Integration
# 3. Enable your WSL distro
# 4. Apply & Restart

# Verify:
docker ps
```

**2. Install kubectl**
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

**3. Install Dapr CLI**
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
dapr version
```

**4. Verify All Tools**
```bash
./scripts/validate-deployment.sh
```

---

### Phase 2: Minikube Deployment (15-20 minutes)

**Step 1: Setup Minikube Cluster**
```bash
cd /mnt/d/Quarter-4/spec_kit_plus/hackathon-todo

./scripts/setup-minikube.sh
```

**Expected Output:**
- Minikube starts with 4 CPUs, 8GB RAM
- Ingress and metrics-server addons enabled
- Cluster info displayed

**Verify:**
```bash
minikube status
kubectl cluster-info
```

---

**Step 2: Install Dapr**
```bash
./scripts/install-dapr-minikube.sh
```

**Expected Output:**
- Dapr initialized on Kubernetes
- 5 Dapr system pods running
- Dapr dashboard accessible

**Verify:**
```bash
kubectl get pods -n dapr-system
# Should show 5 pods all Running
```

---

**Step 3: Build Docker Images**
```bash
./scripts/build-local-images.sh
```

**Expected Output:**
- Connects to Minikube Docker daemon
- Builds 3 images: backend, frontend, reminder-service
- Shows image sizes

**Verify:**
```bash
eval $(minikube docker-env)
docker images | grep todo
# Should show 3 images with 'latest' tag
```

---

**Step 4: Deploy Application**
```bash
./scripts/deploy-to-minikube.sh
```

**Expected Output:**
- Dependencies deployed (Redpanda, Redis)
- Helm chart installed/upgraded
- All pods reach Running state
- Access URLs displayed

**Verify:**
```bash
kubectl get pods
# Should show:
# - redpanda-0 (1/1 Running)
# - redis-0 (1/1 Running)
# - todo-app-backend-xxx (2/2 Running)
# - todo-app-frontend-xxx (2/2 Running)
# - todo-app-reminder-service-xxx (2/2 Running)

kubectl get svc
# Should show NodePort services on ports 30000, 30001
```

---

**Step 5: Run End-to-End Tests**
```bash
./scripts/e2e-test-minikube.sh
```

**Expected Output:**
- 12 tests executed
- All tests pass
- Summary shows 12/12 passed

**Test Coverage:**
- Deployment running
- Backend health check
- Dapr components configured
- Redis connectivity
- Kafka topics configured
- Task CRUD operations
- Recurring task creation
- Task with reminder creation
- Reminder service logging

---

### Phase 3: Manual Verification (5 minutes)

**1. Access Frontend**
```bash
# Option A: Minikube service (opens browser)
minikube service todo-app-frontend

# Option B: Direct URL
MINIKUBE_IP=$(minikube ip)
echo "Frontend: http://$MINIKUBE_IP:30000"
echo "Backend: http://$MINIKUBE_IP:30001"
```

**2. Test Backend API**
```bash
MINIKUBE_IP=$(minikube ip)

# Health check
curl http://$MINIKUBE_IP:30001/health

# Create task
curl -X POST http://$MINIKUBE_IP:30001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Testing deployment"}'

# List tasks
curl http://$MINIKUBE_IP:30001/tasks
```

**3. Check Logs**
```bash
# Backend logs
kubectl logs -f -l app.kubernetes.io/component=backend -c backend

# Frontend logs
kubectl logs -f -l app.kubernetes.io/component=frontend -c frontend

# Reminder service logs
kubectl logs -f -l app.kubernetes.io/component=reminder-service -c reminder-service

# Dapr sidecar logs
kubectl logs -f -l app.kubernetes.io/component=backend -c daprd
```

**4. Verify Kafka Topics**
```bash
kubectl exec -it redpanda-0 -- rpk topic list
# Should show: task.created, task.updated, task.completed, task.deleted, reminder.due
```

**5. Verify Redis**
```bash
kubectl exec -it redis-0 -- redis-cli ping
# Should return: PONG
```

---

### Phase 4: Performance Testing (Optional)

**1. Check Resource Usage**
```bash
kubectl top nodes
kubectl top pods -l app.kubernetes.io/instance=todo-app
```

**2. Load Test (if k6 installed)**
```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/

# Run load test
k6 run - <<EOF
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '2m', target: 50 },
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  let res = http.get('http://$(minikube ip):30001/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
EOF
```

---

## Troubleshooting Quick Reference

### Issue: Pods Not Starting

**Check pod status:**
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c <container-name>
```

**Common fixes:**
```bash
# Rebuild images
./scripts/build-local-images.sh

# Restart deployment
kubectl rollout restart deployment todo-app-backend
kubectl rollout restart deployment todo-app-frontend
kubectl rollout restart deployment todo-app-reminder-service
```

---

### Issue: Cannot Access Frontend

**WSL2 users:**
```bash
# Use port forwarding instead
kubectl port-forward svc/todo-app-frontend 3000:3000
# Access: http://localhost:3000

kubectl port-forward svc/todo-app-backend 8000:8000
# Access: http://localhost:8000
```

---

### Issue: Dapr Components Not Found

**Redeploy Helm chart:**
```bash
helm upgrade todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml

# Verify components
kubectl get components
```

---

### Issue: Database Connection Failed

**Check database URL:**
```bash
kubectl get configmap backend-config -o yaml | grep databaseUrl

# Test connection from pod
kubectl run psql-test --image=postgres:15 --rm -it --restart=Never -- \
  psql "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

---

## Cleanup

**Stop but keep data:**
```bash
minikube stop
```

**Delete everything:**
```bash
helm uninstall todo-app
kubectl delete -f helm/todo-app/dependencies/redpanda.yaml
kubectl delete -f helm/todo-app/dependencies/redis.yaml
minikube delete
```

---

## AWS k3s Testing (After Minikube Success)

Once Minikube deployment is working, test AWS k3s:

**1. Provision AWS Infrastructure**
```bash
# Follow: specs/005-step-5-cloud-deployment/design/cloud-provisioning.md
# - Launch EC2 instance
# - Install k3s
# - Configure security groups
```

**2. Build and Push Images**
```bash
# Login to Docker Hub
docker login

# Build and push
docker build -t <username>/todo-backend:latest ./backend/api
docker build -t <username>/todo-frontend:latest ./frontend
docker build -t <username>/todo-reminder-service:latest ./backend/reminder-service

docker push <username>/todo-backend:latest
docker push <username>/todo-frontend:latest
docker push <username>/todo-reminder-service:latest
```

**3. Deploy to AWS**
```bash
# Configure kubectl for AWS k3s
export KUBECONFIG=~/.kube/config-aws

# Deploy
./scripts/deploy-to-aws.sh
```

**4. Verify Deployment**
```bash
kubectl get pods
kubectl get svc

# Access application
ELASTIC_IP="<your-elastic-ip>"
echo "Frontend: http://$ELASTIC_IP:30000"
echo "Backend: http://$ELASTIC_IP:30001"
```

---

## Success Criteria Checklist

### Minikube Deployment
- [ ] All prerequisites installed
- [ ] Minikube cluster running
- [ ] Dapr installed (5 pods in dapr-system)
- [ ] Docker images built (3 images)
- [ ] Dependencies deployed (Redpanda, Redis)
- [ ] Application deployed (3 services)
- [ ] All pods Running (2/2 containers)
- [ ] Dapr components configured (4 components)
- [ ] Backend health check passes
- [ ] Frontend accessible in browser
- [ ] E2E tests pass (12/12)
- [ ] Logs show no errors

### AWS k3s Deployment
- [ ] EC2 instance running
- [ ] k3s installed and accessible
- [ ] Docker images pushed to Docker Hub
- [ ] Dapr installed on k3s
- [ ] Dependencies deployed
- [ ] Application deployed
- [ ] All pods Running
- [ ] Frontend accessible via Elastic IP
- [ ] Backend API responding
- [ ] Database connection working

---

## Next Steps After Successful Testing

1. **Document any issues encountered** in troubleshooting.md
2. **Implement User Stories 1-7** (advanced features)
3. **Set up CI/CD** (User Story 10)
4. **Deploy monitoring** (User Story 11)
5. **Conduct security audit** using security.md checklist
6. **Perform load testing** and optimize using performance.md

---

**Last Updated**: 2026-02-09
**Version**: Step 5 - Deployment Testing Guide
