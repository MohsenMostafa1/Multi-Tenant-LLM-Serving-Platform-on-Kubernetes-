# Multi-Tenant-LLM-Serving-Platform-on-Kubernetes-
A self-service platform where multiple “tenants” (teams) can deploy different open-source LLMs behind a unified API, with auto-scaling, rate limiting, and usage tracking

## Features
- Multiple LLMs (DeepSeek, Llama) served via vLLM
- Kubernetes deployment with HPA auto-scaling
- FastAPI gateway with JWT auth + Redis rate limiting (100 req/min per tenant)
- GitLab CI/CD (build → test → deploy)
- Prometheus + Grafana ready

## Deploy Locally (K3d)
```bash
k3d cluster create llm-platform --servers 1 --agents 3 --port "8080:80@loadbalancer"
kubectl create ns llm-platform
kubectl apply -f k8s/namespace.yaml -f k8s/redis-deployment.yaml -f k8s/worker-deepseek.yaml -f k8s/worker-llama.yaml -f k8s/gateway-deployment.yaml
