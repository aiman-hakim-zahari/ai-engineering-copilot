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

Requires Python 3.12+.

```bash
cd src/ml
python -m venv .venv
# Windows:    .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8001
```

Then:

```bash
curl http://localhost:8001/healthz
# {"status":"ok","service":"ml","version":"0.1.0"}
```

Interactive docs at <http://localhost:8001/docs>.

## Tests

```bash
pytest
```

## Lint

```bash
ruff check .
ruff format .
```

## Docker

```bash
docker build -t copilot-ml .
docker run --rm -p 8001:8001 copilot-ml
```

The container's `HEALTHCHECK` polls `/healthz` and is what
`docker-compose` keys on for the `ml` service's `service_healthy`
condition.
