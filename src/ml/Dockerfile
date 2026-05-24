# syntax=docker/dockerfile:1.7

# Official uv image with Python 3.12 preinstalled.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # uv: write bytecode at install time, copy instead of hardlink
    # (hardlinks break across mounted volumes).
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Make the project's venv discoverable on PATH for CMD.
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# System deps: curl is used by the docker-compose healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install only runtime dependencies first. This layer is cached
# until pyproject.toml or uv.lock changes.
#
# Requires `uv.lock` to be checked in. Generate it locally with:
#   cd src/ml && uv sync
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Now copy the application code.
COPY app ./app

EXPOSE 8001

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
    CMD curl --fail --silent http://localhost:8001/healthz || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
