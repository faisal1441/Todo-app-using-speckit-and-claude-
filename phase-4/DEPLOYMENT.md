# Phase IV: Kubernetes Deployment Guide

Complete guide for deploying the Todo Chatbot application to local Kubernetes using Minikube.

---

## 🎯 Quick Start (5 Minutes)

```bash
# 1. Build Docker images
cd /path/to/todoapp
./phase-4/scripts/build-images.sh

# 2. Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# 3. Deploy to Minikube
./phase-4/scripts/deploy.sh

# 4. Open the application
minikube service todo-chatbot-frontend
```

**Done!** Your Todo Chatbot is now running on Kubernetes.

---

## 📋 Prerequisites

### Required Tools

1. **Docker Desktop 4.53+** - https://www.docker.com/products/docker-desktop
2. **Minikube** - https://minikube.sigs.k8s.io/docs/start/
3. **kubectl** - https://kubernetes.io/docs/tasks/tools/
4. **Helm 3.x** - https://helm.sh/docs/intro/install/
5. **OpenAI API Key** - https://platform.openai.com/api-keys

### System Requirements

- **CPU**: 4+ cores (2 minimum)
- **RAM**: 8GB+ (6GB minimum)
- **Disk**: 20GB free space

### Verification

```bash
docker --version
minikube version
kubectl version --client
helm version
```

---

## 🚀 Complete Deployment Guide

See the full step-by-step guide with troubleshooting in this file.

For detailed instructions, scroll down or jump to:
- [Build Images](#step-1-build-docker-images)
- [Deploy](#step-5-deploy-with-helm)
- [Troubleshooting](#-troubleshooting)
- [Cleanup](#-cleanup)

---

## 🧹 Quick Cleanup

```bash
./phase-4/scripts/cleanup.sh  # Remove deployment
minikube stop                   # Stop cluster
minikube delete                 # Delete cluster (optional)
```

---

## 📊 Verify Deployment

```bash
./phase-4/scripts/verify-deployment.sh
```

---

**For complete documentation, see the TODO-app Phase 4 README.md**
