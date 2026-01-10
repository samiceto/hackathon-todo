# Tasks: Full-Stack Web Application

**Input**: Design documents from `/specs/002-step-2-web-app/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Tests are included as optional tasks - implement if following TDD approach or if test coverage is priority.

**Organization**: Tasks are grouped by user story (P1-P6 from spec.md) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **web application** with backend and frontend:
- **Backend**: `backend/api/src/`, `backend/api/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Step 1 console app**: `backend/console/` (PRESERVED - no changes)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure
**Duration**: Can complete in parallel
**Checkpoint**: Project structure ready, dependencies installable

- [x] T001 [P] Create backend/api directory structure per plan.md
- [x] T002 [P] Create frontend directory structure per plan.md
- [x] T003 [P] Initialize backend Python project with pyproject.toml in backend/api/
- [x] T004 [P] Initialize frontend Next.js project with package.json in frontend/
- [x] T005 [P] Create backend .env.example in backend/api/.env.example with required variables
- [x] T006 [P] Create frontend .env.local.example in frontend/.env.local.example with required variables
- [x] T007 [P] Create backend .gitignore in backend/api/.gitignore
- [x] T008 [P] Create frontend .gitignore in frontend/.gitignore
- [x] T009 [P] Configure Tailwind CSS in frontend/tailwind.config.js
- [x] T010 [P] Configure TypeScript in frontend/tsconfig.json
- [x] T011 [P] Initialize Alembic for database migrations in backend/api/alembic/

**Checkpoint**: ✅ Both projects have structure, configs, and can install dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T012 Create database configuration in backend/api/src/db/session.py
- [x] T013 Create environment settings loader in backend/api/src/config.py
- [x] T014 Create User SQLModel model in backend/api/src/models/user.py
- [x] T015 Create Task SQLModel model in backend/api/src/models/task.py
- [x] T016 Create Alembic migration for users and tasks tables in backend/api/alembic/versions/
- [x] T017 Create FastAPI main application in backend/api/src/main.py
- [x] T018 Configure CORS middleware in backend/api/src/main.py
- [x] T019 Create JWT verification dependency in backend/api/src/api/deps.py
- [x] T020 [P] Create global CSS styles in frontend/src/styles/globals.css
- [x] T021 [P] Create root layout component in frontend/src/app/layout.tsx
- [x] T022 [P] Create Better Auth configuration in frontend/src/lib/auth/auth-config.ts
- [x] T023 [P] Create Better Auth client in frontend/src/lib/auth/auth-client.ts
- [x] T024 [P] Create API client with JWT support in frontend/src/lib/api/client.ts

**Checkpoint**: ✅ Foundation ready - database models, auth system, and basic app structure in place. User story implementation can now begin.

---

## Phase 3: User Story 1 - User Account Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts, sign in, sign out, and maintain sessions

**Independent Test**: Create account → sign out → sign in → verify session persists → sign out

**Why MVP**: Authentication is required for all other features - this is the minimum viable product

### Implementation for User Story 1

- [x] T025 [P] [US1] Create signup request/response schemas in backend/api/src/schemas/auth.py
- [x] T026 [P] [US1] Create signin request/response schemas in backend/api/src/schemas/auth.py
- [x] T027 [US1] Create authentication service in backend/api/src/services/auth.py (password hashing, JWT creation)
- [x] T028 [US1] Create POST /api/auth/signup endpoint in backend/api/src/api/auth.py
- [x] T029 [US1] Create POST /api/auth/signin endpoint in backend/api/src/api/auth.py
- [x] T030 [P] [US1] Create signup page UI in frontend/src/app/signup/page.tsx
- [x] T031 [P] [US1] Create signin page UI in frontend/src/app/signin/page.tsx
- [x] T032 [P] [US1] Create SignupForm component in frontend/src/components/auth/SignupForm.tsx
- [x] T033 [P] [US1] Create SigninForm component in frontend/src/components/auth/SigninForm.tsx
- [x] T034 [P] [US1] Create form validation utilities in frontend/src/lib/utils/validators.ts
- [x] T035 [US1] Create auth service integration in frontend/src/lib/auth/auth-client.ts
- [x] T036 [US1] Add signout functionality to Better Auth client in frontend/src/lib/auth/auth-client.ts

**Checkpoint**: ✅ At this point, User Story 1 should be fully functional and testable independently. Users can signup, signin, and signout.

