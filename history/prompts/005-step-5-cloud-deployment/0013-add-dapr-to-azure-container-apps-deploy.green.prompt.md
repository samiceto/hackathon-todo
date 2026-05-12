---
name: Add Dapr to Azure Container Apps Deployment
description: Updated GitHub Actions workflow to enable Dapr on Azure Container Apps, add reminder-service deployment, and protect credentials file from git
type: green
stage: green
date: 2026-05-12
surface: agent
model: claude-sonnet-4-6
feature: 005-step-5-cloud-deployment
branch: 005-step-5-cloud-deployment
user: Sami Ullah
command: update azure deployment with dapr
labels: ["dapr", "azure-container-apps", "github-actions", "reminder-service", "gitignore"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .gitignore
  - .github/workflows/deploy.yml
tests: []
---

## Prompt

okey tell me this network issue is because of memory? my pc have low mameory right? what if we deploy this project to azure will it work?

this project is already deployed on azure and running, i deployed it and created github action workflow without dapr, then i enabled dapr, now tell me how to update so the deployed project be updated with dapr, and also for local testing i added actual credentials in values-dev.local.yaml file, so dont push it without removal and adding placeholders

## Response

### Root Cause Confirmed
Local network errors are caused by memory exhaustion (86MB free RAM, swap at 95%). Azure Container Apps resolves this by providing dedicated resources, stable networking, and managed Kubernetes.

### Changes Made

**1. `.gitignore`** — Added `helm/**/values-dev.local.yaml` to prevent credentials from being committed. The existing pattern `helm/**/values-local.yaml` didn't match the actual filename.

**2. `.github/workflows/deploy.yml`** — Completely updated to add Dapr support:
- Added step to retrieve Container Apps Environment name dynamically
- Added Dapr pubsub component registration (Azure Service Bus, name: `pubsub-kafka`)
- Added Dapr cron binding component registration (name: `cron-reminder-processor`, `@every 1m`)
- Updated backend deploy to enable Dapr (`--dapr-enabled --dapr-app-id todo-backend --dapr-app-port 8000`)
- Added reminder-service build + push
- Added reminder-service create-or-update with Dapr enabled (`--dapr-app-id todo-reminder-service --dapr-app-port 8001`, internal ingress)

### User Action Required

**1. Create Azure Service Bus namespace** (one-time, in Azure Portal):
- Create → Service Bus namespace → Standard tier (needed for Topics)
- Go to "Shared access policies" → RootManageSharedAccessKey → copy Primary Connection String

**2. Add GitHub Secret** (Settings → Secrets → Actions):
- `SERVICE_BUS_CONNECTION_STRING` = the connection string from step 1

**3. Push to main** — workflow runs automatically and deploys everything with Dapr enabled.

### How Dapr Works in Azure Container Apps
- No `dapr init` needed — Azure manages the Dapr runtime
- Components are registered at the Environment level (not Kubernetes CRDs)
- Dapr sidecar auto-injects when `--dapr-enabled` is set on a Container App
- Backend publishes task events → Azure Service Bus → reminder-service subscribes
- Cron binding triggers reminder-service every minute (built-in, no external service)
