# Frontend Development Context

## Overview

This directory will contain the Next.js frontend application for Hackathon Todo.

**Current Status**: Placeholder - Not yet implemented 📋

**Planned for**: Step 2+ (Full-Stack Web Application)

---

## Planned Technology Stack

### Core Framework
- **Next.js 16+** (App Router)
- **React 19+**
- **TypeScript 5+**

### Styling & UI
- **Tailwind CSS 4+**
- **shadcn/ui** components
- **Radix UI** primitives

### Authentication
- **Better Auth** (JWT-based)
- OAuth providers (Google, GitHub)

### State Management
- **React Server Components** (default)
- **React hooks** (useState, useReducer)
- **TanStack Query** (API data fetching)

### API Integration
- **Fetch API** / **Axios**
- Backend: FastAPI (http://localhost:8000)

---

## Planned Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Authentication routes
│   │   ├── login/
│   │   └── signup/
│   ├── (dashboard)/         # Protected dashboard routes
│   │   ├── page.tsx         # Main dashboard
│   │   └── layout.tsx       # Dashboard layout
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
├── components/               # Reusable React components
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── TaskList.tsx         # Task list component
│   ├── TaskCard.tsx         # Individual task card
│   ├── TaskForm.tsx         # Add/edit task form
│   └── Header.tsx           # App header
├── lib/                      # Utilities and configurations
│   ├── api.ts               # Backend API client
│   ├── auth.ts              # Better Auth configuration
│   └── utils.ts             # Helper functions
├── hooks/                    # Custom React hooks
│   ├── useTasks.ts          # Task management hook
│   └── useAuth.ts           # Authentication hook
├── types/                    # TypeScript types
│   └── task.ts              # Task interface
├── public/                   # Static assets
├── .env.local               # Environment variables
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Node.js dependencies
```

---

## Planned Features

### Authentication Pages
- **Login**: Email/password and OAuth
- **Signup**: User registration
- **Logout**: Session termination

### Dashboard (Protected)
- **Task List View**: Display all tasks
- **Task Creation**: Add new tasks
- **Task Editing**: Update existing tasks
- **Task Deletion**: Remove tasks
- **Task Completion**: Toggle task status
- **Real-time Updates**: Optimistic UI updates

### UI Components
- **TaskList**: Displays tasks with filters (all, active, completed)
- **TaskCard**: Individual task with actions (edit, delete, toggle)
- **TaskForm**: Modal or inline form for creating/editing
- **Header**: Navigation, user profile, logout

---

## Planned API Integration

### API Client (`lib/api.ts`)

```typescript
// Backend API base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Task API endpoints
export const taskApi = {
  // Get all tasks for user
  getTasks: async (userId: string, token: string) => {
    const res = await fetch(`${API_BASE}/api/${userId}/tasks`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.json();
  },

  // Create new task
  createTask: async (userId: string, task: CreateTaskDto, token: string) => {
    const res = await fetch(`${API_BASE}/api/${userId}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(task)
    });
    return res.json();
  },

  // Update task
  updateTask: async (userId: string, taskId: number, task: UpdateTaskDto, token: string) => {
    const res = await fetch(`${API_BASE}/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(task)
    });
    return res.json();
  },

  // Delete task
  deleteTask: async (userId: string, taskId: number, token: string) => {
    const res = await fetch(`${API_BASE}/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.json();
  },

  // Toggle task completion
  toggleComplete: async (userId: string, taskId: number, token: string) => {
    const res = await fetch(`${API_BASE}/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.json();
  }
};
```

### TypeScript Types (`types/task.ts`)

```typescript
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskDto {
  title: string;
  description?: string;
}

export interface UpdateTaskDto {
  title?: string;
  description?: string;
}
```

---

## Planned Development Workflow

### Setup (When Ready)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your API URL and Better Auth secret

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Development Commands

```bash
# Run dev server (hot reload)
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build

# Run tests (future)
npm test
```

---

## Design Guidelines

### UI/UX Principles
- **Responsive**: Mobile-first design
- **Accessible**: WCAG 2.1 AA compliance
- **Fast**: Optimistic UI updates, server components
- **Clean**: Minimal, modern interface
- **Intuitive**: Clear actions, helpful feedback

### Component Design
- **Atomic Design**: Atoms → Molecules → Organisms → Templates → Pages
- **Reusability**: DRY principle for components
- **Composition**: Prefer composition over inheritance
- **Type Safety**: Full TypeScript coverage

### Performance Targets
- **FCP**: < 1.5s (First Contentful Paint)
- **LCP**: < 2.5s (Largest Contentful Paint)
- **TTI**: < 3.5s (Time to Interactive)
- **CLS**: < 0.1 (Cumulative Layout Shift)

---

## Integration with Backend

### Authentication Flow

1. User logs in via Better Auth
2. Backend issues JWT token
3. Frontend stores token (httpOnly cookie)
4. All API requests include token in Authorization header
5. Backend validates token and returns user-specific data

### Error Handling

```typescript
try {
  const tasks = await taskApi.getTasks(userId, token);
  setTasks(tasks);
} catch (error) {
  if (error.response?.status === 401) {
    // Token expired, redirect to login
    router.push('/login');
  } else {
    // Show error toast
    toast.error('Failed to fetch tasks');
  }
}
```

---

## Testing Strategy (Planned)

### Unit Tests
- Component rendering
- User interactions
- State management

### Integration Tests
- API client functions
- Authentication flows
- CRUD operations

### E2E Tests (Playwright)
- Complete user workflows
- Cross-browser testing

**Coverage Target**: >80%

---

## Migration from Console App

The console app UI will inform the web UI design:

**Console UI Patterns → Web UI**:
- Menu-driven interface → Navigation bar
- Task list display → Task cards/table
- Input prompts → Forms with validation
- Status indicators (○/✓) → Checkboxes/toggles
- Error messages → Toast notifications

**Preserving UX Quality**:
- Console: Retry loops → Web: Inline validation
- Console: Clear prompts → Web: Placeholder text
- Console: Graceful errors → Web: User-friendly error states

---

## Quick Reference (When Implemented)

### Development Server
- URL: http://localhost:3000
- API: http://localhost:8000

### Key Directories
- **app/**: Next.js routes (App Router)
- **components/**: Reusable React components
- **lib/**: Utilities, API client, configurations
- **types/**: TypeScript interfaces

### Documentation
- Next.js: https://nextjs.org/docs
- shadcn/ui: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com/docs
- Better Auth: https://www.better-auth.com/docs

---

**Last Updated**: 2026-01-05 (Monorepo restructuring - Phase 1)

**Status**: Placeholder file - Frontend implementation planned for Step 2+