### Tests for User Story 1 (OPTIONAL - implement if following TDD) ⚠️

> **NOTE: These tests are optional. Implement if test coverage is a priority.**

- [ ] T037 [P] [US1] Create backend auth test fixtures in backend/api/tests/conftest.py
- [ ] T038 [P] [US1] Test POST /api/auth/signup success in backend/api/tests/test_auth.py
- [ ] T039 [P] [US1] Test POST /api/auth/signup duplicate email in backend/api/tests/test_auth.py
- [ ] T040 [P] [US1] Test POST /api/auth/signin success in backend/api/tests/test_auth.py
- [ ] T041 [P] [US1] Test POST /api/auth/signin invalid credentials in backend/api/tests/test_auth.py

---

## Phase 4: User Story 2 - View Task List (Priority: P2)

**Goal**: Display user's tasks in a responsive web interface with proper data isolation

**Independent Test**: Sign in → create test tasks (via API/seed) → verify list displays only user's tasks → test responsive layout → verify empty state

**Dependencies**: Requires US1 (authentication) to be complete

### Implementation for User Story 2

- [x] T042 [P] [US2] Create task response schema in backend/api/src/schemas/task.py
- [x] T043 [P] [US2] Create task list response schema in backend/api/src/schemas/task.py
- [x] T044 [US2] Create task service with get_all_tasks method in backend/api/src/services/tasks.py
- [x] T045 [US2] Create GET /api/{user_id}/tasks endpoint in backend/api/src/api/tasks.py
- [x] T046 [P] [US2] Create tasks page UI in frontend/src/app/tasks/page.tsx
- [x] T047 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx
- [x] T048 [P] [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [x] T049 [P] [US2] Create Loading component in frontend/src/components/ui/Loading.tsx
- [x] T050 [P] [US2] Create ErrorMessage component in frontend/src/components/ui/ErrorMessage.tsx
- [x] T051 [US2] Create task API methods in frontend/src/lib/api/tasks.ts (getTasks)
- [x] T052 [US2] Add empty state handling to TaskList in frontend/src/components/tasks/TaskList.tsx

**Checkpoint**: ✅ User Story 2 complete - users can view their tasks in a responsive interface with data isolation enforced

### Tests for User Story 2 (OPTIONAL) ⚠️

- [ ] T053 [P] [US2] Test GET /api/{user_id}/tasks returns only user's tasks in backend/api/tests/test_tasks.py
- [ ] T054 [P] [US2] Test GET /api/{user_id}/tasks data isolation in backend/api/tests/test_tasks.py
- [ ] T055 [P] [US2] Test GET /api/{user_id}/tasks empty list in backend/api/tests/test_tasks.py

---

## Phase 5: User Story 3 - Create New Tasks (Priority: P3)

**Goal**: Enable users to create new tasks via web form with validation

**Independent Test**: Sign in → click "Add Task" → fill form → submit → verify task appears in list → refresh page → verify persistence

**Dependencies**: Requires US1 (authentication) and US2 (view tasks) to be complete

### Implementation for User Story 3

- [x] T056 [P] [US3] Create task create request schema in backend/api/src/schemas/task.py
- [x] T057 [US3] Add create_task method to task service in backend/api/src/services/tasks.py
- [x] T058 [US3] Create POST /api/{user_id}/tasks endpoint in backend/api/src/api/tasks.py
- [x] T059 [P] [US3] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx
- [x] T060 [P] [US3] Create Input component in frontend/src/components/ui/Input.tsx
- [x] T061 [P] [US3] Create Button component in frontend/src/components/ui/Button.tsx
- [x] T062 [US3] Add createTask method to task API in frontend/src/lib/api/tasks.ts
- [x] T063 [US3] Integrate TaskForm into tasks page in frontend/src/app/tasks/page.tsx
- [x] T064 [US3] Add form validation for title (required, max 500 chars) in frontend/src/components/tasks/TaskForm.tsx

**Checkpoint**: ✅ User Story 3 complete - users can create new tasks with proper validation

### Tests for User Story 3 (OPTIONAL) ⚠️

- [ ] T065 [P] [US3] Test POST /api/{user_id}/tasks success in backend/api/tests/test_tasks.py
- [ ] T066 [P] [US3] Test POST /api/{user_id}/tasks empty title validation in backend/api/tests/test_tasks.py
- [ ] T067 [P] [US3] Test POST /api/{user_id}/tasks associates with correct user in backend/api/tests/test_tasks.py

---

## Phase 6: User Story 4 - Update Existing Tasks (Priority: P4)

**Goal**: Allow users to edit task details (title and description)

**Independent Test**: Sign in → select task → click edit → modify title/description → save → verify changes persist

**Dependencies**: Requires US1 (auth), US2 (view), and US3 (create) to be complete

### Implementation for User Story 4

- [x] T068 [P] [US4] Create task update request schema in backend/api/src/schemas/task.py
- [x] T069 [US4] Add update_task method to task service in backend/api/src/services/tasks.py
- [x] T070 [US4] Create PUT /api/{user_id}/tasks/{id} endpoint in backend/api/src/api/tasks.py
- [x] T071 [US4] Add edit mode state to TaskForm in frontend/src/components/tasks/TaskForm.tsx
- [x] T072 [US4] Add updateTask method to task API in frontend/src/lib/api/tasks.ts
- [x] T073 [US4] Add edit button and integration to TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [x] T074 [US4] Add cancel functionality to TaskForm in frontend/src/components/tasks/TaskForm.tsx

**Checkpoint**: ✅ User Story 4 complete - users can edit task details with proper validation

### Tests for User Story 4 (OPTIONAL) ⚠️

- [ ] T075 [P] [US4] Test PUT /api/{user_id}/tasks/{id} success in backend/api/tests/test_tasks.py
- [ ] T076 [P] [US4] Test PUT /api/{user_id}/tasks/{id} empty title validation in backend/api/tests/test_tasks.py
- [ ] T077 [P] [US4] Test PUT /api/{user_id}/tasks/{id} user ownership validation in backend/api/tests/test_tasks.py

---

## Phase 7: User Story 5 - Toggle Task Completion (Priority: P5)

**Goal**: Enable quick task completion status toggling with visual feedback

**Independent Test**: Sign in → click checkbox on incomplete task → verify visual change and persistence → click again → verify toggle back

**Dependencies**: Requires US1 (auth) and US2 (view) - independent of US3/US4

### Implementation for User Story 5

- [x] T078 [US5] Add toggle_completion method to task service in backend/api/src/services/tasks.py
- [x] T079 [US5] Create PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/api/src/api/tasks.py
- [x] T080 [US5] Add toggleComplete method to task API in frontend/src/lib/api/tasks.ts
- [x] T081 [US5] Add completion toggle UI to TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [x] T082 [US5] Add visual distinction for completed tasks in frontend/src/components/tasks/TaskItem.tsx (strikethrough/color)
- [x] T083 [US5] Add loading state during toggle in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: ✅ User Story 5 complete - users can toggle task completion with visual feedback

### Tests for User Story 5 (OPTIONAL) ⚠️

- [ ] T084 [P] [US5] Test PATCH /api/{user_id}/tasks/{id}/complete toggles status in backend/api/tests/test_tasks.py
- [ ] T085 [P] [US5] Test PATCH /api/{user_id}/tasks/{id}/complete persistence in backend/api/tests/test_tasks.py

---

## Phase 8: User Story 6 - Delete Tasks (Priority: P6)

**Goal**: Allow users to delete tasks with confirmation dialog

**Independent Test**: Sign in → select task → click delete → confirm in dialog → verify task removed and persists

**Dependencies**: Requires US1 (auth) and US2 (view) - independent of other stories

### Implementation for User Story 6

- [ ] T086 [US6] Add delete_task method to task service in backend/api/src/services/tasks.py
- [ ] T087 [US6] Create DELETE /api/{user_id}/tasks/{id} endpoint in backend/api/src/api/tasks.py
- [ ] T088 [US6] Add deleteTask method to task API in frontend/src/lib/api/tasks.ts
- [ ] T089 [P] [US6] Create DeleteConfirm component in frontend/src/components/tasks/DeleteConfirm.tsx
- [ ] T090 [US6] Add delete button and confirmation to TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [ ] T091 [US6] Add error handling for failed deletion in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: ✅ User Story 6 complete - users can delete tasks with confirmation

### Tests for User Story 6 (OPTIONAL) ⚠️

- [ ] T092 [P] [US6] Test DELETE /api/{user_id}/tasks/{id} success in backend/api/tests/test_tasks.py
- [ ] T093 [P] [US6] Test DELETE /api/{user_id}/tasks/{id} user ownership validation in backend/api/tests/test_tasks.py
- [ ] T094 [P] [US6] Test DELETE /api/{user_id}/tasks/{id} non-existent task in backend/api/tests/test_tasks.py

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final touches

- [ ] T095 [P] Create backend README.md in backend/api/README.md with setup instructions
- [ ] T096 [P] Create frontend README.md in frontend/README.md with setup instructions
- [ ] T097 [P] Update root README.md with Step 2 quickstart guide
- [ ] T098 [P] Create .env.example files with all required variables
- [ ] T099 [P] Add API documentation route in backend/api/src/main.py (Swagger UI)
- [ ] T100 Add error boundary to root layout in frontend/src/app/layout.tsx
- [ ] T101 Add loading states to all async operations in frontend components
- [ ] T102 Add success toast notifications in frontend/src/components/ui/Toast.tsx
- [ ] T103 Verify Step 1 console app still works in backend/console/
- [ ] T104 Run backend linting and formatting (ruff, black)
- [ ] T105 Run frontend linting and formatting (eslint, prettier)
- [ ] T106 Verify all environment variables documented in quickstart.md
- [ ] T107 Test end-to-end flow (signup → create task → edit → complete → delete → signout)

**Checkpoint**: ✅ All user stories complete, polished, and documented

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS all user stories
    ↓
┌───────────────────────────────────────────────┐
│  User Stories (can proceed in parallel        │
│  after Foundational phase is complete)        │
├───────────────────────────────────────────────┤
│  Phase 3: US1 (P1) - Auth (MVP - must do)    │
│      ↓                                         │
│  Phase 4: US2 (P2) - View (depends on US1)    │
│      ↓                                         │
│  Phase 5: US3 (P3) - Create (depends on US2)  │
│      ↓                                         │
│  Phase 6: US4 (P4) - Update (depends on US3)  │
│      ↓                                         │
│  Phase 7: US5 (P5) - Complete (depends on US2)│
│      ↓                                         │
│  Phase 8: US6 (P6) - Delete (depends on US2)  │
└───────────────────────────────────────────────┘
    ↓
Phase 9 (Polish)
```

### User Story Dependencies

- **US1 (Authentication)**: No dependencies - can start after Foundational phase ✅
- **US2 (View Tasks)**: Depends on US1 (must be authenticated to view)
- **US3 (Create Tasks)**: Depends on US1 + US2 (auth + need to see created tasks)
- **US4 (Update Tasks)**: Depends on US1 + US2 + US3 (need tasks to update)
- **US5 (Toggle Complete)**: Depends on US1 + US2 (auth + need to see tasks)
- **US6 (Delete Tasks)**: Depends on US1 + US2 (auth + need to see tasks)

### Parallel Opportunities

**Within Setup Phase (Phase 1)**:
```bash
# All these can run in parallel:
Task: "Create backend/api directory structure"
Task: "Create frontend directory structure"
Task: "Initialize backend Python project"
Task: "Initialize frontend Next.js project"
# ... (all T001-T011)
```

**Within Foundational Phase (Phase 2)**:
```bash
# Backend tasks (can run in parallel after T012-T013):
Task: "Create User model"
Task: "Create Task model"

# Frontend tasks (can run in parallel):
Task: "Create global CSS"
Task: "Create root layout"
Task: "Create Better Auth config"
Task: "Create API client"
# ... (T020-T024)
```

**Within User Story 1 (Phase 3)**:
```bash
# Backend schemas (parallel):
Task: "Create signup schemas"
Task: "Create signin schemas"

# Frontend pages (parallel):
Task: "Create signup page"
Task: "Create signin page"

# Frontend components (parallel):
Task: "Create SignupForm"
Task: "Create SigninForm"
Task: "Create form validators"
```

**After US1 is complete**, stories US5 and US6 can proceed in parallel with US3/US4 since they only depend on US1+US2:
```bash
# After US2 completes:
Task: "Implement US3 (Create)" → sequential with US4
Task: "Implement US5 (Toggle)" → can run in parallel with US3/US4
Task: "Implement US6 (Delete)" → can run in parallel with US3/US4
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

**Minimal Viable Product** - get to working demo fastest:

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T024)
3. Complete Phase 3: US1 - Authentication (T025-T036)
4. Complete Phase 4: US2 - View Tasks (T042-T052)
5. **STOP and VALIDATE**:
   - Users can signup, signin, signout
   - Users can view their tasks (seed some test data)
   - Data isolation works (create second user, verify separation)
