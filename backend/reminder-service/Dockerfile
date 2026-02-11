# Multi-stage build for reminder-service
# Base image: Python 3.13 slim

# Stage 1: Build stage
FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies to a virtual environment
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r reminderservice && \
    useradd -r -g reminderservice -u 1001 reminderservice && \
    chown -R reminderservice:reminderservice /app

# Copy virtual environment from builder
COPY --from=builder --chown=reminderservice:reminderservice /opt/venv /opt/venv

# Copy application code
COPY --chown=reminderservice:reminderservice src/ ./src/

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8001 \
    LOG_LEVEL=INFO

# Switch to non-root user
USER reminderservice

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
