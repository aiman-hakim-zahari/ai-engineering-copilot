# ML Service

Python FastAPI service owning the RAG pipeline for the AI Engineering Copilot.

This service is **stateless** with respect to business data. The C# application
backend orchestrates calls to it over REST; the only persistence boundary it
touches is the shared `chunks` table (with the `embedding vector` column) in
PostgreSQL.

See [`docs/architecture.md`](../../docs/architecture.md) for the full service
map and [`docs/api-spec.md`](../../docs/api-spec.md) for endpoint shapes.

## Status

Day 1 scaffold — FastAPI app and `/healthz` only. Ingest, embed, retrieve,
rerank, answer, and evaluate land over Weeks 1–2 per
[`docs/prompts/60_day_roadmap.md`](../../docs/prompts/60_day_roadmap.md).

## Local development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/) as the
dependency manager.

```bash
# Install uv once (any of):
#   curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
#   winget install --id=astral-sh.uv                  # Windows
#   pipx install uv

cd src/ml
uv sync           # creates .venv/, installs runtime + dev groups, generates uv.lock
uv run uvicorn app.main:app --reload --port 8001
```

Then:

```bash
curl http://localhost:8001/healthz
# {"status":"ok","service":"ml","version":"0.1.0"}
```

Interactive docs at <http://localhost:8001/docs>.

> **First-time setup note.** `uv sync` will generate `uv.lock` if it
> doesn't exist. Commit the lock file so Docker builds and CI use
> identical pinned versions.

## Tests

```bash
uv run pytest
```

## Lint

```bash
uv run ruff check .
uv run ruff format .
```

## Docker

The Dockerfile uses `uv sync --frozen`, so `uv.lock` **must** be
checked in before building.

```bash
docker build -t copilot-ml .
docker run --rm -p 8001:8001 copilot-ml
```

The container's `HEALTHCHECK` polls `/healthz` and is what
`docker-compose` keys on for the `ml` service's `service_healthy`
condition.
