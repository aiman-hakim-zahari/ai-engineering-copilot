# Architecture

This repo is currently a small vertical-slice demo, not a production platform.

## Implemented Service Map

| Service | Runtime | Responsibility |
| --- | --- | --- |
| `frontend` | Next.js + TypeScript | Document input, chat form, answer and source display |
| `backend` | ASP.NET Core 8 | Public API gateway, Swagger, CORS, forwarding to ML service |
| `ml` | Python 3.12 + FastAPI | In-memory chunking, keyword retrieval, extractive answer fallback |

```text
Browser
  -> Next.js frontend
  -> ASP.NET Core gateway
  -> FastAPI ML service
  -> in-memory chunk store
```

## Boundaries

- The frontend calls only the ASP.NET Core gateway.
- The gateway owns public API shape and basic error handling.
- The Python service owns chunking, retrieval, and answer construction.
- No service currently persists data after process restart.

## Current Tradeoffs

- In-memory chunks keep the demo easy to run, but data is lost on restart.
- Keyword retrieval is transparent and dependency-free, but not semantic search.
- Optional Ollama support can improve answer wording, but the default path does
  not require model downloads.

## Future Architecture

The likely next step is PostgreSQL with pgvector:

```text
Next.js
  -> ASP.NET Core gateway
  -> FastAPI ML service
  -> PostgreSQL + pgvector
```

Auth, RBAC, admin dashboards, audit logs, observability, and streaming are future
work and are not implemented in the current codebase.
