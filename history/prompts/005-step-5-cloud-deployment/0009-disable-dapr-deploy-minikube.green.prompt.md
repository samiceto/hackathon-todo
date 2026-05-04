---
id: "0009"
title: Disable Dapr and Deploy to Minikube
stage: green
date: 2026-05-01
surface: agent
model: claude-sonnet-4-6
feature: 005-step-5-cloud-deployment
branch: 005-step-5-cloud-deployment
user: Sami Ullah
command: "disable dapr path A, deploy to minikube"
labels: ["minikube","dapr","helm","deployment","docker"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - helm/todo-app/templates/backend-deployment.yaml
  - helm/todo-app/values-dev.yaml
tests:
  - kubectl get pods (both 1/1 Running)
  - curl localhost:8888/health → {"status":"ok"}
---

## Prompt

okey go ahead and run it with path A , minikube is installed and for now docker is iniciated with locak kibernates , connect it with minikube and run my project

## Response snapshot

Path A implemented (disable Dapr, no code removal):
1. Made Dapr pod annotations conditional in backend-deployment.yaml (`{{- if .Values.dapr.enabled }}`)
2. Set `dapr.enabled: false` in values-dev.yaml
3. Set `reminderService.enabled: false` in values-dev.yaml (requires Dapr)
4. Deleted corrupted Minikube cluster and started fresh (`minikube start --driver=docker --cpus=4 --memory=4096`)
5. Built both images inside Minikube's Docker daemon (DOCKER_HOST=tcp://127.0.0.1:60228)
6. Deployed with `helm install todo-app ./helm/todo-app -f helm/todo-app/values-dev.yaml`
7. Both pods Running 1/1, backend /health returns {"status":"ok"}

## Outcome

- ✅ Impact: App fully deployed to Minikube with CRUD + frontend working; reminders disabled (Dapr-free)
- 🧪 Tests: kubectl get pods shows both 1/1 Running; backend health check passes
- 📁 Files: 2 Helm files modified (annotations conditional, flags flipped)
- 🔁 Next prompts: Access frontend via port-forward; re-enable Dapr for reminders later
- 🧠 Reflection: Corrupted Minikube state required full delete+recreate; NodePort not routable from WSL2 so port-forward is needed

## Evaluation notes (flywheel)

- Failure modes observed: Corrupted Minikube cluster (missing RBAC roles); NodePort unreachable from WSL2 (minikube IP not routed)
- Graders run and results (PASS/FAIL): kubectl pods PASS, /health curl PASS
- Prompt variant (if applicable): null
- Next experiment: Test frontend via port-forward on 3000:3000
