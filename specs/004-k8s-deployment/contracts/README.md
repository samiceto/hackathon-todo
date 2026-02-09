# Kubernetes Resource Contracts

**Feature**: 004-k8s-deployment
**Date**: 2026-01-24
**Phase**: Phase 1 - Design & Contracts

## Overview

This directory contains Kubernetes resource specifications that define the contract for deploying the Todo Chatbot application to a local Minikube cluster. These specifications will be used as templates for creating the actual Helm chart in `helm/todo-app/templates/`.

## Resource Files

| File | Resource Type | Purpose |
|------|---------------|---------|
| `backend-deployment.yaml` | Deployment | Backend FastAPI application pods (2 replicas) |
| `frontend-deployment.yaml` | Deployment | Frontend Next.js application pods (2 replicas) |
| `backend-service.yaml` | Service | Expose backend API within cluster (ClusterIP) |
| `frontend-service.yaml` | Service | Expose frontend to host machine (NodePort) |
| `backend-configmap.yaml` | ConfigMap | Non-sensitive backend configuration |
| `frontend-configmap.yaml` | ConfigMap | Non-sensitive frontend configuration |
| `backend-secret.yaml` | Secret | Sensitive backend data (API keys, tokens) |

## Key Specifications

### Deployments

**Backend Deployment**:
- **Replicas**: 2 (high availability)
- **Image**: `todo-backend:latest`
- **Port**: 8000
- **Strategy**: RollingUpdate (maxSurge: 1, maxUnavailable: 0)
- **Health Checks**: Liveness and readiness probes on `/health`
- **Resources**: Requests (256Mi/250m), Limits (512Mi/500m)
- **Security**: Non-root user (UID 1000), capabilities dropped

**Frontend Deployment**:
- **Replicas**: 2 (high availability)
- **Image**: `todo-frontend:latest`
- **Port**: 3000
- **Strategy**: RollingUpdate (maxSurge: 1, maxUnavailable: 0)
- **Health Checks**: Liveness and readiness probes on `/`
- **Resources**: Requests (128Mi/100m), Limits (256Mi/200m)
- **Security**: Non-root user (UID 1001), capabilities dropped

### Services

**Backend Service** (ClusterIP):
- Internal cluster access only
- Port: 8000
- Used by frontend to communicate with backend API

**Frontend Service** (NodePort for Minikube):
- External access from host machine
- Port: 3000
- NodePort: 30000 (configurable via values)
- Access URL: `http://<minikube-ip>:30000`

### Configuration

**Backend ConfigMap**:
- `CORS_ORIGINS`: Allowed CORS origins
- `DATABASE_URL`: Neon PostgreSQL connection string
- `LOG_LEVEL`: Logging verbosity (info, debug, warning, error)
- `ENVIRONMENT`: Application environment (production, development)

**Frontend ConfigMap**:
- `NEXT_PUBLIC_API_URL`: Backend API URL (internal cluster service)
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: OpenAI ChatKit domain key
- `NEXT_PUBLIC_ENVIRONMENT`: Application environment

**Backend Secret**:
- `OPENAI_API_KEY`: OpenAI API key for AI chatbot (REQUIRED)
- `BETTER_AUTH_SECRET`: Shared secret for JWT verification (REQUIRED)
- `DATABASE_PASSWORD`: Database password (optional, if separated from URL)

## Helm Integration

These contract specifications use Helm templating syntax:

- `{{ include "todo-app.fullname" . }}`: Generates full resource name
- `{{ .Values.backend.replicas }}`: References values from `values.yaml`
- `{{ .Values.backend.secrets.openaiApiKey | required "..." }}`: Required value validation
- `{{- include "todo-app.labels" . | nindent 4 }}`: Template helpers for labels

## Values Hierarchy

Configuration values are sourced from:

1. **Default values** (`values.yaml`): Production defaults
2. **Environment overrides** (`values-dev.yaml`): Minikube-specific settings
3. **Runtime flags** (`--set`): Secrets provided at deployment time

Example deployment command:

```bash
helm install todo-app ./helm/todo-app \
  --set backend.secrets.openaiApiKey="sk-..." \
  --set backend.secrets.betterAuthSecret="..." \
  --set frontend.config.openaiDomainKey="..." \
  -f helm/todo-app/values-dev.yaml
```

## Security Considerations

### Secrets Management

- **NEVER** commit actual secret values to Git
- Provide secrets via `--set` flags at deployment time
- Use `.helmignore` to exclude sensitive files
- Consider using Kubernetes native secrets or external secret managers

### Pod Security

- All containers run as non-root users
- Capabilities are dropped to minimum required
- Resource limits prevent resource exhaustion attacks
- Read-only root filesystem where possible

### Network Security

- Backend uses ClusterIP (internal access only)
- Frontend uses NodePort (development) or LoadBalancer (production)
- Network policies can be added for additional isolation (future enhancement)

## Implementation Notes

During the implementation phase (`/sp.implement`), these specifications will be:

1. Copied to `helm/todo-app/templates/` directory
2. Validated against Helm chart best practices
3. Tested with `helm lint` and `helm template`
4. Deployed to Minikube cluster
5. Verified with health checks and integration tests

## References

- Kubernetes API Reference: https://kubernetes.io/docs/reference/kubernetes-api/
- Helm Template Guide: https://helm.sh/docs/chart_template_guide/
- Security Best Practices: https://kubernetes.io/docs/concepts/security/

---

**Contracts Complete**: 2026-01-24
**Next Step**: Create quickstart.md deployment guide
