# API Endpoint Contracts

**Feature**: 002-step-2-web-app
**Date**: 2026-01-08
**Base URL**: `http://localhost:8000` (development)

## Overview

All API endpoints use JSON for request/response bodies. Authentication endpoints are public; task endpoints require JWT authentication.

**Authentication**: JWT token in `Authorization: Bearer <token>` header (except auth endpoints)

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Request Schema**:
```typescript
interface SignupRequest {
  email: string;        // Valid email format
  password: string;     // Min 8 characters
}
```

**Success Response** (201 Created):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-01-08T12:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:

```json
// 400 Bad Request - Invalid email format
{
  "detail": "Invalid email address"
}

// 400 Bad Request - Password too short
{
  "detail": "Password must be at least 8 characters"
}

// 409 Conflict - Email already exists
{
  "detail": "Email already registered"
}

// 422 Unprocessable Entity - Missing fields
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### POST /api/auth/signin

Sign in with existing account.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Request Schema**:
```typescript
interface SigninRequest {
  email: string;
  password: string;
}
```

**Success Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:

```json
// 401 Unauthorized - Invalid credentials
{
  "detail": "Invalid email or password"
}

// 422 Unprocessable Entity - Missing fields
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Task Endpoints

**All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.**

### GET /api/{user_id}/tasks

List all tasks for the authenticated user.

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer): Must match authenticated user's ID from JWT

**Query Parameters**: None

**Request Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Complete Step 2",
      "description": "Build full-stack web app",
      "completed": false,
      "created_at": "2026-01-08T12:00:00Z",
      "updated_at": "2026-01-08T12:00:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "title": "Write documentation",
      "description": "",
      "completed": true,
      "created_at": "2026-01-08T13:00:00Z",
      "updated_at": "2026-01-08T14:00:00Z"
    }
  ],
  "total": 2
}
```

**Error Responses**:

```json
// 401 Unauthorized - No token provided
{
  "detail": "Not authenticated"
}

// 401 Unauthorized - Invalid token
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden - user_id mismatch
{
  "detail": "Not authorized to access this user's tasks"
}
```

---

### POST /api/{user_id}/tasks

Create a new task for the authenticated user.

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer): Must match authenticated user's ID

**Request Body**:
```json
{
  "title": "New task title",
  "description": "Optional task description"
}
```

**Request Schema**:
```typescript
interface CreateTaskRequest {
  title: string;          // Required, min 1 char, max 500 chars
  description?: string;   // Optional, max 5000 chars, defaults to ""
}
```

**Success Response** (201 Created):
```json
{
  "id": 3,
  "user_id": 1,
  "title": "New task title",
  "description": "Optional task description",
  "completed": false,
  "created_at": "2026-01-08T15:00:00Z",
  "updated_at": "2026-01-08T15:00:00Z"
}
```

**Error Responses**:

```json
// 400 Bad Request - Empty title
{
  "detail": "Title cannot be empty"
}

// 400 Bad Request - Title too long
{
  "detail": "Title cannot exceed 500 characters"
}

// 401 Unauthorized - No token
{
  "detail": "Not authenticated"
}

// 403 Forbidden - user_id mismatch
{
  "detail": "Not authorized to create tasks for this user"
}
```

---

### GET /api/{user_id}/tasks/{id}

Get a single task by ID.

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer): Must match authenticated user's ID
- `id` (integer): Task ID

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete Step 2",
  "description": "Build full-stack web app",
  "completed": false,
  "created_at": "2026-01-08T12:00:00Z",
  "updated_at": "2026-01-08T12:00:00Z"
}
```

**Error Responses**:

```json
// 404 Not Found - Task doesn't exist or belongs to another user
{
  "detail": "Task not found"
}

// 401 Unauthorized - No token
{
  "detail": "Not authenticated"
}

// 403 Forbidden - user_id mismatch
{
  "detail": "Not authorized to access this user's tasks"
}
```

