# Multi-stage Dockerfile for FastAPI Backend
# Stage 1: Builder - Install dependencies
# Stage 2: Runtime - Minimal production image

# ============================================
# Stage 1: Build stage
# ============================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev dependencies for production)
RUN uv sync --frozen --no-dev

# ============================================
# Stage 2: Runtime stage
# ============================================
FROM python:3.13-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ /app/src/

# Copy alembic migrations (if needed for database setup)
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set PATH to include virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose application port
EXPOSE 8000

# Health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start FastAPI application with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
