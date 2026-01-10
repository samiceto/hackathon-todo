---
id: 0005
title: Implement Phase 6 Update Existing Tasks
stage: green
date: 2026-01-09
surface: agent
model: claude-sonnet-4-5
feature: 002-step-2-web-app
branch: 002-step-2-web-app
user: samiullah
command: /sp.implement
labels: ["phase-6", "user-story-4", "task-editing", "nextjs", "state-management"]
links:
  spec: /specs/002-step-2-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/components/tasks/TaskForm.tsx (modified - added edit mode)
  - frontend/src/app/tasks/page.tsx (modified - added edit state management)
  - specs/002-step-2-web-app/tasks.md (modified - marked T068-T074 complete)
tests:
  - Manual testing required: Edit task flow, form validation, API integration
---

## Prompt

continue with phase 6

User requested to continue implementing Phase 6 (User Story 4 - Update Existing Tasks) after completing Phase 5, using Next.js and frontend-design skills.

## Response snapshot

Successfully implemented Phase 6 (User Story 4 - Update Existing Tasks) with proper Next.js Client Component state management patterns:

**Backend Status:**
All backend components already existed from previous phases:
- T068: UpdateTaskRequest schema in task.py ✅
- T069: update_task service method in tasks.py ✅
- T070: PUT /api/{user_id}/tasks/{id} endpoint in tasks.py ✅
- T072: updateTask API method in tasks.ts ✅

**Frontend Implementation:**

1. **TaskForm Component** (`frontend/src/components/tasks/TaskForm.tsx`):
   - Added `editTask` prop to accept task data for editing
   - Added `onTaskUpdated` callback for update operations
   - Added `useEffect` hook to populate form when editTask changes
   - Modified form submission to handle both create and update modes
   - Updated header text to show "Edit Task" vs "New Task"
   - Updated button text to show "Update Task" vs "Create Task"
   - Modified cancel behavior to work with edit mode
   - Form automatically expands when in edit mode

2. **Tasks Page** (`frontend/src/app/tasks/page.tsx`):
   - Added state management for edit mode:
     - `editingTask` state to track which task is being edited
     - `isUpdatingTask` state for loading during update
   - Created `handleEditTask` function to open edit form with task data
   - Created `handleUpdateTask` function with API integration:
     - Calls taskApi.updateTask with user ID and task data
     - Updates task in local state optimistically
     - Closes edit form on success
     - Handles errors with user-friendly messages
   - Created `handleCancelEdit` function to close edit form
   - Conditional form rendering:
     - Shows edit form when editingTask is set
     - Shows create form otherwise
   - Connected edit button from TaskItem to handleEditTask
   - Updated success notice to reflect Phase 6 completion

3. **Integration Flow**:
   - User clicks edit button on TaskItem → hover reveals edit icon
   - handleEditTask finds task and sets editingTask state
   - TaskForm re-renders in edit mode with task data populated
   - User modifies title/description → real-time validation
   - User clicks "Update Task" → handleUpdateTask called
   - API updates task → local state updated → form closes
   - Task list refreshes with updated task
   - Cancel button closes form without saving

**Next.js Patterns Used:**
- Client Component state management with useState
- Effect hooks for form population (useEffect)
- Optimistic UI updates for better UX
- Conditional rendering based on edit state
- Event handler composition with proper typing
- Error boundary patterns with error state

**Design Consistency:**
- Maintained "Refined Productivity" aesthetic
- Reused existing Input and Button components
- Consistent form validation and error handling
- Smooth transitions between create and edit modes
- Edit buttons appear on hover (opacity transition)
- Same form UI for both create and edit (reduces cognitive load)

**Tasks Completed:**
- T068: Backend schema ✅ (already existed)
- T069: Backend service method ✅ (already existed)
- T070: Backend PUT endpoint ✅ (already existed)
- T071: Edit mode in TaskForm ✅
- T072: API client method ✅ (already existed)
- T073: Edit button integration ✅ (already existed in TaskItem)
- T074: Cancel functionality ✅

## Outcome

- ✅ Impact: Phase 6 (User Story 4) fully implemented. Users can now edit existing tasks through an elegant form with the same validation and UX as task creation.
- 🧪 Tests: Manual testing required to verify: click edit → form opens with data → modify fields → save → verify updates in list and persist
- 📁 Files: Modified TaskForm component (added edit mode), updated tasks page (added edit state management), marked 7 tasks complete in tasks.md
- 🔁 Next prompts: Implement Phase 7 (User Story 5 - Toggle Task Completion) or Phase 8 (User Story 6 - Delete Tasks) - both can run in parallel as they only depend on US1+US2
- 🧠 Reflection: Next.js Client Component patterns made state management straightforward. The conditional rendering approach (show edit form vs create form) provides a clean UX where users focus on one action at a time.

## Evaluation notes (flywheel)

- Failure modes observed: None - integration was smooth since TaskItem already had edit button implemented
- Graders run and results (PASS/FAIL): N/A - manual testing required
- Prompt variant (if applicable): Used Next.js skill for proper state management patterns
- Next experiment (smallest change to try): Add success toast notifications on update, or implement Phase 7/8 in parallel