---

### PUT /api/{user_id}/tasks/{id}

Update an existing task.

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer): Must match authenticated user's ID
- `id` (integer): Task ID

**Request Body**:
```json
{
  "title": "Updated title",
  "description": "Updated description"
}
```

**Request Schema**:
```typescript
interface UpdateTaskRequest {
  title: string;          // Required, min 1 char, max 500 chars
  description?: string;   // Optional, max 5000 chars
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "completed": false,
  "created_at": "2026-01-08T12:00:00Z",
  "updated_at": "2026-01-08T16:00:00Z"
}
```

**Error Responses**:

```json
// 404 Not Found - Task doesn't exist
{
  "detail": "Task not found"
}

// 400 Bad Request - Empty title
{
  "detail": "Title cannot be empty"
}

// 401 Unauthorized - No token
{
  "detail": "Not authenticated"
}

// 403 Forbidden - user_id mismatch
{
  "detail": "Not authorized to update this task"
}
```

---

### DELETE /api/{user_id}/tasks/{id}

Delete a task.

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer): Must match authenticated user's ID
- `id` (integer): Task ID

**Request Body**: None

**Success Response** (204 No Content):
```
(Empty response body)
```

**Error Responses**:

```json
// 404 Not Found - Task doesn't exist
{
  "detail": "Task not found"
}

// 401 Unauthorized - No token
{
  "detail": "Not authenticated"
}

// 403 Forbidden - user_id mismatch
{
  "detail": "Not authorized to delete this task"
}
```

---

### PATCH /api/{user_id}/tasks/{id}/complete

Toggle task completion status.

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer): Must match authenticated user's ID
- `id` (integer): Task ID

**Request Body**: None (toggles current status)

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete Step 2",
  "description": "Build full-stack web app",
  "completed": true,          // Toggled from false to true
  "created_at": "2026-01-08T12:00:00Z",
  "updated_at": "2026-01-08T17:00:00Z"
}
```

**Error Responses**:

```json
// 404 Not Found - Task doesn't exist
{
  "detail": "Task not found"
}

// 401 Unauthorized - No token
{
  "detail": "Not authenticated"
}

// 403 Forbidden - user_id mismatch
{
  "detail": "Not authorized to update this task"
}
```

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH requests |
| 201 | Created | Successful POST requests |
| 204 | No Content | Successful DELETE requests |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (duplicate email) |
| 422 | Unprocessable Entity | Validation errors from Pydantic |
| 500 | Internal Server Error | Server-side error |

---

## Common Headers

### Request Headers

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Response Headers

```
Content-Type: application/json
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (422), FastAPI returns:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

---

## Rate Limiting

**Not implemented in Step 2** (reserved for future enhancements).

---

## CORS Configuration

**Allowed Origins**:
- Development: `http://localhost:3000`
- Production: TBD (will be configured in .env)

**Allowed Methods**: All (GET, POST, PUT, PATCH, DELETE, OPTIONS)
**Allowed Headers**: All
**Allow Credentials**: Yes (for JWT cookies)

---

## Example API Call (JavaScript)

```javascript
// Fetch user's tasks
const response = await fetch('http://localhost:8000/api/1/tasks', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log(data.tasks);
```

---

## Security Notes

1. **JWT Validation**: All task endpoints validate JWT and extract user_id
2. **user_id Verification**: Path parameter `user_id` must match JWT's `sub` claim
3. **Data Isolation**: Queries always filter by `user_id` from JWT
4. **Password Security**: Passwords are never returned in responses
5. **HTTPS**: Required in production (HTTP acceptable in development)

---

## Testing

Use the following tools to test API endpoints:

- **Postman**: Import OpenAPI spec (can be generated from FastAPI)
- **curl**: Command-line testing
- **httpx**: Python test client (pytest)
- **Playwright**: End-to-end testing

Example curl request:

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```
