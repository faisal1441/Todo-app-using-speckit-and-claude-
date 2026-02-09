#!/bin/bash
# Cleanup Todo Chatbot deployment

echo "🧹 Cleaning up Todo Chatbot deployment..."
echo ""

# Uninstall Helm release
if helm list | grep -q todo-chatbot; then
    echo "📦 Uninstalling Helm release..."
    helm uninstall todo-chatbot
    echo "✅ Helm release uninstalled"
else
    echo "ℹ️  No Helm release found"
fi
echo ""

# Delete secret
if kubectl get secret todo-secrets &> /dev/null; then
    echo "🔐 Deleting secret..."
    kubectl delete secret todo-secrets
    echo "✅ Secret deleted"
fi
echo ""

# Delete any remaining resources
echo "🗑️  Deleting remaining resources..."
kubectl delete all -l app.kubernetes.io/instance=todo-chatbot 2>/dev/null || echo "No resources to delete"
kubectl delete pvc -l app.kubernetes.io/instance=todo-chatbot 2>/dev/null || echo "No PVCs to delete"
echo ""

echo "✅ Cleanup complete!"
echo ""
echo "💡 Optional:"
echo "  Stop Minikube: minikube stop"
echo "  Delete Minikube: minikube delete"
echo "  Remove Docker images: docker rmi todoapp/backend todoapp/frontend todoapp/chatbot"
