# Authentication Flow

**Feature**: 002-step-2-web-app
**Date**: 2026-01-08
**Authentication Strategy**: JWT (JSON Web Tokens) issued by Better Auth

## Overview

The application uses a hybrid authentication approach:
- **Frontend**: Better Auth manages user sessions and issues JWT tokens
- **Backend**: FastAPI validates JWT tokens for API access

**Token Storage**: httpOnly cookies (recommended) or localStorage
**Token Lifetime**: 7 days
**Token Refresh**: Not implemented in Step 2 (future enhancement)

---

## Flow 1: User Signup

### Step-by-Step Process

```
┌─────────┐                    ┌─────────────┐                   ┌──────────┐
│ Browser │                    │  Next.js    │                   │ FastAPI  │
│         │                    │  Frontend   │                   │ Backend  │
└─────────┘                    └─────────────┘                   └──────────┘
     │                                │                                │
     │  1. Navigate to /signup        │                                │
     ├───────────────────────────────>│                                │
     │                                │                                │
     │  2. Render signup form         │                                │
     │<───────────────────────────────┤                                │
     │                                │                                │
     │  3. Submit email + password    │                                │
     ├───────────────────────────────>│                                │
     │                                │                                │
     │                                │  4. POST /api/auth/signup      │
     │                                ├───────────────────────────────>│
     │                                │                                │
     │                                │  5. Validate email format      │
     │                                │                                │
     │                                │  6. Check email uniqueness     │
     │                                │                                │
     │                                │  7. Hash password (bcrypt)     │
     │                                │                                │
     │                                │  8. Create user in database    │
     │                                │                                │
     │                                │  9. Generate JWT token         │
     │                                │     (sub: user_id, exp: 7d)    │
     │                                │                                │
     │                                │  10. Return user + token       │
     │                                │<───────────────────────────────┤
     │                                │  {user: {...}, token: "..."}   │
     │                                │                                │
     │  11. Store token in cookie     │                                │
     │      (httpOnly, secure)        │                                │
     │                                │                                │
     │  12. Redirect to /tasks        │                                │
     │<───────────────────────────────┤                                │
     │                                │                                │
```

### Request/Response Details

**Request** (from frontend to backend):
```http
POST /api/auth/signup HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response** (from backend to frontend):
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-01-08T12:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM2NDI0MDAwfQ.signature"
}
```

**JWT Token Payload** (decoded):
```json
{
  "sub": "1",                      // User ID (subject)
  "email": "user@example.com",     // User email
  "exp": 1736424000,               // Expiration (7 days from issue)
  "iat": 1736337600                // Issued at timestamp
}
```

---

## Flow 2: User Signin

### Step-by-Step Process

```
┌─────────┐                    ┌─────────────┐                   ┌──────────┐
│ Browser │                    │  Next.js    │                   │ FastAPI  │
│         │                    │  Frontend   │                   │ Backend  │
└─────────┘                    └─────────────┘                   └──────────┘
     │                                │                                │
     │  1. Navigate to /signin        │                                │
     ├───────────────────────────────>│                                │
     │                                │                                │
     │  2. Render signin form         │                                │
     │<───────────────────────────────┤                                │
     │                                │                                │
     │  3. Submit email + password    │                                │
     ├───────────────────────────────>│                                │
     │                                │                                │
     │                                │  4. POST /api/auth/signin      │
     │                                ├───────────────────────────────>│
     │                                │                                │
     │                                │  5. Find user by email         │
     │                                │                                │
     │                                │  6. Verify password (bcrypt)   │
     │                                │                                │
     │                                │  7. Generate JWT token         │
     │                                │     (sub: user_id, exp: 7d)    │
     │                                │                                │
     │                                │  8. Return user + token        │
     │                                │<───────────────────────────────┤
     │                                │  {user: {...}, token: "..."}   │
     │                                │                                │
     │  9. Store token in cookie      │                                │
     │     (httpOnly, secure)         │                                │
     │                                │                                │
     │  10. Redirect to /tasks        │                                │
     │<───────────────────────────────┤                                │
     │                                │                                │
```

### Error Cases

**Invalid Credentials**:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Invalid email or password"
}
```

**User Not Found**:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Invalid email or password"
}
```

*Note*: Same error message for both cases (security best practice - don't leak whether email exists)

---

## Flow 3: Authenticated API Request

### Step-by-Step Process

```
┌─────────┐                    ┌─────────────┐                   ┌──────────┐
│ Browser │                    │  Next.js    │                   │ FastAPI  │
│         │                    │  Frontend   │                   │ Backend  │
└─────────┘                    └─────────────┘                   └──────────┘
     │                                │                                │
     │  1. Click "View Tasks"         │                                │
     ├───────────────────────────────>│                                │
     │                                │                                │
     │  2. Read JWT from cookie       │                                │
     │                                │                                │
     │                                │  3. GET /api/1/tasks           │
     │                                │     Authorization: Bearer JWT  │
     │                                ├───────────────────────────────>│
     │                                │                                │
     │                                │  4. Extract JWT from header    │
     │                                │                                │
     │                                │  5. Verify JWT signature       │
     │                                │     (using BETTER_AUTH_SECRET) │
     │                                │                                │
     │                                │  6. Decode JWT payload         │
     │                                │     {sub: "1", email: "..."}   │
     │                                │                                │
     │                                │  7. Validate user_id match     │
     │                                │     (URL /api/1/ vs JWT sub:1) │
     │                                │                                │
     │                                │  8. Query tasks WHERE user_id=1│
     │                                │                                │
     │                                │  9. Return tasks               │
     │                                │<───────────────────────────────┤
     │                                │  {tasks: [...], total: 5}      │
     │                                │                                │
     │  10. Display tasks in UI       │                                │
     │<───────────────────────────────┤                                │
     │                                │                                │
```

### Request Headers

```http
GET /api/1/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### JWT Verification Logic (Backend)

```python
from jose import jwt, JWTError
from fastapi import HTTPException, status

def verify_jwt(token: str) -> dict:
    try:
        # Decode and verify signature
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"user_id": int(user_id), "email": payload.get("email")}

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

