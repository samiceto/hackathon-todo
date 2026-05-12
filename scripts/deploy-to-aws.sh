#!/bin/bash
# Deploy Todo App to AWS k3s using Helm (Step 5)
# This script deploys the full stack to AWS EC2 with k3s

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

RELEASE_NAME="todo-app"
NAMESPACE="default"
HELM_CHART="./helm/todo-app"
VALUES_FILE="./helm/todo-app/values-prod-aws.yaml"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deploying Todo App to AWS k3s${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if kubectl is configured for AWS k3s
echo -e "${BLUE}🔍 Checking Kubernetes connection...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Error: Cannot connect to Kubernetes cluster${NC}"
    echo -e "${YELLOW}💡 Make sure KUBECONFIG is set to your AWS k3s cluster${NC}"
    echo -e "${YELLOW}   export KUBECONFIG=~/.kube/config-aws${NC}"
    exit 1
fi

# Verify it's a k3s cluster
K3S_CHECK=$(kubectl get nodes -o jsonpath='{.items[0].status.nodeInfo.containerRuntimeVersion}' 2>/dev/null || echo "")
if [[ ! "$K3S_CHECK" =~ "containerd" ]]; then
    echo -e "${YELLOW}⚠️  Warning: This doesn't appear to be a k3s cluster${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ Connected to Kubernetes cluster${NC}"
kubectl cluster-info
echo ""

# Check if Dapr is installed
echo -e "${BLUE}🔍 Checking Dapr installation...${NC}"
if ! kubectl get pods -n dapr-system &> /dev/null; then
    echo -e "${RED}❌ Error: Dapr is not installed${NC}"
    echo -e "${YELLOW}💡 Install Dapr first: dapr init -k${NC}"
    exit 1
fi

DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
if [ "$DAPR_PODS" -eq 0 ]; then
    echo -e "${RED}❌ Error: No Dapr pods found${NC}"
    echo -e "${YELLOW}💡 Install Dapr first: dapr init -k${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Dapr is installed ($DAPR_PODS pods)${NC}"
echo ""

# Check if dependencies are deployed
echo -e "${BLUE}🔍 Checking dependencies (Redpanda, Redis)...${NC}"
REDPANDA_PODS=$(kubectl get pods -l app=redpanda --no-headers 2>/dev/null | wc -l)
REDIS_PODS=$(kubectl get pods -l app=redis --no-headers 2>/dev/null | wc -l)

if [ "$REDPANDA_PODS" -eq 0 ] || [ "$REDIS_PODS" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Dependencies not found. Deploying...${NC}"
    echo ""

    echo -e "${BLUE}📦 Deploying Redpanda (Kafka)...${NC}"
    kubectl apply -f helm/todo-app/dependencies/redpanda.yaml

    echo -e "${BLUE}📦 Deploying Redis...${NC}"
    kubectl apply -f helm/todo-app/dependencies/redis.yaml

    echo -e "${BLUE}⏳ Waiting for dependencies to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=redpanda --timeout=300s || true
    kubectl wait --for=condition=ready pod -l app=redis --timeout=180s || true
    echo -e "${GREEN}✅ Dependencies deployed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already deployed (Redpanda: $REDPANDA_PODS, Redis: $REDIS_PODS)${NC}"
fi
echo ""

# Check if Helm chart exists
if [ ! -d "$HELM_CHART" ]; then
    echo -e "${RED}❌ Error: Helm chart not found at $HELM_CHART${NC}"
    exit 1
fi

if [ ! -f "$VALUES_FILE" ]; then
    echo -e "${RED}❌ Error: Values file not found at $VALUES_FILE${NC}"
    exit 1
fi

# Check for placeholder values
echo -e "${BLUE}🔍 Checking for placeholder values...${NC}"
if grep -q "<your-dockerhub-username>" "$VALUES_FILE"; then
    echo -e "${RED}❌ Error: Please update Docker Hub username in $VALUES_FILE${NC}"
    echo -e "${YELLOW}💡 Replace <your-dockerhub-username> with your actual Docker Hub username${NC}"
    exit 1
fi

if grep -q "<ELASTIC_IP>" "$VALUES_FILE"; then
    echo -e "${YELLOW}⚠️  Warning: Placeholder <ELASTIC_IP> found in $VALUES_FILE${NC}"
    echo -e "${YELLOW}💡 Update with your AWS Elastic IP for proper CORS and API URL configuration${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if release already exists
echo -e "${BLUE}🔍 Checking existing deployment...${NC}"
if helm list -n $NAMESPACE | grep -q "^$RELEASE_NAME"; then
    echo -e "${YELLOW}📦 Release '$RELEASE_NAME' exists. Upgrading...${NC}"
    ACTION="upgrade"
else
    echo -e "${BLUE}📦 Release '$RELEASE_NAME' not found. Installing...${NC}"
    ACTION="install"
fi
echo ""

# Deploy or upgrade the Helm chart
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Deploying Todo App Helm Chart${NC}"
echo -e "${BLUE}========================================${NC}"

if [ "$ACTION" = "upgrade" ]; then
    helm upgrade $RELEASE_NAME $HELM_CHART \
        -f $VALUES_FILE \
        --namespace $NAMESPACE \
        --wait \
        --timeout 10m
else
    helm install $RELEASE_NAME $HELM_CHART \
        -f $VALUES_FILE \
        --namespace $NAMESPACE \
        --wait \
        --timeout 10m
fi

echo -e "${GREEN}✅ Helm deployment completed${NC}"
echo ""

# Wait for pods to be ready
echo -e "${BLUE}⏳ Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/instance=$RELEASE_NAME \
    --timeout=600s || true
echo ""

# Display deployment status
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📊 Deployment Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${BLUE}Pods:${NC}"
kubectl get pods -l app.kubernetes.io/instance=$RELEASE_NAME
echo ""

echo -e "${BLUE}Services:${NC}"
kubectl get svc -l app.kubernetes.io/instance=$RELEASE_NAME
echo ""

echo -e "${BLUE}Dapr Components:${NC}"
kubectl get components
echo ""

# Get node external IP (Elastic IP)
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>/dev/null)
if [ -z "$NODE_IP" ]; then
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null)
fi

