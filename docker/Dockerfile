# Multi-stage build for lmelp (Le Masque et la Plume)
# Optimized for size and performance with ML models (Whisper, Transformers)

# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Builder - Install Python dependencies
FROM base as builder

WORKDIR /build

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy requirements
COPY .devcontainer/requirements.txt .

# Install dependencies with uv
# Note: Some packages (dbus-python) may fail in Docker - that's expected and handled
RUN uv pip install --system -r requirements.txt || \
    (grep -v "dbus-python" requirements.txt > requirements-docker.txt && \
     uv pip install --system -r requirements-docker.txt)

# Stage 3: Runtime image
FROM base as runtime

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY nbs/ /app/nbs/
COPY ui/ /app/ui/
COPY scripts/ /app/scripts/

# Create directories for volumes
RUN mkdir -p /app/audios /app/db /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# Expose Streamlit port
EXPOSE 8501

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Copy entrypoint script
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Default to web mode (Streamlit UI)
ENV LMELP_MODE=web

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
