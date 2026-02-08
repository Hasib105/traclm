# Multi-stage Dockerfile for LLM Tracer
# Builds frontend assets and runs the Python backend

# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY apps/web/package.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY apps/web/ ./

# Build for production
RUN npm run build

# ============================================
# Stage 2: Python Runtime
# ============================================
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PICCOLO_CONF=llm_tracer.db.piccolo_conf

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy Python package files
COPY packages/llm-tracer/pyproject.toml packages/llm-tracer/README.md ./

# Create src directory structure
RUN mkdir -p src/llm_tracer

# Copy server source code
COPY packages/llm-tracer/src/ ./src/

# Install the package
RUN uv pip install --system -e .

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist ./static

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "llm_tracer", "--host", "0.0.0.0", "--port", "8000"]
