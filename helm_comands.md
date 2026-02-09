# ===============================
# STEP 0 — Verify Required Tools
# ===============================
docker --version
kubectl version --client
minikube version
helm version


# ===============================
# STEP 1 — Start Minikube
# ===============================
minikube start --driver=docker --cpus=2 --memory=4096


# ===============================
# STEP 1.1 — Verify Kubernetes
# ===============================
kubectl get nodes


# ===============================
# STEP 2 — Use Minikube Docker
# ===============================
eval $(minikube docker-env)


# ===============================
# STEP 2.1 — Verify Docker Context
# ===============================
docker ps


# ===============================
# STEP 3 — Build Backend Image
# ===============================
cd hackathon/backend
docker build -t hackathon-backend:dev .


# ===============================
# STEP 4 — Build Frontend Image
# ===============================
cd ../frontend
docker build -t hackathon-frontend:dev .


# ===============================
# STEP 5 — Create Helm Chart (ONE TIME ONLY)
# ===============================
cd ..
helm create helm/hackathon


# ===============================
# STEP 6 — Deploy Backend (First Install)
# ===============================
helm install hackathon ./helm/hackathon -f values-dev.yaml


# ===============================
# STEP 7 — Verify Backend
# ===============================
kubectl get pods
kubectl get svc


# ===============================
# STEP 8 — Test Backend
# ===============================
kubectl port-forward svc/hackathon-backend 8000:8000
# (open new terminal for curl)
curl http://localhost:8000/health


# ===============================
# STEP 9 — Deploy / Update Frontend
# ===============================
helm upgrade hackathon ./helm/hackathon -f values-dev.yaml


# ===============================
# STEP 10 — Verify Frontend
# ===============================
kubectl get pods
kubectl get svc


# ===============================
# STEP 11 — Access Frontend
# ===============================
minikube service hackathon-frontend


Phase 5 Commands Log

  1. Prerequisites & Setup

  # Check prerequisites and get feature directory
  .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks

  # Check for checklists directory
  ls -la /mnt/d/Quarter-4/spec_kit_plus/hackathon-todo/specs/004-k8s-deployment/checklists/

  # Check Minikube cluster status
  minikube status

  2. Docker Image Verification

  # Check if Docker images exist in Minikube (attempt 1)
  eval $(minikube docker-env) && docker images | grep -E "(todo-backend|todo-frontend)" | head -5

  # Check Docker images with table format (attempt 2)
  eval $(minikube docker-env) && docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep
  -E "(REPOSITORY|todo-backend|todo-frontend)"

  # Check Docker images via Minikube SSH (successful)
  minikube ssh "docker images" | grep -E "(todo-backend|todo-frontend)"

  3. Helm Release Status

  # List all Helm releases
  helm list -A

  4. Configuration Testing (Before Upgrade)

  # Check current LOG_LEVEL value
  kubectl get configmap todo-app-backend-config -o yaml | grep LOG_LEVEL

  5. Helm Upgrade Test

  # Upgrade Helm release with configuration change (LOG_LEVEL: debug → info)
  helm upgrade todo-app ./helm/todo-app -f ./helm/todo-app/values-dev.yaml \
    --set backend.secrets.openaiApiKey=$OPENAI_API_KEY \
    --set backend.secrets.betterAuthSecret=uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC

  6. Upgrade Verification

  # Check pod status after upgrade (verify rolling update)
  kubectl get pods -l app.kubernetes.io/instance=todo-app

  # Verify LOG_LEVEL changed to "info"
  kubectl get configmap todo-app-backend-config -o yaml | grep LOG_LEVEL

  # View Helm release history (all revisions)
  helm history todo-app

  7. Helm Rollback Test

  # Rollback to previous revision (revision 9)
  helm rollback todo-app

  8. Rollback Verification

  # Verify LOG_LEVEL reverted to "debug"
  kubectl get configmap todo-app-backend-config -o yaml | grep LOG_LEVEL

  # View recent Helm history (last 5 revisions)
  helm history todo-app | tail -5
  
  
    1. Health Check Verification
  
    # Verify backend liveness probe configuration
    kubectl get deployment todo-app-backend -o yaml | grep -A 20 "livenessProbe:"
  
    # Verify backend readiness probe configuration
    kubectl get deployment todo-app-backend -o yaml | grep -A 10 "readinessProbe:"
  
    # Verify frontend liveness probe configuration
    kubectl get deployment todo-app-frontend -o yaml | grep -A 20 "livenessProbe:"
  
    # Verify frontend readiness probe configuration
    kubectl get deployment todo-app-frontend -o yaml | grep -A 10 "readinessProbe:"
  
    2. Auto-Restart Testing
  
    # Get backend pod name
    kubectl get pods -l app.kubernetes.io/component=backend
  
    # Attempt to kill pod process (kill command not available in container)
    kubectl exec todo-app-backend-66b7878fd8-nwkvv -- kill 1
  
    # Delete backend pod to test Kubernetes auto-restart
    kubectl delete pod todo-app-backend-66b7878fd8-nwkvv
  
    # Wait 5 seconds and verify pod was recreated
    sleep 5 && kubectl get pods -l app.kubernetes.io/component=backend
  
    3. Metrics-Server Setup
  
    # Check if metrics-server is already enabled
    minikube addons list | grep metrics-server
  
    # Enable metrics-server addon
    minikube addons enable metrics-server
  
    # Wait and check pod resource usage (failed - metrics API not ready)
    echo "Waiting for metrics-server to collect data..." && sleep 20 && kubectl top pods -l
    app.kubernetes.io/instance=todo-app
  
    # Check metrics-server pod status
    kubectl get pods -n kube-system | grep metrics-server
  
    # Wait and check again
    echo "Waiting for metrics-server pod to be ready..." && sleep 30 && kubectl get pods -n kube-system | grep
     metrics-server
  
    # Check with label selector
    kubectl get pods -n kube-system -l k8s-app=metrics-server
  
    # Check metrics-server pod events
    kubectl describe pod -n kube-system -l k8s-app=metrics-server | grep -A 10 "Events:"
  
    # Continue checking status (multiple attempts)
    kubectl get pods -n kube-system -l k8s-app=metrics-server
    sleep 60 && kubectl get pods -n kube-system -l k8s-app=metrics-server
  
    # Check recent metrics-server events
    kubectl get events -n kube-system --sort-by='.lastTimestamp' | grep metrics-server | tail -5
  
    4. Resource Limits Verification
  
    # Verify backend pod resource limits
    kubectl describe pod -l app.kubernetes.io/component=backend | grep -A 10 "Limits:"
  
    # Verify frontend pod resource limits
    kubectl describe pod -l app.kubernetes.io/component=frontend | grep -A 10 "Limits:"
  
    5. Documentation
  
    # Search for health check sections in quickstart
    grep -n "Health" /mnt/d/Quarter-4/spec_kit_plus/hackathon-todo/specs/004-k8s-deployment/quickstart.md |
    head -10
  
    # Count lines in quickstart guide
    wc -l /mnt/d/Quarter-4/spec_kit_plus/hackathon-todo/specs/004-k8s-deployment/quickstart.md
  
    # Search for probe-related content
    grep -n -i "probe\|liveness\|readiness"
    /mnt/d/Quarter-4/spec_kit_plus/hackathon-todo/specs/004-k8s-deployment/quickstart.md