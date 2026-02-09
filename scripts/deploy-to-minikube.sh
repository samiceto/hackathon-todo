#!/bin/bash
# Deploy Todo App to Minikube using Helm (Step 5)
# This script deploys the full stack including backend, frontend, and reminder-service

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
VALUES_FILE="./helm/todo-app/values-dev.yaml"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deploying Todo App to Minikube${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Minikube is running
echo -e "${BLUE}🔍 Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo -e "${RED}❌ Error: Minikube is not running${NC}"
    echo -e "${YELLOW}💡 Start Minikube first: ./scripts/setup-minikube.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Minikube is running${NC}"
echo ""

# Check if Dapr is installed
echo -e "${BLUE}🔍 Checking Dapr installation...${NC}"
if ! kubectl get pods -n dapr-system &> /dev/null; then
    echo -e "${RED}❌ Error: Dapr is not installed${NC}"
    echo -e "${YELLOW}💡 Install Dapr first: ./scripts/install-dapr-minikube.sh${NC}"
    exit 1
fi

DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
if [ "$DAPR_PODS" -eq 0 ]; then
    echo -e "${RED}❌ Error: No Dapr pods found${NC}"
    echo -e "${YELLOW}💡 Install Dapr first: ./scripts/install-dapr-minikube.sh${NC}"
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
    kubectl wait --for=condition=ready pod -l app=redpanda --timeout=180s || true
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
        --timeout 5m
else
    helm install $RELEASE_NAME $HELM_CHART \
        -f $VALUES_FILE \
        --namespace $NAMESPACE \
        --wait \
        --timeout 5m
fi

echo -e "${GREEN}✅ Helm deployment completed${NC}"
echo ""

# Wait for pods to be ready
echo -e "${BLUE}⏳ Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/instance=$RELEASE_NAME \
    --timeout=300s || true
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

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Get NodePort for frontend
FRONTEND_NODEPORT=$(kubectl get svc -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].spec.ports[0].nodePort}' 2>/dev/null || echo "30000")
BACKEND_NODEPORT=$(kubectl get svc -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].spec.ports[0].nodePort}' 2>/dev/null || echo "30001")

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}🌐 Access URLs:${NC}"
echo -e "   Frontend: ${GREEN}http://$MINIKUBE_IP:$FRONTEND_NODEPORT${NC}"
echo -e "   Backend:  ${GREEN}http://$MINIKUBE_IP:$BACKEND_NODEPORT${NC}"
echo ""
echo -e "${YELLOW}💡 Useful commands:${NC}"
echo -e "   View pods:           ${BLUE}kubectl get pods${NC}"
echo -e "   View logs (backend): ${BLUE}kubectl logs -f -l app.kubernetes.io/component=backend${NC}"
echo -e "   View logs (frontend):${BLUE}kubectl logs -f -l app.kubernetes.io/component=frontend${NC}"
echo -e "   View logs (reminder):${BLUE}kubectl logs -f -l app.kubernetes.io/component=reminder-service${NC}"
echo -e "   Port forward backend:${BLUE}kubectl port-forward svc/$RELEASE_NAME-backend 8000:8000${NC}"
echo -e "   Open frontend:       ${BLUE}minikube service $RELEASE_NAME-frontend${NC}"
echo -e "   Helm status:         ${BLUE}helm status $RELEASE_NAME${NC}"
echo -e "   Uninstall:           ${BLUE}helm uninstall $RELEASE_NAME${NC}"
echo ""
