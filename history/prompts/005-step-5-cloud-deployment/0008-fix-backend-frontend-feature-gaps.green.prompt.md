---
name: Fix Backend-Frontend Feature Gaps
description: Fixed 4 gaps between backend API and frontend UI - tag management endpoints, pagination, reminder notifications (language already implemented)
type: green
stage: green
date: 2026-04-30
surface: agent
model: claude-sonnet-4-6
feature: 005-step-5-cloud-deployment
branch: 005-step-5-cloud-deployment
user: Sami Ullah
labels: ["frontend", "tags", "pagination", "reminders", "api-client"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

## Prompt

check my project if all backend features implemented in ui or not? check step by step, first list all the features and then check one by one

[follow-up] fix all of them

## Response

Performed a full backend-vs-frontend feature audit, identified 4 gaps, confirmed Fix 3 (language) was already implemented, then fixed the remaining 3:

### Fix 1 — Tag management endpoints (dedicated API + inline UI)
- `frontend/src/lib/api/tasks.ts`: Added `tagApi` with `addTag()` and `removeTag()` calling the dedicated `/tags` endpoints
- `frontend/src/components/tasks/TaskItem.tsx`: Added `onTagAdd` / `onTagRemove` props; tags now show an X button (remove) and an inline input to add new tags without opening the full edit form; optimistic updates with revert on error
- `frontend/src/components/tasks/TaskList.tsx`: Added `onTagAdd` / `onTagRemove` to props, passed down to TaskItem

### Fix 2 — Pagination
- `frontend/src/components/tasks/Pagination.tsx`: New component — prev/next buttons + page number buttons with ellipsis for large page counts; shows "Showing X–Y of Z tasks"
- `frontend/src/app/tasks/page.tsx`: Added `currentPage`, `PAGE_SIZE=10`, `totalTasks` state; passes `limit`/`offset` query params; resets to page 1 when search/filter/sort changes; renders `<Pagination>` below TaskList; updated task count display to use `totalTasks`

### Fix 3 — Language switcher
Already implemented: ChatInterface uses `useI18n()` context and passes `language` to `chatkitApi.streamResponse()`; `<LanguageSwitcher>` is rendered in the ChatInterface header. No changes needed.

### Fix 4 — Reminder notifications
- `frontend/src/lib/hooks/useReminderNotifications.ts`: New hook — polls every 60 seconds, fires `onReminder(task)` when `now >= reminderTime && now < dueDate`; uses `sessionStorage` to track shown reminders so page refresh doesn't re-fire
- `frontend/src/app/tasks/page.tsx`: Wired `useReminderNotifications(tasks, handleReminder)`; `handleReminder` shows a warning toast with human-readable time label

## Files Modified/Created

 - frontend/src/lib/api/tasks.ts
 - frontend/src/components/tasks/TaskItem.tsx
 - frontend/src/components/tasks/TaskList.tsx
 - frontend/src/app/tasks/page.tsx
 - frontend/src/components/tasks/Pagination.tsx (new)
 - frontend/src/lib/hooks/useReminderNotifications.ts (new)

## Tests

 - TypeScript check: 0 new errors (3 pre-existing heroicons import errors unrelated to these changes)
