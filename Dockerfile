# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies (cached layer — only reruns when lock/toml change)
ENV UV_PROJECT_ENVIRONMENT=/venv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --python=${PYTHON_VERSION}

# Copy the project into the image
COPY . /app

# Sync the project (installs the project itself into the venv)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --python=${PYTHON_VERSION}

# Collect static files (uses a dummy SECRET_KEY since we only need the files)
RUN SECRET_KEY=dummy-build-key DEBUG=False ALLOWED_HOSTS=* \
    EMAIL_HOST_USER=noop EMAIL_HOST_PASSWORD=noop \
    /venv/bin/python manage.py collectstatic --noinput


FROM python:${PYTHON_VERSION}-slim-bookworm AS runner

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd --system app && useradd --system --gid app app

# Copy the virtual environment from the builder stage
COPY --from=builder /venv /venv

# Place executables in the environment at the front of the path
ENV PATH="/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy the project files
COPY --from=builder /app /app

# Create directories for runtime data and give ownership to app user
RUN mkdir -p /app/data /app/media /app/static && \
    chown -R app:app /app

# Expose port
EXPOSE 8000

# Health check using Python stdlib (no curl needed in slim image)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')"

# Run as non-root user
USER app

# Run gunicorn sized for a 2GB RAM droplet
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "torres_web.wsgi:application"]
