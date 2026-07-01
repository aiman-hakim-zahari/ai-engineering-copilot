# ML Service

Python FastAPI service for the demo RAG slice.

It accepts raw document text, chunks it into small in-memory passages, retrieves
matching chunks with lightweight keyword scoring, and returns an answer with
source chunks. It works without PostgreSQL, pgvector, Ollama, or paid API keys.

## Endpoints

- `GET /healthz`
- `POST /ingest`
- `POST /answer`

FastAPI docs are available at <http://localhost:8001/docs>.

## Local development

```bash
cd src/ml
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

## Tests

```bash
uv run pytest
```

## Optional Ollama

Set `OLLAMA_BASE_URL` and `OLLAMA_CHAT_MODEL` to let `/answer` try local Ollama
generation. If Ollama is missing or times out, the service automatically falls
back to extractive answers from matched chunks.
