"""FastAPI application entry point.

Main application with CORS configuration and API route registration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings


# Create FastAPI application instance
app = FastAPI(
    title="Hackathon Todo API",
    description="RESTful API for multi-user task management with JWT authentication",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Specific origins only (e.g., ["http://localhost:3000"])
    allow_credentials=True,  # Required for cookies and Authorization headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS)
    allow_headers=["*"],  # Allow all headers (including Authorization)
)


@app.get("/")
async def root():
    """Root endpoint with API information.

    Returns:
        dict: API metadata and documentation links
    """
    return {
        "name": "Hackathon Todo API",
        "version": "2.0.0",
        "description": "Full-stack web application for task management",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring.

    Returns:
        dict: Service health status
    """
    return {"status": "ok"}


# API router registration
from .api import auth, tasks

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
