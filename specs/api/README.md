# API Specifications

This directory contains API endpoint and contract specifications for backend services.

## Organization

API specs define:
- Endpoint paths and methods
- Request/response schemas
- Authentication requirements
- Error responses
- Rate limiting and quotas

## Planned Specifications

### Step 2: RESTful Task API
- **rest-endpoints.md** - Task CRUD endpoints (planned)
- **authentication-api.md** - Better Auth endpoints (planned)

### Step 3+: AI Chatbot API
- **chatbot-endpoints.md** - OpenAI integration endpoints (planned)

## Current Status

**Not yet implemented** - Specifications will be created when developing the FastAPI backend in Step 2.

## API Design Principles

When creating API specs, follow these guidelines:
- RESTful design patterns
- JSON request/response format
- JWT authentication via Authorization header
- Consistent error response format
- API versioning (e.g., /api/v1/)
- OpenAPI/Swagger documentation
