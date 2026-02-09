#!/bin/bash

# Script to setup Minikube with required resources for Step 5 deployment
# Requires: minikube, kubectl installed

set -e  # Exit on any error

echo "🚀 Setting up Minikube for Step 5 deployment..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube is not installed. Please install minikube first:"
    echo "   Linux/Mac: curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/"
    echo "   Or use package manager: brew install minikube (Mac) or apt-get install minikube (Ubuntu)"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first:"
    echo "   Mac: brew install kubectl"
    echo "   Ubuntu: snap install kubectl --classic"
    echo "   Or visit: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if the minikube cluster already exists
if minikube status &> /dev/null; then
    echo "🔄 Minikube cluster already exists, checking status..."
    minikube status

    # Check if it's running with sufficient resources
    MINIKUBE_STATUS=$(minikube status --format='{{.CPUs}}:{{.Memory}}')
    if [[ $MINIKUBE_STATUS =~ ^([0-9]+):([0-9]+)MB$ ]]; then
        CPUS=${BASH_REMATCH[1]}
        MEMORY_MB=${BASH_REMATCH[2]}

        if [[ $CPUS -ge 2 ]] && [[ $MEMORY_MB -ge 3072 ]]; then
            echo "✅ Minikube is already running with sufficient resources (CPU: $CPUS, Memory: ${MEMORY_MB}MB)"
            echo "🎉 Minikube setup complete!"
            exit 0
        else
            echo "⚠️  Current Minikube resources are insufficient (CPU: $CPUS, Memory: ${MEMORY_MB}MB)"
            echo "🔄 Stopping current cluster to restart with required resources..."
            minikube stop
            minikube delete
        fi
    fi
else
    echo "ℹ️  No existing Minikube cluster found, will create new one"
fi

# Start minikube with required resources (2+ CPUs, 3GB+ RAM)
echo "🔧 Starting Minikube with 2 CPUs and 4GB RAM..."
minikube start --cpus=2 --memory=4096mb --disk-size=10gb

# Verify the cluster is running correctly
echo "🔍 Verifying cluster status..."
minikube status

# Wait for kube-system pods to be ready
echo "⏳ Waiting for kube-system pods to be ready..."
kubectl wait --for=condition=ready pod -l component=kube-apiserver -n kube-system --timeout=120s || true
kubectl wait --for=condition=ready pod -l k8s-app=kube-proxy -n kube-system --timeout=120s || true

echo "✅ Minikube cluster is running with required resources (2 CPUs, 4GB RAM)"
echo ""
echo "📋 Next steps:"
echo "   1. Run this script to ensure Minikube is properly configured"
echo "   2. Install Dapr: scripts/install-dapr-minikube.sh (after it's created)"
echo "   3. Build local images: scripts/build-local-images.sh (after it's created)"
echo "   4. Deploy to Minikube: scripts/deploy-to-minikube.sh (after it's created)"
echo ""
echo "💡 To interact with the cluster directly:"
echo "   kubectl get nodes"
echo "   minikube dashboard  # opens web dashboard"
echo ""
echo "🎉 Minikube setup complete!"