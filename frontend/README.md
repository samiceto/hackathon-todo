# Hackathon Todo - Frontend

Next.js frontend for the Hackathon Todo full-stack web application (Step 2).

## Technology Stack

- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript 5+
- **UI Library**: React 18+
- **Styling**: Tailwind CSS 3+
- **Authentication**: Better Auth
- **API Client**: axios
- **Testing**: Jest, React Testing Library, Playwright

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Landing page
│   │   ├── signup/       # Signup page
│   │   ├── signin/       # Signin page
│   │   └── tasks/        # Task management page
│   ├── components/       # React components
│   │   ├── auth/         # Authentication forms
│   │   ├── tasks/        # Task components
│   │   └── ui/           # Reusable UI components
│   ├── lib/              # Utilities and services
│   │   ├── auth/         # Better Auth configuration
│   │   ├── api/          # API client and methods
│   │   └── utils/        # Helper functions
│   └── styles/           # Global CSS and Tailwind
├── public/               # Static assets
├── tests/                # Test suites
├── .env.local.example    # Example environment variables
├── package.json          # Node dependencies
└── tailwind.config.js    # Tailwind configuration
```

## Setup

### Prerequisites

- Node.js 20+
- npm 10+ (or pnpm)
- Backend API running on port 8000

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Copy environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```

3. **Edit `.env.local` and add your credentials**:
   - `BETTER_AUTH_SECRET`: 32+ character secret (must match backend)
   - `BETTER_AUTH_URL`: `http://localhost:3000` for development
   - `DATABASE_URL`: Your Neon PostgreSQL connection string (same as backend)
   - `NEXT_PUBLIC_API_URL`: `http://localhost:8000` (backend API URL)

4. **Install dependencies**:
   ```bash
   npm install
   # or
   pnpm install
   ```

5. **Start the development server**:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```

   Application will be available at: http://localhost:3000

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm test` - Run Jest unit tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:e2e` - Run Playwright E2E tests
- `npm run test:e2e:ui` - Run E2E tests with UI

## Pages

### Public Pages
- `/` - Landing page with links to signup/signin
- `/signup` - User registration page
- `/signin` - User login page

### Protected Pages (Require Authentication)
- `/tasks` - Task management interface (view, create, update, delete tasks)

## Features

### Authentication
- User signup with email and password
- User signin with session management
- JWT token stored in httpOnly cookies
- Automatic redirect to `/signin` if not authenticated
- Sign out functionality

### Task Management
- View all user's tasks in a responsive list
- Create new tasks with title and description
- Update existing task details
- Mark tasks as complete/incomplete
- Delete tasks with confirmation dialog
- Empty state when no tasks exist

### UI/UX
- Responsive design (mobile-first approach)
- Loading states during API calls
- Error messages with user-friendly text
- Form validation with helpful feedback
- Success messages for completed actions

## Development

The frontend uses:
- **Next.js App Router** for file-based routing and layouts
- **Better Auth** for authentication with JWT tokens
- **Tailwind CSS** for utility-first styling
- **TypeScript** for type safety
- **Axios** for API calls with JWT header injection

All API requests automatically include the JWT token from Better Auth in the `Authorization: Bearer <token>` header.

## Testing

### Unit Tests (Jest + React Testing Library)

```bash
npm test
```

Test files are located in `tests/unit/` and use the `*.test.tsx` naming convention.

### End-to-End Tests (Playwright)

```bash
npm run test:e2e
```

E2E test files are located in `tests/e2e/` and use the `*.spec.ts` naming convention.

## Environment Variables

### Required Variables

- `BETTER_AUTH_SECRET` - Shared secret for JWT (32+ chars, must match backend)
- `BETTER_AUTH_URL` - Frontend URL (e.g., `http://localhost:3000`)
- `DATABASE_URL` - Neon PostgreSQL connection string (for Better Auth)
- `NEXT_PUBLIC_API_URL` - Backend API URL (e.g., `http://localhost:8000`)

**Security Note**: Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Never put secrets in `NEXT_PUBLIC_*` variables.

## Styling

Tailwind CSS is configured with:
- Custom color palette (primary, success, error)
- Responsive breakpoints
- Custom font family support
- Utility classes for rapid development

Global styles are in `src/styles/globals.css`.

## Related Documentation

- [Frontend Specification](../specs/002-step-2-web-app/spec.md)
- [API Endpoint Contracts](../specs/002-step-2-web-app/contracts/api-endpoints.md)
- [Authentication Flow](../specs/002-step-2-web-app/contracts/auth-flow.md)
- [Quickstart Guide](../specs/002-step-2-web-app/design/quickstart.md)