# Get NodePort for frontend and backend
FRONTEND_NODEPORT=$(kubectl get svc -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].spec.ports[0].nodePort}' 2>/dev/null || echo "30000")
BACKEND_NODEPORT=$(kubectl get svc -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].spec.ports[0].nodePort}' 2>/dev/null || echo "30001")

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}🌐 Access URLs:${NC}"
echo -e "   Frontend: ${GREEN}http://$NODE_IP:$FRONTEND_NODEPORT${NC}"
echo -e "   Backend:  ${GREEN}http://$NODE_IP:$BACKEND_NODEPORT${NC}"
echo ""
echo -e "${YELLOW}💡 Useful commands:${NC}"
echo -e "   View pods:           ${BLUE}kubectl get pods${NC}"
echo -e "   View logs (backend): ${BLUE}kubectl logs -f -l app.kubernetes.io/component=backend -c backend${NC}"
echo -e "   View logs (frontend):${BLUE}kubectl logs -f -l app.kubernetes.io/component=frontend -c frontend${NC}"
echo -e "   View logs (reminder):${BLUE}kubectl logs -f -l app.kubernetes.io/component=reminder-service -c reminder-service${NC}"
echo -e "   View Dapr logs:      ${BLUE}kubectl logs -f -l app.kubernetes.io/component=backend -c daprd${NC}"
echo -e "   Helm status:         ${BLUE}helm status $RELEASE_NAME${NC}"
echo -e "   Uninstall:           ${BLUE}helm uninstall $RELEASE_NAME${NC}"
echo ""
echo -e "${YELLOW}🔒 Security Reminders:${NC}"
echo -e "   - Update BETTER_AUTH_SECRET in production"
echo -e "   - Restrict security group rules to specific IPs"
echo -e "   - Enable TLS/SSL for production traffic"
echo -e "   - Store secrets in Kubernetes secrets, not values files"
echo ""
