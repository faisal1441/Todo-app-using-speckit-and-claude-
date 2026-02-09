# Phase IV: Local Kubernetes Deployment

Deploying the Todo Chatbot on a local Kubernetes cluster using Minikube, Helm Charts, and AI-assisted DevOps tools.

## Overview

This phase focuses on:
- **Containerization**: Docker containers for frontend and backend
- **Orchestration**: Local Kubernetes deployment via Minikube
- **Package Management**: Helm charts for application deployment
- **AI-Assisted DevOps**: Docker AI (Gordon), kubectl-ai, and Kagent for intelligent operations

## Project Structure

```
phase-4/
├── dockerfiles/              # Multi-stage Dockerfiles ✅
│   ├── Dockerfile.backend    # FastAPI Python app
│   ├── Dockerfile.frontend   # React + nginx
│   └── Dockerfile.chatbot    # Express TypeScript app
├── helm-charts/              # Helm chart (single umbrella) ✅
│   ├── Chart.yaml            # Chart metadata
│   ├── values.yaml           # Default configuration
│   └── templates/            # Kubernetes manifests
│       ├── _helpers.tpl      # Template helpers
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       ├── frontend-deployment.yaml
│       ├── frontend-service.yaml
│       ├── chatbot-deployment.yaml
│       ├── chatbot-service.yaml
│       ├── pvc.yaml          # Persistent volumes (optional)
│       ├── serviceaccount.yaml
│       └── ingress.yaml      # Ingress (optional)
├── scripts/                  # Deployment automation ✅
│   ├── build-images.sh       # Build all Docker images
│   ├── deploy.sh             # One-command deployment
│   ├── verify-deployment.sh  # Health check validation
│   └── cleanup.sh            # Remove deployment
├── nginx.conf                # nginx config for frontend
├── README.md                 # This file
└── DEPLOYMENT.md             # Complete deployment guide ✅
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Containerization | Docker (Docker Desktop) |
| Docker AI | Docker AI Agent (Gordon) |
| Orchestration | Kubernetes (Minikube) |
| Package Manager | Helm Charts |
| AI DevOps | kubectl-ai, Kagent |
| Application | Phase III Todo Chatbot |

## Prerequisites

- Docker Desktop 4.53+ (with Gordon enabled)
- Minikube installed
- kubectl configured
- kubectl-ai installed
- Kagent installed (optional)
- Helm 3.x installed

## Getting Started

### Quick Deployment (3 Commands)

```bash
# 1. Build Docker images
./phase-4/scripts/build-images.sh

# 2. Deploy to Minikube (starts Minikube if needed)
export OPENAI_API_KEY=sk-your-key-here
./phase-4/scripts/deploy.sh

# 3. Open the application
minikube service todo-chatbot-frontend
```

### Detailed Steps

1. **Build Docker Images**:
   ```bash
   ./phase-4/scripts/build-images.sh
   ```
   Builds optimized multi-stage images for backend, frontend, and chatbot

2. **Deploy to Minikube**:
   ```bash
   export OPENAI_API_KEY=sk-your-actual-key
   ./phase-4/scripts/deploy.sh
   ```
   Starts Minikube, loads images, deploys with Helm

3. **Verify Deployment**:
   ```bash
   ./phase-4/scripts/verify-deployment.sh
   ```
   Checks pod health, service endpoints, and runs health checks

4. **Access Application**:
   ```bash
   minikube service todo-chatbot-frontend
   ```
   Opens frontend in your browser

### Manual Deployment (Alternative)

If you prefer manual control:

```bash
# Start Minikube
minikube start --cpus=4 --memory=6144

# Build and load images
docker build -f phase-4/dockerfiles/Dockerfile.backend -t todoapp/backend:latest .
docker build -f phase-4/dockerfiles/Dockerfile.frontend -t todoapp/frontend:latest .
docker build -f phase-4/dockerfiles/Dockerfile.chatbot -t todoapp/chatbot:latest .

minikube image load todoapp/backend:latest
minikube image load todoapp/frontend:latest
minikube image load todoapp/chatbot:latest

# Create secret
kubectl create secret generic todo-secrets --from-literal=OPENAI_API_KEY=sk-your-key

# Deploy with Helm
helm install todo-chatbot ./phase-4/helm-charts --wait

# Get frontend URL
minikube service todo-chatbot-frontend --url
```

## AI-Assisted Operations

### Using Docker AI (Gordon)
```bash
docker ai "What can you do?"
docker ai "build and optimize the todo frontend image"
docker ai "analyze the Dockerfile for security"
```

### Using kubectl-ai
```bash
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"
```

### Using Kagent
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation"
kagent "generate deployment recommendations"
```

## Key Phases

1. **Containerization**: Create and test Docker images for all components
2. **Minikube Setup**: Initialize local Kubernetes cluster
3. **Helm Chart Development**: Create reusable Helm charts
4. **Deployment**: Deploy applications to Minikube
5. **Testing & Optimization**: Verify deployment and optimize resources

## Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [kubectl-ai Documentation](https://github.com/kubernetes-sigs/kubectl-ai)
- [Docker AI (Gordon)](https://docs.docker.com/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

## Implementation Status

- [x] ✅ Multi-stage Dockerfiles for all 3 services
- [x] ✅ Helm chart with templates for deployments, services, PVCs
- [x] ✅ Automated deployment scripts (build, deploy, verify, cleanup)
- [x] ✅ Comprehensive deployment documentation
- [x] ✅ Health checks and resource limits configured
- [x] ✅ Optional persistent storage support
- [x] ✅ Optional ingress configuration
- [ ] 🔄 CI/CD pipeline integration (Future enhancement)
- [ ] 🔄 kubectl-ai and Kagent integration (Optional)
- [ ] 🔄 Production deployment (AWS EKS/GKE/AKS) (Phase V)

## Configuration

### Helm Values

Edit `helm-charts/values.yaml` to customize:

- **Replicas**: Adjust `replicaCount` for each service
- **Resources**: Modify CPU/memory requests and limits
- **Storage**: Enable `persistence.enabled: true` for persistent data
- **Ingress**: Enable `ingress.enabled: true` for hostname-based routing
- **Environment**: Change environment variables per service

### Resource Requirements

**Default Configuration**:
- Backend: 2 replicas × (100m CPU, 128Mi RAM)
- Frontend: 2 replicas × (50m CPU, 64Mi RAM)
- Chatbot: 1 replica × (100m CPU, 256Mi RAM)
- **Total**: ~400m CPU, 640Mi RAM requests

**Minikube Recommendation**: 4 CPUs, 6GB RAM, 20GB disk

## Troubleshooting

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed troubleshooting guide.

**Quick fixes**:

```bash
# Check pod status
kubectl get pods

# View logs
kubectl logs -f deployment/todo-chatbot-backend

# Restart deployment
kubectl rollout restart deployment/todo-chatbot-backend

# Delete and redeploy
./phase-4/scripts/cleanup.sh
./phase-4/scripts/deploy.sh
```

## Cleanup

```bash
# Remove deployment (keeps Minikube running)
./phase-4/scripts/cleanup.sh

# Stop Minikube
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete
```