---

## Flow 4: User Signout

### Step-by-Step Process

```
┌─────────┐                    ┌─────────────┐
│ Browser │                    │  Next.js    │
│         │                    │  Frontend   │
└─────────┘                    └─────────────┘
     │                                │
     │  1. Click "Sign Out"           │
     ├───────────────────────────────>│
     │                                │
     │  2. Delete JWT cookie          │
     │     document.cookie = "...";   │
     │                                │
     │  3. Redirect to /signin        │
     │<───────────────────────────────┤
     │                                │
```

**Note**: JWT signout is client-side only. The token remains valid until expiration, but the client forgets it. For immediate revocation, implement token blacklist (not in Step 2 scope).

---

## Flow 5: Expired Token

### Step-by-Step Process

```
┌─────────┐                    ┌─────────────┐                   ┌──────────┐
│ Browser │                    │  Next.js    │                   │ FastAPI  │
└─────────┘                    └─────────────┘                   └──────────┘
     │                                │                                │
     │  1. Make API request           │                                │
     ├───────────────────────────────>│                                │
     │                                │                                │
     │                                │  2. GET /api/1/tasks           │
     │                                │     Authorization: Bearer JWT  │
     │                                ├───────────────────────────────>│
     │                                │                                │
     │                                │  3. Verify JWT signature       │
     │                                │                                │
     │                                │  4. Check expiration (exp)     │
     │                                │     Current time > exp ❌      │
     │                                │                                │
     │                                │  5. Return 401 Unauthorized    │
     │                                │<───────────────────────────────┤
     │                                │  {detail: "Token expired"}     │
     │                                │                                │
     │  6. Handle 401 error           │                                │
     │     Delete cookie              │                                │
     │     Redirect to /signin        │                                │
     │<───────────────────────────────┤                                │
     │                                │                                │
```

---

## Security Measures

### Password Security

1. **Hashing Algorithm**: bcrypt (12 rounds)
2. **Salt**: Automatically generated per password
3. **Storage**: Only hashed password stored (never plain text)

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("plain_password")

# Verify password
is_valid = pwd_context.verify("plain_password", hashed)
```

### JWT Security

1. **Algorithm**: HS256 (HMAC with SHA-256)
2. **Secret**: 32+ character random string (user provided)
3. **Expiration**: 7 days (configurable)
4. **Claims**:
   - `sub`: User ID (subject)
   - `email`: User email
   - `exp`: Expiration timestamp
   - `iat`: Issued at timestamp

### Token Storage

**Recommended**: httpOnly Cookie
- **Pros**: Immune to XSS attacks, automatic inclusion in requests
- **Cons**: Vulnerable to CSRF (mitigated by SameSite attribute)

**Alternative**: localStorage
- **Pros**: Simple to implement, works cross-domain
- **Cons**: Vulnerable to XSS attacks

```javascript
// Set httpOnly cookie (backend sets this in response)
Set-Cookie: auth_token=eyJ...; HttpOnly; Secure; SameSite=Lax; Max-Age=604800

// Read cookie (automatically sent with requests)
// No JavaScript access (httpOnly)
```

### CORS Security

```python
# FastAPI CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin only
    allow_credentials=True,                   # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Error Handling

| Scenario | Status Code | Response | Frontend Action |
|----------|-------------|----------|-----------------|
| No token provided | 401 | `{"detail": "Not authenticated"}` | Redirect to /signin |
| Invalid token signature | 401 | `{"detail": "Could not validate credentials"}` | Delete cookie, redirect to /signin |
| Expired token | 401 | `{"detail": "Token expired"}` | Delete cookie, redirect to /signin |
| user_id mismatch | 403 | `{"detail": "Not authorized..."}` | Show error message |
| Network error | 500 | Connection error | Show retry button |

---

## Environment Variables

### Backend (.env)

```bash
BETTER_AUTH_SECRET=uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC
DATABASE_URL=postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)

```bash
BETTER_AUTH_SECRET=uwOPm1ir2FvGcIcJoOGyub2FQPQPysvC
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://neondb_owner:npg_QVsP5gmjC4wb@ep-snowy-cell-a4068rur-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Critical**: `BETTER_AUTH_SECRET` must be identical on both frontend and backend.

---

## Testing Authentication

### Manual Testing

1. **Signup**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

2. **Signin**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/signin \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

3. **Authenticated Request**:
   ```bash
   curl -X GET http://localhost:8000/api/1/tasks \
     -H "Authorization: Bearer <TOKEN_FROM_SIGNIN>"
   ```

### Automated Testing

```python
# pytest example
def test_signup():
    response = client.post(
        "/api/auth/signup",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert "token" in response.json()

def test_authenticated_request():
    # Signup and get token
    signup_response = client.post("/api/auth/signup", ...)
    token = signup_response.json()["token"]

    # Make authenticated request
    response = client.get(
        "/api/1/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

---

## Future Enhancements (Out of Scope for Step 2)

- **Token Refresh**: Issue new tokens before expiration
- **Token Revocation**: Blacklist tokens on signout
- **Multi-Factor Authentication (MFA)**: Add 2FA support
- **OAuth Social Login**: Google, GitHub, etc.
- **Password Reset**: Email-based password recovery
- **Email Verification**: Confirm email before activation
- **Session Management**: View/revoke active sessions
