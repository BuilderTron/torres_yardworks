# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
ENV UV_PROJECT_ENVIRONMENT=/venv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --python=${PYTHON_VERSION}

# Copy the project into the image
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --python=${PYTHON_VERSION}


FROM python:${PYTHON_VERSION}-slim-bookworm AS runner

# Copy the environment from the builder stage
COPY --from=builder --chown=app:app /venv /venv

# Place executables in the environment at the front of the path
ENV PATH="/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Expose port
EXPOSE 8000

# Run commands
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "torres_web.wsgi:application"]
