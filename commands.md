# Session Commands

All commands used during the Minikube deployment session.

---

## Diagnostics

```bash
minikube status                          # Check if Minikube is running
kubectl config current-context           # Check which k8s cluster kubectl points to
kubectl get nodes                        # Check if cluster API is reachable
minikube profile list                    # List all Minikube profiles and their drivers
cat ~/.minikube/machines/minikube/config.json  # Read saved Minikube driver config
```

## Cluster Reset

```bash
minikube start --driver=docker           # Attempt start (failed — corrupted state)
kubectl get nodes                        # Confirmed API server was down
minikube delete                          # Wipe the corrupted cluster completely
minikube start --driver=docker --cpus=4 --memory=4096  # Fresh cluster with enough resources
kubectl get nodes                        # Verify new cluster is healthy
free -h                                  # Check available system memory
```

## Docker Image Builds

```bash
minikube docker-env                      # Get env vars to point Docker CLI at Minikube's daemon
DOCKER_HOST=... docker build -t todo-backend:latest backend/api/   # Build backend image inside Minikube
DOCKER_HOST=... docker build -t todo-frontend:latest frontend/      # Build frontend image inside Minikube
```

## Deployment

```bash
helm list                                # Check for existing Helm releases
helm install todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml  # Deploy app to Minikube
```

## Verification

```bash
kubectl get pods -l app.kubernetes.io/instance=todo-app -w   # Watch pods come up in real time
kubectl get pods -l app.kubernetes.io/instance=todo-app       # Final pod status check
minikube ip                              # Get Minikube's cluster IP
kubectl get svc -l app.kubernetes.io/instance=todo-app        # List services and NodePorts
kubectl port-forward svc/todo-app-backend 8888:8000           # Tunnel backend to localhost
curl http://localhost:8888/health        # Confirm backend returns {"status":"ok"}
```

---

**Total: 16 commands** across 4 phases — diagnose → reset → build → deploy.


## What Works / What's Disabled

| Feature                | Status                          |
|------------------------|---------------------------------|
| Task CRUD              | ✅ Works                        |
| Frontend UI            | ✅ Works                        |
| Reminder notifications | ❌ Disabled (needs Dapr)        |
| Event streaming        | ❌ Silently degraded (no crash) |

To re-enable reminders later, set `dapr.enabled: true` and `reminderService.enabled: true` after installing Dapr on the cluster. 


 Access the app (WSL2 — use port-forward, NodePort IP isn't routable)                                                                        
  Backend API:                                                                                                                                kubectl port-forward svc/todo-app-backend 8000:8000       
  # then open: http://localhost:8000/docs            
                                                                                                                                              Frontend:
  kubectl port-forward svc/todo-app-frontend 3000:3000                                                                                        # then open: http://localhost:3000    