6. Demo/deploy if ready ✅

**Total MVP Tasks**: 52 tasks (T001-T052, excluding optional tests)

### Incremental Delivery (Full Feature Set)

Add features one by one in priority order:

1. Complete Setup + Foundational → Foundation ready (T001-T024)
2. Add US1 (Auth) → Test independently → **MVP #1** (T025-T036)
3. Add US2 (View) → Test independently → **MVP #2** (T042-T052)
4. Add US3 (Create) → Test independently → **MVP #3** (T056-T064)
5. Add US4 (Update) → Test independently → **MVP #4** (T068-T074)
6. Add US5 (Complete) → Test independently → **MVP #5** (T078-T083)
7. Add US6 (Delete) → Test independently → **MVP #6** (T086-T091)
8. Polish → Final release (T095-T107)

Each increment is deployable and adds value without breaking previous features.

### Parallel Team Strategy

With multiple developers (or efficient AI implementation):

1. **Team completes Setup + Foundational together** (T001-T024)
2. **Once Foundational is done**:
   - Developer A: US1 (Auth) - T025-T036 (MUST complete first)
   - Wait for US1...
3. **After US1 completes**:
   - Developer A: US2 (View) - T042-T052
   - Wait for US2...
4. **After US2 completes** (parallel work begins):
   - Developer A: US3 (Create) - T056-T064
   - Developer B: US5 (Toggle) - T078-T083 (in parallel!)
   - Developer C: US6 (Delete) - T086-T091 (in parallel!)
