#!/bin/bash

# Script to install Dapr in Minikube cluster for Step 5 deployment
# Requires: minikube, kubectl, dapr CLI installed

set -e  # Exit on any error

echo "🚀 Installing Dapr in Minikube cluster..."

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Please start Minikube first with:"
    echo "   scripts/setup-minikube.sh"
    exit 1
fi

# Check if dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "❌ Dapr CLI is not installed. Please install Dapr CLI first:"
    echo "   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash"
    echo "   Or visit: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Verify current kubectl context is pointing to minikube
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "")
if [[ "$CURRENT_CONTEXT" != *"minikube"* ]]; then
    echo "⚠️  Current kubectl context is not Minikube: $CURRENT_CONTEXT"
    echo "   Switching to minikube context..."
    kubectl config use-context minikube
fi

# Check if Dapr is already installed
if kubectl get namespace dapr-system &> /dev/null; then
    echo "🔄 Dapr is already installed in the cluster, checking status..."

    # Check if all Dapr system pods are running
    DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
    if [[ $DAPR_PODS -gt 0 ]]; then
        RUNNING_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | grep -c "Running\|Completed" || echo "0")
        if [[ $RUNNING_PODS -eq $DAPR_PODS ]]; then
            echo "✅ Dapr is already installed and all system pods are running ($RUNNING_PODS/$DAPR_PODS)"
            echo "📋 Dapr system pods status:"
            kubectl get pods -n dapr-system
            echo "🎉 Dapr installation complete!"
            exit 0
        else
            echo "⚠️  Dapr is installed but not all pods are running ($RUNNING_PODS/$DAPR_PODS)"
            echo "📋 Dapr system pods status:"
            kubectl get pods -n dapr-system
            echo "🔄 Restarting Dapr system pods..."
            kubectl delete pods -n dapr-system --all
        fi
    fi
fi

# Install Dapr in Kubernetes mode
echo "🔧 Installing Dapr in Kubernetes mode..."
dapr init -k

# Wait for Dapr system pods to be ready
echo "⏳ Waiting for Dapr system pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=dapr --timeout=180s -n dapr-system

# Additional wait for operator pod specifically
kubectl wait --for=condition=ready pod -l app=dapr-operator --timeout=120s -n dapr-system || true

# Verify installation
echo "🔍 Verifying Dapr installation..."
DAPR_VERSION=$(dapr --version 2>/dev/null || echo "unknown")
echo "   Dapr CLI version: $DAPR_VERSION"

# Check that all Dapr system pods are running
echo "📋 Dapr system pods status:"
kubectl get pods -n dapr-system

# Count running pods
RUNNING_COUNT=$(kubectl get pods -n dapr-system --no-headers | grep -c "Running\|Completed" || echo "0")
TOTAL_COUNT=$(kubectl get pods -n dapr-system --no-headers | wc -l)

if [[ $RUNNING_COUNT -eq $TOTAL_COUNT ]] && [[ $TOTAL_COUNT -gt 0 ]]; then
    echo "✅ Dapr installed successfully with all system pods running ($RUNNING_COUNT/$TOTAL_COUNT)"
else
    echo "⚠️  Dapr installation completed but not all pods are running ($RUNNING_COUNT/$TOTAL_COUNT)"
    echo "   Check pod status with: kubectl get pods -n dapr-system"
    echo "   Check pod logs with: kubectl logs -n dapr-system <pod-name>"
fi

# Test Dapr functionality
echo "🧪 Testing Dapr functionality..."
dapr status -k

echo ""
echo "📋 Next steps:"
echo "   1. Run this script to ensure Dapr is properly installed"
echo "   2. Deploy dependencies (Redpanda, Redis): Apply YAML files in helm/todo-app/dependencies/ (after they're created)"
echo "   3. Build local images: scripts/build-local-images.sh (after it's created)"
echo "   4. Deploy to Minikube: scripts/deploy-to-minikube.sh (after it's created)"
echo ""
echo "💡 Useful Dapr commands:"
echo "   dapr status -k          # Check Dapr system status"
echo "   dapr dashboard -k       # Open Dapr dashboard"
echo "   kubectl get pods -n dapr-system  # View Dapr pods"
echo ""
echo "🎉 Dapr installation complete!"