#!/bin/bash
# Build all Docker images for Todo Chatbot

set -e

echo "🐳 Building Docker images for Todo Chatbot..."
echo ""

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PHASE4_DIR="$REPO_ROOT/phase-4"

cd "$REPO_ROOT"

# Build backend image
echo "📦 Building backend image..."
docker build \
  -f "$PHASE4_DIR/dockerfiles/Dockerfile.backend" \
  -t todoapp/backend:latest \
  .
echo "✅ Backend image built successfully"
echo ""

# Build frontend image
echo "📦 Building frontend image..."
docker build \
  -f "$PHASE4_DIR/dockerfiles/Dockerfile.frontend" \
  -t todoapp/frontend:latest \
  .
echo "✅ Frontend image built successfully"
echo ""

# Build chatbot image
echo "📦 Building chatbot image..."
docker build \
  -f "$PHASE4_DIR/dockerfiles/Dockerfile.chatbot" \
  -t todoapp/chatbot:latest \
  .
echo "✅ Chatbot image built successfully"
echo ""

echo "🎉 All images built successfully!"
echo ""
echo "📋 Built images:"
docker images | grep todoapp | head -3

echo ""
echo "💡 Next steps:"
echo "  1. Start Minikube: minikube start --cpus=4 --memory=6144"
echo "  2. Load images: minikube image load todoapp/backend:latest todoapp/frontend:latest todoapp/chatbot:latest"
echo "  3. Deploy: ./phase-4/scripts/deploy.sh"
