# UI Specifications

This directory contains user interface component and page specifications for the frontend application.

## Organization

UI specs define:
- Component structure and props
- User interaction flows
- Accessibility requirements
- Responsive design breakpoints
- Visual design guidelines

## Planned Specifications

### Step 2: Core UI Components
- **components.md** - TaskList, TaskCard, TaskForm components (planned)
- **pages.md** - Dashboard, Login, Signup pages (planned)
- **theme.md** - Color palette, typography, spacing (planned)

### Step 3+: Advanced UI
- **chatbot-ui.md** - AI chatbot interface (planned)

## Current Status

**Not yet implemented** - Specifications will be created when developing the Next.js frontend in Step 2.

## Current UI (Step 1)

The console app uses terminal-based UI:
- **Location**: `backend/console/src/hackathon_todo/ui.py`
- **Pattern**: Menu-driven interface with text prompts
- **Features**: Input validation, error messages, status indicators (○/✓)

## Migration Path

**Console UI → Web UI**:
```
Console Pattern                →  Web Component
---------------                   -------------
display_menu()                 →  Navigation bar
view_tasks_ui()               →  TaskList component
add_task_ui()                 →  TaskForm modal/page
Input prompts                  →  Form fields with validation
Status indicators (○/✓)       →  Checkboxes/toggles
Error messages                 →  Toast notifications
```

## UI Design Principles

When creating UI specs, follow these guidelines:
- **Accessibility**: WCAG 2.1 AA compliance
- **Responsive**: Mobile-first design (breakpoints: 640px, 768px, 1024px, 1280px)
- **Performance**: Optimize for Core Web Vitals (LCP, FID, CLS)
- **Consistency**: Reusable component library (shadcn/ui)
- **User Experience**: Clear feedback, intuitive interactions
- **Design System**: Tailwind CSS utility classes, consistent spacing/colors
