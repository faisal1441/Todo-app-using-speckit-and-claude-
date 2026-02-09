#!/bin/bash
# Verify Todo Chatbot deployment health

echo "🔍 Verifying Todo Chatbot deployment..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check pod status
echo "📦 Pod Status:"
kubectl get pods -l app.kubernetes.io/instance=todo-chatbot
echo ""

# Check if all pods are ready
NOT_READY=$(kubectl get pods -l app.kubernetes.io/instance=todo-chatbot --no-headers | grep -v "Running\|Completed" | wc -l)
if [ "$NOT_READY" -gt 0 ]; then
    echo "${RED}❌ Some pods are not ready${NC}"
    echo "Run 'kubectl describe pod <pod-name>' to investigate"
    echo ""
else
    echo "${GREEN}✅ All pods are running${NC}"
    echo ""
fi

# Check service endpoints
echo "🌐 Service Endpoints:"
kubectl get svc -l app.kubernetes.io/instance=todo-chatbot
echo ""

# Test health endpoints
echo "🏥 Testing health endpoints..."

BACKEND_POD=$(kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
FRONTEND_POD=$(kubectl get pods -l app=todo-frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
CHATBOT_POD=$(kubectl get pods -l app=todo-chatbot -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

# Test backend health
if [ -n "$BACKEND_POD" ]; then
    if kubectl exec "$BACKEND_POD" -- curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "${GREEN}✅ Backend health check passed${NC}"
    else
        echo "${RED}❌ Backend health check failed${NC}"
    fi
else
    echo "${YELLOW}⚠️  Backend pod not found${NC}"
fi

# Test frontend
if [ -n "$FRONTEND_POD" ]; then
    if kubectl exec "$FRONTEND_POD" -- wget -q -O- http://localhost/ > /dev/null 2>&1; then
        echo "${GREEN}✅ Frontend health check passed${NC}"
    else
        echo "${RED}❌ Frontend health check failed${NC}"
    fi
else
    echo "${YELLOW}⚠️  Frontend pod not found${NC}"
fi

# Test chatbot health
if [ -n "$CHATBOT_POD" ]; then
    if kubectl exec "$CHATBOT_POD" -- wget -q -O- http://localhost:3000/health > /dev/null 2>&1; then
        echo "${GREEN}✅ Chatbot health check passed${NC}"
    else
        echo "${RED}❌ Chatbot health check failed${NC}"
    fi
else
    echo "${YELLOW}⚠️  Chatbot pod not found${NC}"
fi
echo ""

# Show resource usage
echo "📊 Resource Usage:"
kubectl top pods -l app.kubernetes.io/instance=todo-chatbot 2>/dev/null || echo "Metrics server not available. Install with: minikube addons enable metrics-server"
echo ""

# Show recent events
echo "📰 Recent Events:"
kubectl get events --sort-by='.lastTimestamp' | tail -10
echo ""

echo "${GREEN}✅ Verification complete${NC}"
echo ""
echo "💡 Useful commands:"
echo "  View logs: kubectl logs -f deployment/todo-chatbot-backend"
echo "  Access frontend: minikube service todo-chatbot-frontend"
echo "  Port forward: kubectl port-forward svc/todo-chatbot-backend 8000:8000"