5. **After US3 completes**:
   - Developer A: US4 (Update) - T068-T074
6. **Polish together** (T095-T107)

---

## Task Summary

**Total Tasks**: 107 tasks
- **Setup**: 11 tasks (T001-T011)
- **Foundational**: 13 tasks (T012-T024)
- **US1 (Auth)**: 12 implementation + 5 tests = 17 tasks (T025-T041)
- **US2 (View)**: 11 implementation + 3 tests = 14 tasks (T042-T055)
- **US3 (Create)**: 9 implementation + 3 tests = 12 tasks (T056-T067)
- **US4 (Update)**: 7 implementation + 3 tests = 10 tasks (T068-T077)
- **US5 (Toggle)**: 6 implementation + 2 tests = 8 tasks (T078-T085)
- **US6 (Delete)**: 6 implementation + 3 tests = 9 tasks (T086-T094)
- **Polish**: 13 tasks (T095-T107)

**Implementation Tasks Only** (excluding optional tests): **85 tasks**

**MVP Tasks** (Setup + Foundational + US1 + US2, no tests): **52 tasks**

### Independent Test Criteria

Each user story has a clear independent test:

- **US1**: Create account → signout → signin → verify session → signout ✅
- **US2**: Signin → verify task list displays → check data isolation → test responsive ✅
- **US3**: Signin → create task → verify in list → refresh → verify persistence ✅
- **US4**: Signin → edit task → save → refresh → verify changes persist ✅
- **US5**: Signin → toggle task → verify visual change → refresh → verify persistence ✅
- **US6**: Signin → delete task → confirm → verify removal → refresh → verify gone ✅

### Parallel Task Count

- **Phase 1**: 11 tasks can run in parallel
- **Phase 2**: 8 tasks can run in parallel (after T012-T013)
- **Within each US**: 3-5 tasks can run in parallel (schemas, components, pages)
- **After US2**: US5 and US6 can run in parallel with US3/US4

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] label**: Maps task to specific user story for traceability
- **File paths**: Every task includes exact file path for implementation
- **Tests optional**: Marked with ⚠️ - implement if TDD or coverage is priority
- **Checkpoints**: After each phase to validate story independently
- **MVP**: Stop after US1+US2 for fastest demo (52 tasks)
- **Incremental**: Add one story at a time for continuous delivery
- **Parallel**: US5 and US6 can run alongside US3/US4 after US2

**Avoid**:
- Starting US2-US6 before US1 (auth) is complete
- Starting any US before Foundational phase is complete
- Modifying Step 1 console app (backend/console/ is preserved)
- Hardcoding secrets (use .env files)
