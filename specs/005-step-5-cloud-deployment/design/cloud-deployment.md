# Cloud Deployment Guide - AWS k3s

**Step 5: Advanced Cloud Deployment - Application Deployment to AWS**

This guide provides step-by-step instructions for deploying the Todo App to AWS k3s cluster after infrastructure provisioning is complete.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Prepare Docker Images](#prepare-docker-images)
3. [Configure Helm Values](#configure-helm-values)
4. [Deploy Dependencies](#deploy-dependencies)
5. [Deploy Application](#deploy-application)
6. [Verification and Testing](#verification-and-testing)
7. [Post-Deployment Configuration](#post-deployment-configuration)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Rollback and Recovery](#rollback-and-recovery)

---

## Prerequisites

### Infrastructure Setup Complete

Before proceeding, ensure you have completed the infrastructure provisioning from `cloud-provisioning.md`:

- ✅ AWS EC2 instance running with k3s installed
- ✅ Elastic IP allocated and associated
- ✅ Security groups configured
- ✅ kubectl configured to access k3s cluster
- ✅ Dapr installed on k3s cluster
- ✅ Neon PostgreSQL database accessible

### Verify Infrastructure

```bash
# Check k3s cluster
export KUBECONFIG=~/.kube/config-aws
kubectl cluster-info
kubectl get nodes

# Check Dapr
kubectl get pods -n dapr-system

# Test database connectivity
psql "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

### Required Tools

- Docker (for building images)
- kubectl (configured for AWS k3s)
- Helm 3.x
- Git (for cloning repository)

---

## Prepare Docker Images

### Option A: Use Docker Hub (Recommended)

#### 1. Create Docker Hub Account

Sign up at https://hub.docker.com if you don't have an account.

#### 2. Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password.

#### 3. Build and Tag Images

```bash
# Navigate to project root
cd /path/to/hackathon-todo

# Build backend image
docker build -t <your-dockerhub-username>/todo-backend:latest ./backend/api

# Build frontend image
docker build -t <your-dockerhub-username>/todo-frontend:latest ./frontend

# Build reminder-service image
docker build -t <your-dockerhub-username>/todo-reminder-service:latest ./backend/reminder-service
```

**Replace `<your-dockerhub-username>` with your actual Docker Hub username.**

#### 4. Push Images to Docker Hub

```bash
docker push <your-dockerhub-username>/todo-backend:latest
docker push <your-dockerhub-username>/todo-frontend:latest
docker push <your-dockerhub-username>/todo-reminder-service:latest
```

**Estimated time**: 5-10 minutes (depending on internet speed)

#### 5. Verify Images

```bash
# List your Docker Hub repositories
docker search <your-dockerhub-username>/todo
```

Or visit: `https://hub.docker.com/u/<your-dockerhub-username>`

---

### Option B: Import Images Directly to k3s

If you prefer not to use Docker Hub (for privacy or bandwidth reasons):

#### 1. Build Images Locally

```bash
docker build -t todo-backend:latest ./backend/api
docker build -t todo-frontend:latest ./frontend
docker build -t todo-reminder-service:latest ./backend/reminder-service
```

#### 2. Save Images as Tar Files

```bash
docker save todo-backend:latest | gzip > backend.tar.gz
docker save todo-frontend:latest | gzip > frontend.tar.gz
docker save todo-reminder-service:latest | gzip > reminder.tar.gz
```

#### 3. Copy to EC2 Instance

```bash
# Get Elastic IP
ELASTIC_IP="<your-elastic-ip>"

# Copy images
scp -i ~/.ssh/todo-app-key.pem backend.tar.gz ubuntu@$ELASTIC_IP:~
scp -i ~/.ssh/todo-app-key.pem frontend.tar.gz ubuntu@$ELASTIC_IP:~
scp -i ~/.ssh/todo-app-key.pem reminder.tar.gz ubuntu@$ELASTIC_IP:~
```

#### 4. Import Images on EC2

```bash
# SSH into EC2
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$ELASTIC_IP

# Import images
sudo k3s ctr images import backend.tar.gz
sudo k3s ctr images import frontend.tar.gz
sudo k3s ctr images import reminder.tar.gz

# Verify images
sudo k3s crictl images | grep todo

# Exit SSH
exit
```

---

## Configure Helm Values

### 1. Copy Production Values Template

```bash
cp helm/todo-app/values-prod-aws.yaml helm/todo-app/values-prod-aws-custom.yaml
```

### 2. Update Docker Hub Username

Edit `helm/todo-app/values-prod-aws-custom.yaml`:

```yaml
backend:
  image:
    repository: <your-dockerhub-username>/todo-backend  # Update this
    tag: latest
    pullPolicy: Always  # Use Never if using Option B (local images)

frontend:
  image:
    repository: <your-dockerhub-username>/todo-frontend  # Update this
    tag: latest
    pullPolicy: Always

reminderService:
  image:
    repository: <your-dockerhub-username>/todo-reminder-service  # Update this
    tag: latest
    pullPolicy: Always
```

### 3. Update Elastic IP

Get your Elastic IP:

```bash
aws ec2 describe-addresses --query 'Addresses[0].PublicIp' --output text
```

Update in `values-prod-aws-custom.yaml`:

```yaml
backend:
  config:
    corsOrigins: "http://<ELASTIC_IP>:30000,https://<your-domain>"  # Update ELASTIC_IP

frontend:
  config:
    nextPublicApiUrl: "http://<ELASTIC_IP>:30001"  # Update ELASTIC_IP
```

### 4. Update Secrets (Important!)

**Never commit secrets to Git!**

Update `betterAuthSecret` with a strong random value:

```bash
# Generate a secure random secret
openssl rand -base64 32
```

Update in `values-prod-aws-custom.yaml`:

```yaml
backend:
  secrets:
    betterAuthSecret: "<generated-secret>"  # Replace with generated value
```

### 5. Verify Database URL

Ensure the Neon PostgreSQL connection string is correct:

```yaml
backend:
  config:
    databaseUrl: "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
```

---

## Deploy Dependencies

### 1. Deploy Redpanda (Kafka)

```bash
# Apply Redpanda deployment
kubectl apply -f helm/todo-app/dependencies/redpanda.yaml

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=300s

# Check status
kubectl get pods -l app=redpanda
kubectl logs -l app=redpanda --tail=50
```

### 2. Create Kafka Topics

```bash
# Get Redpanda pod name
REDPANDA_POD=$(kubectl get pods -l app=redpanda -o jsonpath='{.items[0].metadata.name}')

# Create topics
kubectl exec -it $REDPANDA_POD -- rpk topic create task.created --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create task.updated --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create task.completed --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create task.deleted --partitions 1 --replicas 1
kubectl exec -it $REDPANDA_POD -- rpk topic create reminder.due --partitions 1 --replicas 1

# Verify topics
kubectl exec -it $REDPANDA_POD -- rpk topic list
```

Expected output:
```
NAME             PARTITIONS  REPLICAS
task.created     1           1
task.updated     1           1
task.completed   1           1
task.deleted     1           1
reminder.due     1           1
```

### 3. Deploy Redis

```bash
# Apply Redis deployment
kubectl apply -f helm/todo-app/dependencies/redis.yaml

# Wait for Redis to be ready
kubectl wait --for=condition=ready pod -l app=redis --timeout=180s

# Check status
kubectl get pods -l app=redis
kubectl logs -l app=redis --tail=50
```

### 4. Test Redis Connectivity

```bash
# Get Redis pod name
REDIS_POD=$(kubectl get pods -l app=redis -o jsonpath='{.items[0].metadata.name}')

# Test Redis
kubectl exec -it $REDIS_POD -- redis-cli ping
```

Expected output: `PONG`

---

## Deploy Application

### Method 1: Using Deployment Script (Recommended)

```bash
# Run deployment script
./scripts/deploy-to-aws.sh
```

This script will:
- Verify cluster connectivity
- Check Dapr installation
- Deploy dependencies (if not already deployed)
- Deploy application with Helm
- Wait for pods to be ready
- Display access URLs

---

### Method 2: Manual Helm Deployment

#### 1. Install/Upgrade with Helm

```bash
# First-time installation
helm install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-prod-aws-custom.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# Or upgrade existing deployment
helm upgrade todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-prod-aws-custom.yaml \
  --namespace default \
  --wait \
  --timeout 10m
```

#### 2. Monitor Deployment

```bash
# Watch pods starting
watch kubectl get pods

# Check deployment status
kubectl get deployments
kubectl get services
```

#### 3. Wait for Pods to be Ready

```bash
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/instance=todo-app \
  --timeout=600s
```

---

## Verification and Testing

### 1. Check Pod Status

```bash
# All pods should show READY 2/2 (app + Dapr sidecar)
kubectl get pods -l app.kubernetes.io/instance=todo-app
```

Expected output:
```
NAME                                      READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxxx                    2/2     Running   0          2m
todo-app-frontend-xxxxx                   2/2     Running   0          2m
todo-app-reminder-service-xxxxx           2/2     Running   0          2m
```

### 2. Check Services

```bash
kubectl get svc -l app.kubernetes.io/instance=todo-app
```

Expected output:
```
NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
todo-app-backend            NodePort    10.43.x.x       <none>        8000:30001/TCP   2m
todo-app-frontend           NodePort    10.43.x.x       <none>        3000:30000/TCP   2m
todo-app-reminder-service   ClusterIP   10.43.x.x       <none>        8001/TCP         2m
```

### 3. Check Dapr Components

```bash
kubectl get components
```

Expected output:
```
NAME                       AGE
cron-reminder-processor    2m
kubernetes-secrets         2m
pubsub-kafka              2m
statestore-redis          2m
```

### 4. Test Backend Health

```bash
# Get Elastic IP
ELASTIC_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')

# Test health endpoint
curl http://$ELASTIC_IP:30001/health
```

Expected response:
```json
{"status": "healthy"}
```

### 5. Test Frontend Access

```bash
# Open frontend in browser
echo "Frontend URL: http://$ELASTIC_IP:30000"
```

Visit the URL in your browser. You should see the Todo App interface.

### 6. Test Task Creation

```bash
# Create a test task
curl -X POST http://$ELASTIC_IP:30001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Testing AWS deployment"}'
```

Expected response: JSON with task details including ID.

### 7. View Application Logs

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

---

## Post-Deployment Configuration

### 1. Set Up Custom Domain (Optional)

If you have a domain name:

#### Update DNS Records

Point your domain to the Elastic IP:

```
Type: A
Name: todo-app (or @)
Value: <ELASTIC_IP>
TTL: 300
```

#### Update Helm Values

```yaml
backend:
  config:
    corsOrigins: "https://todo-app.yourdomain.com"

frontend:
  config:
    nextPublicApiUrl: "https://api.todo-app.yourdomain.com"
```

#### Install cert-manager for TLS

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 2. Configure Monitoring (Optional)

Deploy Prometheus and Grafana for monitoring:

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### 3. Set Up Backups

#### Database Backups

Neon PostgreSQL has automatic backups. Verify in Neon dashboard.

#### k3s Cluster Backups

```bash
# SSH into EC2
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$ELASTIC_IP

# Create snapshot
sudo k3s etcd-snapshot save

# List snapshots
sudo ls -lh /var/lib/rancher/k3s/server/db/snapshots/
```

---

## Monitoring and Maintenance

### 1. Monitor Resource Usage

```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -l app.kubernetes.io/instance=todo-app
```

### 2. Check Application Health

```bash
# Health check script
while true; do
  curl -s http://$ELASTIC_IP:30001/health | jq .
  sleep 30
done
```

### 3. Update Application

#### Build New Images

```bash
# Build with version tag
docker build -t <username>/todo-backend:v1.1.0 ./backend/api
docker push <username>/todo-backend:v1.1.0
```

#### Update Deployment

```bash
helm upgrade todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-prod-aws-custom.yaml \
  --set backend.image.tag=v1.1.0 \
  --wait
```

### 4. Scale Application

```bash
# Scale backend replicas
kubectl scale deployment todo-app-backend --replicas=2

# Or update Helm values and upgrade
helm upgrade todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-prod-aws-custom.yaml \
  --set backend.replicas=2
```

---

## Troubleshooting

### Pods Not Starting

**Check pod status:**
```bash
kubectl describe pod <pod-name>
```

**Common issues:**

1. **ImagePullBackOff**: Docker Hub credentials or image name incorrect
   ```bash
   # Verify image exists
   docker pull <username>/todo-backend:latest
   ```

2. **CrashLoopBackOff**: Application error
   ```bash
   # Check logs
   kubectl logs <pod-name> -c backend
   ```

3. **Pending**: Insufficient resources
   ```bash
   # Check node resources
   kubectl describe node
   ```

### Cannot Access Application

**Check security groups:**
```bash
aws ec2 describe-security-groups --group-ids <sg-id>
```

Ensure ports 30000 and 30001 are open.

**Check NodePort services:**
```bash
kubectl get svc
```

### Database Connection Issues

**Test from pod:**
```bash
kubectl run psql-test --image=postgres:15 --rm -it --restart=Never -- \
  psql "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

### Dapr Issues

**Check Dapr sidecar:**
```bash
kubectl logs <pod-name> -c daprd
```

**Verify Dapr components:**
```bash
kubectl describe component pubsub-kafka
kubectl describe component statestore-redis
```

---

## Rollback and Recovery

### Rollback Helm Deployment

```bash
# View deployment history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 2
```

### Restore k3s from Snapshot

```bash
# SSH into EC2
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$ELASTIC_IP

# Stop k3s
sudo systemctl stop k3s

# Restore from snapshot
sudo k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/<snapshot-name>

# Start k3s
sudo systemctl start k3s
```

### Disaster Recovery

If EC2 instance is lost:

1. Launch new EC2 instance
2. Install k3s
3. Restore from snapshot (if available)
4. Redeploy application with Helm

Database (Neon) is external and unaffected.

---

## Cost Optimization

### 1. Stop Instance When Not in Use

```bash
# Stop instance (keeps data)
aws ec2 stop-instances --instance-ids <instance-id>

# Start instance
aws ec2 start-instances --instance-ids <instance-id>
```

**Cost while stopped**: ~$3/month (EBS storage only)

### 2. Use Spot Instances (Advanced)

For non-critical workloads, use EC2 Spot Instances to save up to 90%.

### 3. Monitor Costs

Set up AWS billing alerts:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name todo-app-billing-alert \
  --alarm-description "Alert when monthly costs exceed $50" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold
```

---

## Next Steps

After successful deployment:

1. **Set Up CI/CD**: Automate deployments with GitHub Actions (see User Story 10)
2. **Enable Monitoring**: Deploy full observability stack (see User Story 11)
3. **Load Testing**: Test application under realistic load
4. **Security Hardening**: Implement additional security measures
5. **Documentation**: Document custom configurations and procedures

---

**Last Updated**: 2026-02-09
**Version**: Step 5 - User Story 9 (AWS Cloud Deployment)
