# Cloud Infrastructure Provisioning Guide - AWS Free Tier

**Step 5: Advanced Cloud Deployment - AWS Free Tier Setup**

This guide provides step-by-step instructions for deploying the Todo App on AWS using free tier resources with k3s Kubernetes, keeping costs at $0-10/month.

---

## Table of Contents

1. [Overview](#overview)
2. [AWS Free Tier Setup](#aws-free-tier-setup)
3. [k3s Kubernetes Cluster](#k3s-kubernetes-cluster)
4. [Database Configuration (Neon PostgreSQL)](#database-configuration-neon-postgresql)
5. [Self-Hosted Kafka (Redpanda)](#self-hosted-kafka-redpanda)
6. [Self-Hosted Redis](#self-hosted-redis)
7. [Cost Breakdown](#cost-breakdown)
8. [Security Best Practices](#security-best-practices)

---

## Overview

### Architecture Components

**Kubernetes Cluster**:
- k3s lightweight Kubernetes on EC2 t2.medium (or 2x t2.micro)
- Single-node or 2-node cluster
- Self-hosted control plane (no EKS costs)

**Services**:
- **PostgreSQL**: Neon PostgreSQL (already configured, free tier)
- **Kafka**: Self-hosted Redpanda in cluster
- **Redis**: Self-hosted Redis in cluster
- **Storage**: EBS volumes (30GB free tier)

**Networking**:
- Elastic IP for stable access
- Security groups for firewall rules
- Public access via NodePort or LoadBalancer

### Cost Estimate

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| EC2 t2.medium | 1 instance (750 hours free) | $0 (first 12 months) |
| EBS Storage | 30GB SSD | $0 (free tier) |
| Elastic IP | 1 IP (while attached) | $0 |
| Data Transfer | 15GB outbound | $0 (free tier) |
| Neon PostgreSQL | Free tier | $0 |
| **Total** | | **$0/month** (within free tier) |

**After 12 months**: ~$30-40/month for t2.medium

---

## AWS Free Tier Setup

### Prerequisites

1. **AWS Account**: Sign up at https://aws.amazon.com/free/
2. **AWS CLI**: Install and configure
3. **SSH Key Pair**: For EC2 access
4. **Domain (Optional)**: For custom domain and TLS

### 1. Install AWS CLI

```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# macOS
brew install awscli

# Windows
choco install awscli
```

### 2. Configure AWS CLI

```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format: `json`

### 3. Create SSH Key Pair

```bash
aws ec2 create-key-pair \
  --key-name todo-app-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/todo-app-key.pem

chmod 400 ~/.ssh/todo-app-key.pem
```

---

## k3s Kubernetes Cluster

### Option A: Single Node (Recommended for Free Tier)

#### 1. Create Security Group

```bash
# Create security group
aws ec2 create-security-group \
  --group-name todo-app-sg \
  --description "Security group for Todo App k3s cluster"

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups \
  --group-names todo-app-sg \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Allow SSH (port 22)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Allow HTTP (port 80)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS (port 443)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow NodePort range (30000-32767)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 30000-32767 \
  --cidr 0.0.0.0/0

# Allow k3s API (port 6443)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 6443 \
  --cidr 0.0.0.0/0
```

#### 2. Launch EC2 Instance

```bash
# Get latest Ubuntu AMI ID
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)

# Launch instance (t2.medium for better performance, or t2.micro for strict free tier)
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.medium \
  --key-name todo-app-key \
  --security-group-ids $SG_ID \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=30,VolumeType=gp2}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=todo-app-k3s}]'
```

**Note**: Use `t2.micro` if you want to stay strictly within free tier, but performance will be limited.

#### 3. Allocate and Associate Elastic IP

```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Get allocation ID
ALLOC_ID=$(aws ec2 describe-addresses \
  --query 'Addresses[?PublicIp!=`null`] | [0].AllocationId' \
  --output text)

# Get instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=todo-app-k3s" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

# Associate Elastic IP with instance
aws ec2 associate-address \
  --instance-id $INSTANCE_ID \
  --allocation-id $ALLOC_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-addresses \
  --allocation-ids $ALLOC_ID \
  --query 'Addresses[0].PublicIp' \
  --output text)

echo "Instance Public IP: $PUBLIC_IP"
```

#### 4. Install k3s on EC2

```bash
# SSH into instance
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install k3s
curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --node-external-ip $PUBLIC_IP

# Verify installation
sudo k3s kubectl get nodes
```

#### 5. Get kubeconfig for Local Access

```bash
# On EC2 instance
sudo cat /etc/rancher/k3s/k3s.yaml

# Copy output to local machine
# Replace 127.0.0.1 with $PUBLIC_IP
```

On your local machine:

```bash
# Create kubeconfig
mkdir -p ~/.kube
cat > ~/.kube/config-aws <<EOF
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <CA_DATA>
    server: https://$PUBLIC_IP:6443
  name: k3s-aws
contexts:
- context:
    cluster: k3s-aws
    user: k3s-aws
  name: k3s-aws
current-context: k3s-aws
kind: Config
preferences: {}
users:
- name: k3s-aws
  user:
    client-certificate-data: <CLIENT_CERT_DATA>
    client-key-data: <CLIENT_KEY_DATA>
EOF

# Use this config
export KUBECONFIG=~/.kube/config-aws

# Verify connection
kubectl get nodes
```

#### 6. Install Dapr on k3s

```bash
# On local machine (with KUBECONFIG set)
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system
```

---

### Option B: Multi-Node Cluster (2x t2.micro)

If you prefer high availability within free tier:

1. Launch 2x t2.micro instances (1 server, 1 agent)
2. Install k3s server on first instance
3. Join second instance as agent

**Note**: This uses your full 750 hours/month free tier allowance.

---

## Database Configuration (Neon PostgreSQL)

### Current Setup

You're already using Neon PostgreSQL (free tier). No changes needed!

**Connection String** (from your values-dev.yaml):
```
postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Verify Connectivity from EC2

```bash
# SSH into EC2 instance
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$PUBLIC_IP

# Install PostgreSQL client
sudo apt install -y postgresql-client

# Test connection
psql "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

If connection works, you're all set!

---

## Self-Hosted Kafka (Redpanda)

Deploy Redpanda inside the k3s cluster (same as Minikube setup).

### 1. Deploy Redpanda

```bash
# Apply Redpanda deployment
kubectl apply -f helm/todo-app/dependencies/redpanda.yaml

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=300s

# Verify Redpanda
kubectl get pods -l app=redpanda
kubectl logs -l app=redpanda
```

### 2. Create Topics

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

---

## Self-Hosted Redis

Deploy Redis inside the k3s cluster (same as Minikube setup).

### 1. Deploy Redis

```bash
# Apply Redis deployment
kubectl apply -f helm/todo-app/dependencies/redis.yaml

# Wait for Redis to be ready
kubectl wait --for=condition=ready pod -l app=redis --timeout=180s

# Verify Redis
kubectl get pods -l app=redis
kubectl logs -l app=redis
```

### 2. Test Redis

```bash
# Get Redis pod name
REDIS_POD=$(kubectl get pods -l app=redis -o jsonpath='{.items[0].metadata.name}')

# Test Redis
kubectl exec -it $REDIS_POD -- redis-cli ping
```

Expected output: `PONG`

---

## Deploy Todo App

### 1. Build and Push Docker Images

Since k3s doesn't have a built-in registry, you have two options:

**Option A: Use Docker Hub (Recommended)**

```bash
# Login to Docker Hub
docker login

# Build and tag images
docker build -t <your-dockerhub-username>/todo-backend:latest ./backend/api
docker build -t <your-dockerhub-username>/todo-frontend:latest ./frontend
docker build -t <your-dockerhub-username>/todo-reminder-service:latest ./backend/reminder-service

# Push images
docker push <your-dockerhub-username>/todo-backend:latest
docker push <your-dockerhub-username>/todo-frontend:latest
docker push <your-dockerhub-username>/todo-reminder-service:latest
```

**Option B: Import Images Directly to k3s**

```bash
# Save images locally
docker save todo-backend:latest | gzip > backend.tar.gz
docker save todo-frontend:latest | gzip > frontend.tar.gz
docker save todo-reminder-service:latest | gzip > reminder.tar.gz

# Copy to EC2
scp -i ~/.ssh/todo-app-key.pem *.tar.gz ubuntu@$PUBLIC_IP:~

# SSH into EC2 and import
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$PUBLIC_IP
sudo k3s ctr images import backend.tar.gz
sudo k3s ctr images import frontend.tar.gz
sudo k3s ctr images import reminder.tar.gz
```

### 2. Create Helm Values for AWS

Create `helm/todo-app/values-aws.yaml`:

```yaml
# AWS k3s deployment configuration
global:
  environment: production

# Backend configuration
backend:
  replicas: 1
  image:
    repository: <your-dockerhub-username>/todo-backend  # or todo-backend for local
    tag: latest
    pullPolicy: Always  # or Never for local images
  service:
    type: NodePort
    port: 8000
    nodePort: 30001
  config:
    corsOrigins: "http://<PUBLIC_IP>:30000,https://<your-domain>"
    databaseUrl: "postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    logLevel: "info"
  secrets:
    openaiApiKey: ""  # Provide via --set
    betterAuthSecret: "uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC"

# Frontend configuration
frontend:
  replicas: 1
  image:
    repository: <your-dockerhub-username>/todo-frontend
    tag: latest
    pullPolicy: Always
  service:
    type: NodePort
    port: 3000
    nodePort: 30000
  config:
    nextPublicApiUrl: "http://<PUBLIC_IP>:30001"

# Reminder Service configuration
reminderService:
  enabled: true
  replicaCount: 1
  image:
    repository: <your-dockerhub-username>/todo-reminder-service
    tag: latest
    pullPolicy: Always
  service:
    type: ClusterIP
    port: 8001
  logLevel: "INFO"

# Database configuration
database:
  secretName: "backend-secret"

# Dapr configuration
dapr:
  enabled: true
  logLevel: "info"
  pubsub:
    name: pubsub-kafka
    type: pubsub.kafka
    version: v1
    metadata:
      - name: brokers
        value: "redpanda:9092"
      - name: authType
        value: "none"
      - name: consumerGroup
        value: "todo-app-group"
      - name: clientID
        value: "todo-app-client"
  statestore:
    name: statestore-redis
    type: state.redis
    version: v1
    metadata:
      - name: redisHost
        value: "redis:6379"
      - name: redisPassword
        value: ""
      - name: actorStateStore
        value: "true"
  cronBinding:
    name: cron-reminder-processor
    type: bindings.cron
    version: v1
    metadata:
      - name: schedule
        value: "*/1 * * * *"
      - name: direction
        value: "input"
  secrets:
    name: kubernetes-secrets
    type: secretstores.kubernetes
    version: v1
    metadata:
      - name: defaultNamespace
        value: "default"
```

### 3. Deploy with Helm

```bash
# Deploy dependencies (if not already deployed)
kubectl apply -f helm/todo-app/dependencies/redpanda.yaml
kubectl apply -f helm/todo-app/dependencies/redis.yaml

# Wait for dependencies
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis --timeout=180s

# Deploy Todo App
helm install todo-app ./helm/todo-app -f ./helm/todo-app/values-aws.yaml

# Check deployment
kubectl get pods
kubectl get svc
```

### 4. Access Application

```bash
# Get public IP
echo "Frontend: http://$PUBLIC_IP:30000"
echo "Backend: http://$PUBLIC_IP:30001"

# Open in browser
xdg-open http://$PUBLIC_IP:30000  # Linux
open http://$PUBLIC_IP:30000      # macOS
```

---

## Cost Breakdown

### Within Free Tier (First 12 Months)

| Service | Free Tier Allowance | Usage | Cost |
|---------|---------------------|-------|------|
| EC2 t2.medium | 750 hours/month | 1 instance | $0 |
| EBS Storage | 30GB | 30GB | $0 |
| Data Transfer Out | 15GB/month | ~5GB | $0 |
| Elastic IP | 1 IP (attached) | 1 IP | $0 |
| Neon PostgreSQL | Free tier | 0.5GB | $0 |
| **Total** | | | **$0/month** |

### After Free Tier Expires (Month 13+)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| EC2 t2.medium | 1 instance (730 hours) | $33.87 |
| EBS Storage | 30GB SSD | $3.00 |
| Data Transfer | 15GB outbound | $1.35 |
| Elastic IP | 1 IP (attached) | $0 |
| Neon PostgreSQL | Free tier | $0 |
| **Total** | | **~$38/month** |

### Cost Optimization Tips

1. **Use t2.micro**: Reduces cost to ~$8.50/month after free tier
2. **Stop instance when not in use**: Pay only for storage (~$3/month)
3. **Use Reserved Instances**: Save up to 72% with 1-year commitment
4. **Monitor usage**: Set up billing alerts in AWS Console

---

## Security Best Practices

### 1. Restrict Security Group Rules

```bash
# Remove public SSH access, allow only your IP
MY_IP=$(curl -s ifconfig.me)

aws ec2 revoke-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr $MY_IP/32
```

### 2. Enable Automatic Security Updates

```bash
# SSH into EC2
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$PUBLIC_IP

# Enable unattended upgrades
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Use Secrets Management

```bash
# Store secrets in Kubernetes secrets (not in values files)
kubectl create secret generic backend-secret \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=BETTER_AUTH_SECRET="..."
```

### 4. Enable TLS/SSL (Optional)

Use Let's Encrypt with cert-manager:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Configure Let's Encrypt issuer
# (Requires domain name)
```

### 5. Regular Backups

```bash
# Backup k3s cluster
sudo k3s etcd-snapshot save

# Backup to S3 (optional)
aws s3 cp /var/lib/rancher/k3s/server/db/snapshots/ s3://my-backup-bucket/ --recursive
```

---

## Monitoring and Maintenance

### 1. Check Resource Usage

```bash
# SSH into EC2
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$PUBLIC_IP

# Check CPU and memory
htop

# Check disk usage
df -h

# Check k3s status
sudo systemctl status k3s
```

### 2. View Logs

```bash
# k3s logs
sudo journalctl -u k3s -f

# Application logs
kubectl logs -f -l app.kubernetes.io/component=backend
kubectl logs -f -l app.kubernetes.io/component=frontend
kubectl logs -f -l app.kubernetes.io/component=reminder-service
```

### 3. Update Applications

```bash
# Rebuild and push new images
docker build -t <username>/todo-backend:v2 ./backend/api
docker push <username>/todo-backend:v2

# Update Helm deployment
helm upgrade todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-aws.yaml \
  --set backend.image.tag=v2
```

---

## Troubleshooting

### Instance Not Accessible

```bash
# Check instance status
aws ec2 describe-instances --instance-ids $INSTANCE_ID

# Check security group rules
aws ec2 describe-security-groups --group-ids $SG_ID

# Verify Elastic IP association
aws ec2 describe-addresses
```

### k3s Not Starting

```bash
# SSH into instance
ssh -i ~/.ssh/todo-app-key.pem ubuntu@$PUBLIC_IP

# Check k3s logs
sudo journalctl -u k3s -n 100

# Restart k3s
sudo systemctl restart k3s
```

### Pods Not Starting

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check node resources
kubectl top nodes
kubectl describe node
```

---

## Cleanup

### Stop Instance (Keep Data)

```bash
aws ec2 stop-instances --instance-ids $INSTANCE_ID
```

**Cost while stopped**: ~$3/month (EBS storage only)

### Terminate Instance (Delete Everything)

```bash
# Terminate instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID

# Release Elastic IP
aws ec2 release-address --allocation-id $ALLOC_ID

# Delete security group
aws ec2 delete-security-group --group-id $SG_ID

# Delete key pair
aws ec2 delete-key-pair --key-name todo-app-key
rm ~/.ssh/todo-app-key.pem
```

---

## Next Steps

After successful AWS deployment:

1. **Set Up Domain**: Point domain to Elastic IP for custom URL
2. **Enable TLS**: Use cert-manager and Let's Encrypt
3. **Configure CI/CD**: Automate deployments with GitHub Actions
4. **Set Up Monitoring**: Deploy Prometheus and Grafana
5. **Load Testing**: Test application under load

---

**Last Updated**: 2026-02-09
**Version**: Step 5 - User Story 9 (AWS Free Tier Deployment)
