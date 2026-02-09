---
id: 0006
title: Implement Phase 3 User Story 1
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 001-step-1-core-features
branch: 001-step-1-core-features
user: agent
command: /sp.implement
labels: ["implementation", "user-story-1", "phase-3", "ui", "mvp", "green"]
links:
  spec: specs/001-step-1-core-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/hackathon_todo/ui.py
  - tests/test_ui.py
  - specs/001-step-1-core-features/tasks.md
  - manual_test_phase3.py
tests:
  - tests/test_ui.py (11 tests, all passed)
  - Manual test (3 test scenarios, all passed)
---

## Prompt

execute implementation of phase 3

## Response snapshot

Successfully completed Phase 3 (User Story 1 - Add New Tasks) with MVP functionality:

**T010 & T011 - Implement UI functions** (74 lines total):
- Created src/hackathon_todo/ui.py with two functions:

  **get_non_empty_input(prompt: str) -> str**:
  - Continuously prompts user until valid non-empty input received
  - Strips leading/trailing whitespace
  - Displays error message for empty input
  - Returns validated, stripped string

  **add_task_ui(storage: TaskStorage) -> None**:
  - Interactive flow for adding new tasks
  - Prompts for title (required) using get_non_empty_input()
  - Prompts for description (optional, can be empty)
  - Creates task in storage
  - Displays success message with task ID, title, and description (if provided)
  - Shows "--- Add New Task ---" header for clear UX

**T012 - Write UI input validation tests** (11 tests):
- Created tests/test_ui.py with comprehensive coverage:

  **TestGetNonEmptyInput** (5 tests):
  - test_get_non_empty_input_with_valid_input: Returns valid input
  - test_get_non_empty_input_strips_whitespace: Strips padding
  - test_get_non_empty_input_rejects_empty_string: Rejects empty, retries
  - test_get_non_empty_input_rejects_whitespace_only: Rejects whitespace, retries
  - test_get_non_empty_input_multiple_retries: Handles 3+ retry attempts

  **TestAddTaskUI** (6 tests):
  - test_add_task_ui_with_title_and_description: Creates task with both fields
  - test_add_task_ui_with_title_only: Creates task with empty description
  - test_add_task_ui_rejects_empty_title: Validation error handling
  - test_add_task_ui_strips_whitespace_from_inputs: Input normalization
  - test_add_task_ui_assigns_sequential_ids: ID generation verification
  - test_add_task_ui_displays_header: UX header display

**T013 - Manual test** (3 scenarios):
- Created manual_test_phase3.py with simulation tests:
  - TEST 1: Add task with title and description ✓
  - TEST 2: Add task with title only ✓
  - TEST 3: Empty title validation ✓
- All manual tests passed successfully

**Test Results**:
```
62 passed in 8.29s (51 from Phase 2 + 11 new UI tests)
Coverage: 100.00% (72/72 statements)
- models.py: 100%
- storage.py: 100%
- ui.py: 100% (new)
```

**Module Size**: ui.py = 74 lines (well under 300-line limit) ✅

**User Story 1 Acceptance Criteria Verified**:
✓ New tasks created with status "incomplete" and unique ID
✓ Tasks display with title, description, status, and ID
✓ Empty/whitespace titles rejected with error message
✓ Description is optional (can be empty)

## Outcome

- ✅ Impact: Phase 3 complete - User Story 1 (Add Tasks) implemented, MVP core feature ready
- 🧪 Tests: 11 new tests passed + manual validation, 100% coverage maintained (72/72 statements)
- 📁 Files: Created ui.py (74 lines), test_ui.py (11 tests), manual_test_phase3.py, updated tasks.md
- 🔁 Next prompts: Proceed to Phase 4 (User Story 2 - View All Tasks) to complete MVP
- 🧠 Reflection: User Story 1 is first MVP feature; clean separation of input validation (get_non_empty_input) from business logic (add_task_ui); comprehensive test coverage ensures reliability; manual test validates end-to-end functionality

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All tests PASS (62/62), Coverage PASS (100% > 90%), Module size PASS (74 lines < 300), Manual test PASS (3/3 scenarios)
- Prompt variant (if applicable): Standard implementation workflow with automated and manual testing
- Next experiment (smallest change to try): Implement Phase 4 (View Tasks) to complete the read operation and enable full MVP (add + view)
