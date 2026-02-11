#!/bin/bash
# Deployment Testing Checklist for Step 5
# Run this script to validate each step of the deployment process

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Step 5 Deployment Testing Checklist${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if command succeeded
check_step() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Test 1: Prerequisites
echo -e "${BLUE}[1/10] Checking Prerequisites...${NC}"
docker --version > /dev/null 2>&1 && \
minikube version > /dev/null 2>&1 && \
kubectl version --client > /dev/null 2>&1 && \
helm version > /dev/null 2>&1 && \
dapr version > /dev/null 2>&1
check_step

# Test 2: Minikube Status
echo -e "${BLUE}[2/10] Checking Minikube Status...${NC}"
minikube status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Minikube is running${NC}"
else
    echo -e "${YELLOW}⚠️  Minikube not running. Run: ./scripts/setup-minikube.sh${NC}"
fi

# Test 3: Dapr Installation
echo -e "${BLUE}[3/10] Checking Dapr Installation...${NC}"
kubectl get pods -n dapr-system > /dev/null 2>&1
if [ $? -eq 0 ]; then
    DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ Dapr installed ($DAPR_PODS pods)${NC}"
else
    echo -e "${YELLOW}⚠️  Dapr not installed. Run: ./scripts/install-dapr-minikube.sh${NC}"
fi

# Test 4: Docker Images
echo -e "${BLUE}[4/10] Checking Docker Images...${NC}"
eval $(minikube docker-env 2>/dev/null)
if docker images | grep -q "todo-backend"; then
    echo -e "${GREEN}✅ Docker images built${NC}"
    docker images | grep todo
else
    echo -e "${YELLOW}⚠️  Images not built. Run: ./scripts/build-local-images.sh${NC}"
fi

# Test 5: Dependencies Deployed
echo -e "${BLUE}[5/10] Checking Dependencies (Redpanda, Redis)...${NC}"
REDPANDA=$(kubectl get pods -l app=redpanda --no-headers 2>/dev/null | wc -l)
REDIS=$(kubectl get pods -l app=redis --no-headers 2>/dev/null | wc -l)
if [ "$REDPANDA" -gt 0 ] && [ "$REDIS" -gt 0 ]; then
    echo -e "${GREEN}✅ Dependencies deployed (Redpanda: $REDPANDA, Redis: $REDIS)${NC}"
else
    echo -e "${YELLOW}⚠️  Dependencies not deployed${NC}"
fi

# Test 6: Helm Release
echo -e "${BLUE}[6/10] Checking Helm Release...${NC}"
if helm list | grep -q "todo-app"; then
    echo -e "${GREEN}✅ Helm release deployed${NC}"
    helm list
else
    echo -e "${YELLOW}⚠️  Helm release not found. Run: ./scripts/deploy-to-minikube.sh${NC}"
fi

# Test 7: Pods Running
echo -e "${BLUE}[7/10] Checking Pod Status...${NC}"
PODS=$(kubectl get pods -l app.kubernetes.io/instance=todo-app --no-headers 2>/dev/null | wc -l)
if [ "$PODS" -gt 0 ]; then
    echo -e "${GREEN}✅ Application pods running ($PODS pods)${NC}"
    kubectl get pods -l app.kubernetes.io/instance=todo-app
else
    echo -e "${YELLOW}⚠️  No application pods found${NC}"
fi

# Test 8: Dapr Components
echo -e "${BLUE}[8/10] Checking Dapr Components...${NC}"
COMPONENTS=$(kubectl get components --no-headers 2>/dev/null | wc -l)
if [ "$COMPONENTS" -ge 4 ]; then
    echo -e "${GREEN}✅ Dapr components configured ($COMPONENTS components)${NC}"
    kubectl get components
else
    echo -e "${YELLOW}⚠️  Dapr components not found${NC}"
fi

# Test 9: Backend Health
echo -e "${BLUE}[9/10] Checking Backend Health...${NC}"
MINIKUBE_IP=$(minikube ip 2>/dev/null)
if [ -n "$MINIKUBE_IP" ]; then
    HEALTH=$(curl -s http://$MINIKUBE_IP:30001/health 2>/dev/null || echo "")
    if echo "$HEALTH" | grep -q "healthy"; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend health check failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cannot get Minikube IP${NC}"
fi

# Test 10: Frontend Access
echo -e "${BLUE}[10/10] Checking Frontend Access...${NC}"
if [ -n "$MINIKUBE_IP" ]; then
    echo -e "${GREEN}✅ Frontend URL: http://$MINIKUBE_IP:30000${NC}"
    echo -e "${GREEN}✅ Backend URL: http://$MINIKUBE_IP:30001${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot determine access URLs${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. If any tests failed, follow the suggested commands"
echo "2. Run end-to-end tests: ./scripts/e2e-test-minikube.sh"
echo "3. Access frontend: minikube service todo-app-frontend"
echo "4. View logs: kubectl logs -f -l app.kubernetes.io/component=backend"
echo ""
