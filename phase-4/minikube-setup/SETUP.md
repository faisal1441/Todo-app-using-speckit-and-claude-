# Minikube Setup Guide

This guide walks through setting up a local Kubernetes cluster using Minikube for the Todo Chatbot application.

## Prerequisites

- **Minikube**: 1.26+
- **kubectl**: 1.24+
- **Helm**: 3.x+
- **Docker**: For building container images
- **Gordon** (Docker AI): For AI-assisted containerization (optional)

## Installation

### Windows (PowerShell)

```powershell
# Install Minikube using Chocolatey
choco install minikube

# Or download from https://minikube.sigs.k8s.io/docs/start/

# Verify installation
minikube version
kubectl version --client
helm version
```

### macOS

```bash
# Install via Homebrew
brew install minikube kubectl helm

# Verify installation
minikube version
kubectl version --client
helm version
```

### Linux (Ubuntu/Debian)

```bash
# Install Minikube
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
minikube version
kubectl version --client
helm version
```

## Starting Minikube

### Basic Startup

```bash
# Start Minikube with default settings
minikube start

# Start with specific resources (recommended)
minikube start --cpus=4 --memory=8192 --disk-size=50g

# Start with specific container runtime (Docker/Containerd)
minikube start --container-runtime=docker
```

### Configuration for Todo App

For optimal performance with the Todo Chatbot:

```bash
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=50g \
  --container-runtime=docker \
  --addons=ingress \
  --addons=dashboard
```

### Enable Addons

```bash
# Enable Ingress controller
minikube addons enable ingress

# Enable Kubernetes Dashboard
minikube addons enable dashboard

# View enabled addons
minikube addons list
```

## Docker Integration

### Using Minikube's Docker Daemon

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images directly in Minikube (no need to push to registry)
docker build -f phase-4/dockerfiles/Dockerfile.backend -t todoapp/backend:latest .
docker build -f phase-4/dockerfiles/Dockerfile.frontend -t todoapp/frontend:latest .
docker build -f phase-4/dockerfiles/Dockerfile.chatbot -t todoapp/chatbot:latest .

# List images in Minikube
docker images
```

### Reset Docker Context

```bash
# Return to local Docker daemon
eval $(minikube docker-env -u)
```

## kubectl Configuration

### Get Cluster Info

```bash
# View cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Get node details
kubectl describe nodes

# View Minikube dashboard
minikube dashboard
```

### Configure kubectl Context

```bash
# List available contexts
kubectl config get-contexts

# Switch to Minikube context
kubectl config use-context minikube

# View current context
kubectl config current-context
```

## Networking

### Access Services from Host

```bash
# Get service IP (for ClusterIP services)
minikube service <service-name> -n <namespace> --url

# Open service in browser
minikube service <service-name> -n <namespace>

# Port forward to access locally
kubectl port-forward svc/<service-name> 8080:80
```

### Local DNS Resolution

Add to `/etc/hosts` (Linux/macOS) or `%windir%\system32\drivers\etc\hosts` (Windows):

```
127.0.0.1    todoapp.local
127.0.0.1    localhost
```

Then access services via: `http://todoapp.local`

## Managing Minikube

### Useful Commands

```bash
# Check status
minikube status

# Pause cluster
minikube pause

# Unpause cluster
minikube unpause

# Stop cluster
minikube stop

# Delete cluster
minikube delete

# SSH into Minikube node
minikube ssh

# View logs
minikube logs

# Update Minikube
minikube update-context
```

## Troubleshooting

### Minikube Won't Start

```bash
# Check system resources
minikube status

# Delete and restart
minikube delete
minikube start

# Check logs
minikube logs
```

### Docker Daemon Issues

```bash
# Restart Docker daemon
minikube stop
eval $(minikube docker-env -u)
minikube start
```

### Resource Constraints

```bash
# Increase resources
minikube start --cpus=8 --memory=16384 --disk-size=100g

# Check current resource usage
kubectl top nodes
kubectl top pods
```

## Next Steps

1. Build Docker images: `./build-images.sh`
2. Deploy with Helm: `helm install todo-app ./helm-charts`
3. Access application: `minikube service todo-frontend -n default`
4. Monitor with Dashboard: `minikube dashboard`

## Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Helm Documentation](https://helm.sh/docs/)
