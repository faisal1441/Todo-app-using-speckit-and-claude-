#!/bin/bash
# Deploy Todo Chatbot to Minikube

set -e

echo "🚀 Deploying Todo Chatbot to Minikube..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HELM_CHART="$REPO_ROOT/phase-4/helm-charts"

# Check if Minikube is running
echo "🔍 Checking Minikube status..."
if ! minikube status &> /dev/null; then
    echo "⚠️  Minikube is not running. Starting Minikube..."
    minikube start --cpus=4 --memory=6144 --disk-size=20g
else
    echo "✅ Minikube is running"
fi
echo ""

# Load images into Minikube
echo "📤 Loading Docker images into Minikube..."
minikube image load todoapp/backend:latest || echo "⚠️  Backend image not found locally. Build it first with ./phase-4/scripts/build-images.sh"
minikube image load todoapp/frontend:latest || echo "⚠️  Frontend image not found locally"
minikube image load todoapp/chatbot:latest || echo "⚠️  Chatbot image not found locally"
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "${YELLOW}⚠️  Warning: OPENAI_API_KEY environment variable is not set${NC}"
    echo "Chatbot service will not function without an API key."
    echo "Set it with: export OPENAI_API_KEY=sk-your-key-here"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create secret for OpenAI API key if it doesn't exist
if kubectl get secret todo-secrets &> /dev/null; then
    echo "✅ Secret todo-secrets already exists"
else
    echo "🔐 Creating secret for OpenAI API key..."
    kubectl create secret generic todo-secrets \
      --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-placeholder}" \
      --dry-run=client -o yaml | kubectl apply -f -
    echo "✅ Secret created"
fi
echo ""

# Deploy with Helm
echo "📦 Deploying with Helm..."
cd "$HELM_CHART"

if helm list | grep -q todo-chatbot; then
    echo "Upgrading existing release..."
    helm upgrade todo-chatbot . --wait --timeout=5m
else
    echo "Installing new release..."
    helm install todo-chatbot . --wait --timeout=5m
fi
echo ""

echo "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Show deployment status
echo "📊 Deployment status:"
kubectl get pods
echo ""
kubectl get services
echo ""

# Get frontend URL
echo "🌐 Frontend URL:"
minikube service todo-chatbot-frontend --url
echo ""

echo "💡 Next steps:"
echo "  1. Access frontend: minikube service todo-chatbot-frontend"
echo "  2. Check logs: kubectl logs -f deployment/todo-chatbot-backend"
echo "  3. Verify deployment: ./phase-4/scripts/verify-deployment.sh"
echo "  4. Cleanup: ./phase-4/scripts/cleanup.sh"
