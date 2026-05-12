#!/bin/bash
# Build Docker images directly in minikube's daemon

set -e

echo "🔧 Connecting to minikube's Docker daemon..."
eval $(minikube docker-env)

echo "🐳 Building backend image..."
docker build -t todo-backend:latest ./backend/api

echo "🎨 Building frontend image..."
docker build -t todo-frontend:latest ./frontend

echo "✅ Images built successfully in minikube!"
echo ""
echo "📋 Available images:"
docker images | grep -E "todo-|REPOSITORY"
