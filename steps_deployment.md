# Step 5: Cloud Deployment Guide

Docker Hub username: `samiceto`
Azure resource group: `todoapp`
Azure location: `eastus`
Container Apps environment: `todo-env`

---

## Phase 1: One-Time Azure Setup (Manual, Run Once)

```bash
# Create resource group
az group create --name todoapp --location eastus

# Create Container Apps environment
az containerapp env create \
  --name todo-env \
  --resource-group todoapp \
  --location eastus
```

---

## Phase 2: First-Time Deployment (Manual)

### Step 1: Build & push backend image
```bash
docker build -t samiceto/todo-backend:latest ./backend/api/
docker push samiceto/todo-backend:latest
```

### Step 2: Deploy backend to Azure
```bash
az containerapp create \
  --name todo-backend \
  --resource-group todoapp \
  --environment todo-env \
  --image samiceto/todo-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    DATABASE_URL=<your-neon-db-url> \
    OPENAI_API_KEY=<your-openai-key> \
    CORS_ORIGINS=*
```

### Step 3: Get backend URL
```bash
az containerapp show \
  --name todo-backend \
  --resource-group todoapp \
  --query properties.configuration.ingress.fqdn -o tsv
```
Copy the output URL — you need it for the next step.

### Step 4: Build & push frontend image with backend URL
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://<backend-url-from-step-3> \
  -t samiceto/todo-frontend:latest \
  ./frontend/

docker push samiceto/todo-frontend:latest
```

### Step 5: Deploy frontend to Azure
```bash
az containerapp create \
  --name todo-frontend \
  --resource-group todoapp \
  --environment todo-env \
  --image samiceto/todo-frontend:latest \
  --target-port 3000 \
  --ingress external
```

### Step 6: Get frontend URL
```bash
az containerapp show \
  --name todo-frontend \
  --resource-group todoapp \
  --query properties.configuration.ingress.fqdn -o tsv
```

### Step 7: Update backend CORS with real frontend URL
```bash
az containerapp update \
  --name todo-backend \
  --resource-group todoapp \
  --set-env-vars CORS_ORIGINS=https://<frontend-url-from-step-6>
```

---

## Phase 3: GitHub Secrets Setup

Go to: GitHub repo → Settings → Secrets and variables → Actions → Repository secrets

| Secret | Value |
|---|---|
| `DOCKER_HUB_USERNAME` | `samiceto` |
| `DOCKER_HUB_ACCESS_TOKEN` | Docker Hub → Account Settings → Security → New Access Token |
| `AZURE_CREDENTIALS` | JSON output from `az ad sp create-for-rbac` (todoappPrincipal) |
| `DATABASE_URL` | Neon dashboard → your project → connection string |
| `OPENAI_API_KEY` | platform.openai.com → API keys |

---

## Phase 4: GitHub Actions Workflow

Create file: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1

      - name: Log in to Docker Hub
        run: |
          echo ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }} | docker login \
            -u ${{ secrets.DOCKER_HUB_USERNAME }} --password-stdin

      # ── Backend ──────────────────────────────────────
      - name: Build and push backend image
        run: |
          docker build -t ${{ secrets.DOCKER_HUB_USERNAME }}/todo-backend:latest ./backend/api/
          docker push ${{ secrets.DOCKER_HUB_USERNAME }}/todo-backend:latest

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy backend
        run: |
          az containerapp update \
            --name todo-backend \
            --resource-group todoapp \
            --image ${{ secrets.DOCKER_HUB_USERNAME }}/todo-backend:latest \
            --set-env-vars \
              DATABASE_URL=${{ secrets.DATABASE_URL }} \
              OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}

      - name: Get backend URL
        id: backend-url
        run: |
          URL=$(az containerapp show \
            --name todo-backend \
            --resource-group todoapp \
            --query properties.configuration.ingress.fqdn -o tsv)
          echo "url=https://$URL" >> $GITHUB_OUTPUT

      # ── Frontend ─────────────────────────────────────
      - name: Build and push frontend image
        run: |
          docker build \
            --build-arg NEXT_PUBLIC_API_URL=${{ steps.backend-url.outputs.url }} \
            -t ${{ secrets.DOCKER_HUB_USERNAME }}/todo-frontend:latest \
            ./frontend/
          docker push ${{ secrets.DOCKER_HUB_USERNAME }}/todo-frontend:latest

      - name: Deploy frontend
        run: |
          az containerapp update \
            --name todo-frontend \
            --resource-group todoapp \
            --image ${{ secrets.DOCKER_HUB_USERNAME }}/todo-frontend:latest
```

> Note: Workflow uses `az containerapp update` (not `create`) because the apps already exist from Phase 2.

---

## After First Deployment

Every `git push` to `main` → GitHub Actions automatically:
1. Builds new backend image → pushes to Docker Hub → deploys to Azure
2. Gets backend URL → builds frontend with correct URL → pushes → deploys to Azure

---

## Useful Commands

```bash
# Check deployed apps
az containerapp list --resource-group todoapp -o table

# View backend logs
az containerapp logs show --name todo-backend --resource-group todoapp --follow

# View frontend logs
az containerapp logs show --name todo-frontend --resource-group todoapp --follow

# Get app URLs
az containerapp show --name todo-backend --resource-group todoapp --query properties.configuration.ingress.fqdn -o tsv
az containerapp show --name todo-frontend --resource-group todoapp --query properties.configuration.ingress.fqdn -o tsv
```