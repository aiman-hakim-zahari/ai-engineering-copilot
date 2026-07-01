# API Specification

The frontend calls the ASP.NET Core gateway only. The gateway calls the FastAPI
ML service over HTTP.

## Gateway API

Base URL for local development: `http://localhost:5000`

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Gateway liveness |
| POST | `/documents` | Accept JSON text or multipart `.txt` / `.md`, then forward to ML `/ingest` |
| POST | `/chat` | Accept a question, then forward to ML `/answer` |

Swagger is available at `/swagger`.

### `POST /documents`

JSON request:

```json
{
  "source": "demo.md",
  "text": "The gateway is ASP.NET Core."
}
```

Response:

```json
{
  "document_id": "uuid",
  "chunks_indexed": 1,
  "sources": ["demo.md"]
}
```

Multipart form also works with `file`, optional `source`, and optional `text`.

### `POST /chat`

Request:

```json
{
  "question": "What is the gateway built with?",
  "topK": 4
}
```

Response:

```json
{
  "answer": "Based on the matching document context: ...",
  "sources": [
    {
      "source": "demo.md",
      "chunk_id": "abcd1234-1",
      "score": 2.4
    }
  ],
  "matched_chunks": [
    {
      "source": "demo.md",
      "chunk_id": "abcd1234-1",
      "score": 2.4,
      "text": "The gateway is ASP.NET Core."
    }
  ]
}
```

## ML Service API

Base URL for local development: `http://localhost:8001`

| Method | Path | Description |
| --- | --- | --- |
| GET | `/healthz` | ML service liveness |
| POST | `/ingest` | Chunk and store text in memory |
| POST | `/answer` | Retrieve matching chunks and return answer + sources |

FastAPI docs are available at `/docs`.

Authentication, streaming, `/retrieve`, `/rerank`, `/evaluate`, and metrics are
not implemented in this slice.
