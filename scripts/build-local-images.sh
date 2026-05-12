#!/bin/bash
# Build Docker images for Minikube local deployment (Step 5)
# This script builds backend, frontend, and reminder-service images directly in Minikube's Docker daemon

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Docker Images for Minikube${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}❌ Error: Minikube is not running${NC}"
    echo -e "${YELLOW}💡 Start Minikube first: ./scripts/setup-minikube.sh${NC}"
    exit 1
fi

# Connect to Minikube's Docker daemon
echo -e "${BLUE}🔧 Connecting to Minikube's Docker daemon...${NC}"
eval $(minikube docker-env)

# Verify connection
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Error: Failed to connect to Minikube's Docker daemon${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Connected to Minikube Docker daemon${NC}"
echo ""

# Build backend image
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🐳 Building Backend Image (FastAPI)${NC}"
echo -e "${BLUE}========================================${NC}"
if [ ! -d "./backend/api" ]; then
    echo -e "${RED}❌ Error: backend/api directory not found${NC}"
    exit 1
fi

docker build -t todo-backend:latest ./backend/api
echo -e "${GREEN}✅ Backend image built successfully${NC}"
echo ""

# Build frontend image
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🎨 Building Frontend Image (Next.js)${NC}"
echo -e "${BLUE}========================================${NC}"
if [ ! -d "./frontend" ]; then
    echo -e "${RED}❌ Error: frontend directory not found${NC}"
    exit 1
fi

docker build -t todo-frontend:latest ./frontend
echo -e "${GREEN}✅ Frontend image built successfully${NC}"
echo ""

# Build reminder-service image
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}⏰ Building Reminder Service Image${NC}"
echo -e "${BLUE}========================================${NC}"
if [ ! -d "./backend/reminder-service" ]; then
    echo -e "${RED}❌ Error: backend/reminder-service directory not found${NC}"
    exit 1
fi

docker build -t todo-reminder-service:latest ./backend/reminder-service
echo -e "${GREEN}✅ Reminder service image built successfully${NC}"
echo ""

# Display built images
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📋 Built Images Summary${NC}"
echo -e "${BLUE}========================================${NC}"
docker images | grep -E "todo-|REPOSITORY"
echo ""

# Image sizes
echo -e "${BLUE}📊 Image Sizes:${NC}"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "todo-|REPOSITORY"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All images built successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "   1. Deploy dependencies: kubectl apply -f helm/todo-app/dependencies/"
echo -e "   2. Deploy application: ./scripts/deploy-to-minikube.sh"
echo -e "   3. Check deployment: kubectl get pods"
echo ""
