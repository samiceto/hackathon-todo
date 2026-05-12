---
name: UI/UX Pro Max Teal Redesign
description: Applied ui-ux-pro-max design system to redesign all frontend pages with teal palette, Plus Jakarta Sans, and orange CTA
type: green
stage: green
date: 2026-05-02
surface: agent
model: claude-sonnet-4-6
feature: 005-step-5-cloud-deployment
branch: 005-step-5-cloud-deployment
user: Sami Ullah
command: /ui-ux-pro-max skill applied to entire frontend
labels: ["ui", "design-system", "teal", "typography", "micro-interactions"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_modified:
  - frontend/tailwind.config.js
  - frontend/src/app/layout.tsx
  - frontend/src/styles/globals.css
  - frontend/src/app/page.tsx
  - frontend/src/app/signin/page.tsx
  - frontend/src/app/signup/page.tsx
  - frontend/src/app/tasks/page.tsx
  - frontend/src/components/auth/SigninForm.tsx
  - frontend/src/components/auth/SignupForm.tsx
  - frontend/src/components/chat/FloatingChat.tsx
  - frontend/src/components/chat/ChatInterface.tsx
  - frontend/src/components/chat/ChatMessage.tsx
  - frontend/src/components/chat/MessageInput.tsx
  - frontend/src/components/chat/MessageList.tsx
  - frontend/src/components/tasks/TaskItem.tsx
  - frontend/src/components/tasks/TaskList.tsx
  - frontend/src/components/tasks/FilterPanel.tsx
  - frontend/src/components/tasks/TaskForm.tsx
  - frontend/src/components/tasks/PrioritySelector.tsx
  - frontend/src/components/tasks/TagInput.tsx
  - frontend/src/components/tasks/DueDatePicker.tsx
  - frontend/src/components/tasks/RecurrenceInput.tsx
  - frontend/src/components/tasks/SearchBar.tsx
  - frontend/src/components/tasks/SortControls.tsx
  - frontend/src/components/tasks/Pagination.tsx
  - frontend/src/components/ui/Loading.tsx
  - frontend/src/components/ui/Toast.tsx
  - frontend/src/components/ui/ErrorMessage.tsx
  - frontend/src/app/error.tsx
  - frontend/src/app/global-error.tsx
tests: []
---

## Prompt

"use your ui ux pro max skill and decorate the frontend of project"

## Response

Applied the ui-ux-pro-max design system with the following changes:

**Design System Selected:**
- Style: Micro-interactions (SaaS productivity tool)
- Primary: Teal #0D9488 (teal-600) — replaced all blue-600 references
- CTA: Orange #F97316 (orange-500) — used on landing/auth submit buttons
- Background: teal-50 (#F0FDFA)
- Typography: Plus Jakarta Sans (replaced Inter)

**Key Changes:**
1. `globals.css` — Updated all CSS HSL variables to teal palette; added `prefers-reduced-motion` media query; teal scrollbars and focus rings
2. `layout.tsx` — Switched from Inter to Plus Jakarta Sans (300–800 weights)
3. `tailwind.config.js` — Updated fontFamily to `--font-jakarta`
4. `app/page.tsx` — Gradient teal hero with dot grid, teal feature pills, orange CTA button
5. `signin/page.tsx` + `signup/page.tsx` — Teal-900→700 gradient left panel with dot grid texture
6. Auth forms — Teal focus rings (`hover:border-teal-300 focus:border-teal-500`), orange submit buttons
7. `tasks/page.tsx` — Teal sidebar borders, teal active nav, teal header border
8. `TaskItem.tsx` — Teal checkbox (checked state), teal medium priority badge, teal tag input, hover lift
9. `TaskList.tsx` — Teal filter tabs with `bg-teal-50` pill container, teal empty state icon
10. `FilterPanel.tsx` — Removed emoji priority icons (replaced with text), teal active badge, teal focus styles
11. `FloatingChat.tsx` — Teal FAB with hover scale effect
12. All 20+ remaining components — Systematic blue→teal replacement via Python script

**TypeScript check:** Passed (exit code 0)
