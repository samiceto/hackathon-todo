---
name: Fix chat position, search UX, and chatbot connectivity
description: Fix 5 UI/backend bugs: chat panel position, search white-screen, pre-fetch UX, chatbot API field mismatch, and search crash
type: green
stage: green
date: 2026-05-01
surface: agent
model: claude-sonnet-4-6
feature: 005-step-5-cloud-deployment
branch: 005-step-5-cloud-deployment
user: Sami Ullah
command: chat message
labels: ["bug-fix", "ux", "chatbot", "search", "frontend", "backend"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
---

## Prompt

1. the chat boat is opening to the left side in laptop , fix it i want to be open on right side exact same where it's collapsable button floating
2. when i serch task in search box , intire app turn white and loading , i want to stay visible and perform loading
3. i want to bring data from database when first load so when i search it does not take time
4. the cahtboat is not responding i have openapi key in .env file in backend, is there some issue?
5. the app crush while searching task check if there is bug.

## Response

Fixed 5 bugs across frontend and backend:

**1. Chat panel opens to the left (FloatingChat.tsx)**
- Root cause: `left-0` from mobile styles was not overridden at desktop breakpoint
- Fix: Added `sm:left-auto` so the panel anchors to the right side (next to the FAB) on desktop

**2 & 5. Search causes white screen / app crash (tasks/page.tsx)**
- Root cause: `if (isLoading) return <Loading>` replaced the entire page DOM on every fetch including search/filter/page changes
- Fix: Added `isInitialLoad` state — full-page spinner only on the very first load; subsequent fetches show a small inline spinner above the task list while existing tasks remain visible

**3. Pre-fetch UX improvement (tasks/page.tsx)**
- Tasks stay visible during search/filter refreshes (same fix as #2)
- Inline "Updating…" indicator appears during background fetch so user knows it's working

**4. Chatbot not responding (chatkit.ts, ChatInterface.tsx, chatkit/server.py)**
- Root cause 1: Frontend sent `thread_id` (string) but backend expected `conversation_id` (int) — Pydantic accepted it but created a new conversation every message
- Root cause 2: `conversationId` state was never updated from the server response, so conversation history was lost between messages
- Root cause 3: Backend used `gpt-4` model — if account lacks GPT-4 access, fails silently
- Root cause 4: Errors inside the SSE stream generator were swallowed without notifying the frontend
- Root cause 5: `values-dev.yaml` had `sk-dummy-key-for-testing` as the OpenAI key for k8s deployments
- Fixes:
  - Changed `thread_id` → `conversation_id` (int) in all request payloads
  - Added `onConversationId` callback to capture returned conversation_id and persist it in ChatInterface state
  - Changed model to `gpt-3.5-turbo` (widely available)
  - Added try/except in SSE generator to stream errors back to frontend
  - Removed dummy key from values-dev.yaml; documented `--set backend.secrets.openaiApiKey=<KEY>` pattern

## Files Modified

- frontend/src/components/chat/FloatingChat.tsx
- frontend/src/app/tasks/page.tsx
- frontend/src/lib/api/chatkit.ts
- frontend/src/components/chat/ChatInterface.tsx
- backend/api/src/chatkit/server.py
- backend/api/src/api/chatkit.py
- helm/todo-app/values-dev.yaml
