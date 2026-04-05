# =============================================================================
# Tutor API — FastAPI backend for the Socratic AI tutor
# =============================================================================
# Build:  docker build -f docker/tutor.Dockerfile -t learn-ai-tutor .
# Run:    docker run -p 8000:8000 learn-ai-tutor
# =============================================================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---------------------------------------------------------------------------
# Dependencies — cached layer (only rebuilds when pyproject.toml changes)
# ---------------------------------------------------------------------------
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Application source
# ---------------------------------------------------------------------------
COPY tutor/ ./tutor/

# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------
EXPOSE 8000

# Run with 4 workers for production; override via UVICORN_WORKERS env var
CMD ["uvicorn", "tutor.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]
