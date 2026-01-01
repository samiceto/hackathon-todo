---
id: 0008
title: Implement Phase 5 User Story 3
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 001-step-1-core-features
branch: 001-step-1-core-features
user: agent
command: /sp.implement
labels: ["implementation", "user-story-3", "phase-5", "ui", "mark-complete", "green"]
links:
  spec: specs/001-step-1-core-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/hackathon_todo/ui.py
  - tests/test_ui.py
  - specs/001-step-1-core-features/tasks.md
  - manual_test_phase5.py
tests:
  - tests/test_ui.py (14 new tests, all passed)
  - Manual test (5 test scenarios, all passed)
---

## Prompt

execute implementation of phase 5

## Response snapshot

Successfully completed Phase 5 (User Story 3 - Mark Tasks as Complete):

**T018 & T019 - Implement mark_complete_ui() and get_task_id()** (79 additional lines to ui.py):
- Added get_task_id(storage, prompt) function to src/hackathon_todo/ui.py:

  **get_task_id(storage: TaskStorage, prompt: str) -> int**:
  - Gets valid task ID from user with retry loop
  - Validates numeric input (rejects "abc", "xyz", etc.)
  - Validates task exists in storage (rejects non-existent IDs like 99)
  - Retry loop with clear error messages
  - Strips whitespace from input
  - Returns valid task ID

- Added mark_complete_ui(storage) function to src/hackathon_todo/ui.py:

  **mark_complete_ui(storage: TaskStorage) -> None**:
  - Displays header: "--- Mark Task Complete/Incomplete ---"
  - Checks if tasks exist (shows "No tasks available. Add a task first!" if empty)
  - Gets valid task ID using get_task_id() helper
  - Toggles task completion status (complete ↔ incomplete)
  - Displays success message with updated status
  - Shows visual indicator: ✓ for complete, ○ for incomplete
  - Displays task title with new status

**T020 - Write toggle completion tests** (14 new tests):
- Added TestGetTaskID class to tests/test_ui.py (6 tests):
  - test_get_task_id_with_valid_input: Returns correct task ID
  - test_get_task_id_rejects_non_numeric: Rejects "abc" and retries
  - test_get_task_id_rejects_non_existent_id: Rejects ID 99 when not in storage
  - test_get_task_id_multiple_retries: Handles "abc", "99", "xyz" before "1"
  - test_get_task_id_with_multiple_tasks: Validates against correct task
  - test_get_task_id_strips_whitespace: Strips "  1  " to "1"

- Added TestMarkCompleteUI class to tests/test_ui.py (8 tests):
  - test_mark_complete_ui_marks_task_complete: Toggles incomplete → complete
  - test_mark_complete_ui_toggles_complete_to_incomplete: Toggles complete → incomplete
  - test_mark_complete_ui_with_empty_storage: Shows "No tasks available" message
  - test_mark_complete_ui_handles_invalid_id: Retries on non-existent ID
  - test_mark_complete_ui_handles_non_numeric_input: Retries on "abc"
  - test_mark_complete_ui_displays_header: Shows correct header
  - test_mark_complete_ui_with_multiple_tasks: Toggles specific task only
  - test_mark_complete_ui_multiple_toggles: Handles multiple toggles on same task

**T021 - Manual test** (5 scenarios):
- Created manual_test_phase5.py with comprehensive tests:
  - TEST 1: Attempt to mark task complete with empty storage ✓
  - TEST 2: Mark incomplete task as complete ✓
  - TEST 3: Toggle complete task back to incomplete ✓
  - TEST 4: Mark multiple tasks complete (mixed status) ✓
  - TEST 5: Input validation verification ✓
- All manual tests passed with visual verification

**Test Results**:
```
85 passed in 6.38s (71 from Phases 1-4 + 14 new Phase 5 tests)
Coverage: 100.00% (106/106 statements)
- models.py: 100% (23/23)
- storage.py: 100% (32/32)
- ui.py: 100% (50/50) ← Grew from 29 to 50 statements
```

**Module Size**: ui.py = 203 lines (still well under 300-line limit) ✅

**User Story 3 Acceptance Criteria Verified**:
✓ Task status changes from incomplete to complete
✓ Status toggles (complete ↔ incomplete)
✓ Non-existent task IDs show error message
✓ Invalid input (non-numeric) shows error and retry
✓ Visual indicators (✓ and ○) work correctly
✓ Success messages display with updated status

**Sample Output from Manual Test**:
```
--- Mark Task Complete/Incomplete ---

[1] ✓ Buy groceries
    Milk, eggs, bread
[2] ○ Write tests
    Complete unit tests for models
[3] ✓ Deploy app
    Push to production

Task 1 marked as complete!
[1] ✓ Buy groceries
```

## Outcome

- ✅ Impact: Phase 5 complete - User Story 3 (Mark Tasks as Complete) implemented with full toggle functionality
- 🧪 Tests: 14 new tests passed + manual validation, 100% coverage maintained (106/106 statements)
- 📁 Files: Updated ui.py (+79 lines to 203 total), test_ui.py (+14 tests to 34 total), manual_test_phase5.py, tasks.md
- 🔁 Next prompts: Continue with Phase 6-7 (Update/Delete - P3 priorities) for full CRUD, or skip to Phase 8 (Integration) for working application
- 🧠 Reflection: Core CRUD operations nearly complete (Create, Read, Toggle/Update Complete); input validation robust with retry loops; status toggling intuitive with visual feedback; comprehensive test coverage ensures reliability; 3 of 5 user stories complete (Add, View, Mark Complete)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All tests PASS (85/85), Coverage PASS (100% > 90%), Module size PASS (203 lines < 300), Manual test PASS (5/5 scenarios), User Story 3 PASS (all acceptance criteria met)
- Prompt variant (if applicable): Standard implementation workflow with TDD approach for UI functions
- Next experiment (smallest change to try): Phase 6 (Update Task Details) and Phase 7 (Delete Tasks) to complete full CRUD operations, then Phase 8 (Integration) to create working menu-driven application
