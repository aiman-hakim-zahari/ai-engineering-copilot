# AI Engineering Copilot

> AI-powered document intelligence platform — upload engineering documents,
> ask questions, and receive contextual answers with source citations.

[![.NET 8](https://img.shields.io/badge/.NET-8.0-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![C#](https://img.shields.io/badge/C%23-12-239120?logo=csharp&logoColor=white)](https://learn.microsoft.com/dotnet/csharp/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-enabled-336791)](https://github.com/pgvector/pgvector)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Ollama](https://img.shields.io/badge/Ollama-local%20LLM-000000)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **Document ingestion** — upload and parse PDF, DOCX, and TXT files
- **RAG-based Q&A** — contextual answers grounded in your documents, with source citations
- **Semantic + hybrid search** — pgvector-backed vector search combined with full-text relevance
- **JWT authentication** — role-based access (admin / user) with refresh tokens
- **Admin dashboard** — ingestion metrics, embedding throughput, and processing health
- **Fully containerized** — single `docker compose up` brings up the full stack locally

---

## Tech Stack

| Layer                       | Technology                                                                   |
|-----------------------------|------------------------------------------------------------------------------|
| Frontend                    | Next.js 15, TypeScript 5                                                     |
| API Gateway                 | ASP.NET Core 8, C# 12, Entity Framework Core                                 |
| ML Service                  | Python 3.12, FastAPI, sentence-transformers / PyTorch                        |
| Database                    | PostgreSQL 16 + pgvector (shared between gateway and ML service)             |
| LLM / Embeddings            | Ollama local (`llama3`, `nomic-embed-text`); pluggable to OpenAI / Anthropic |
| Inter-service communication | REST over HTTP (JSON)                                                        |
| Auth                        | JWT (access + refresh)                                                       |
| Testing                     | xUnit (C#), pytest (Python), Playwright (E2E)                                |
| Orchestration               | Docker Compose (5 services)                                                  |

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for system design, data flow, and component diagrams.

```
┌────────────┐  HTTPS   ┌─────────────────┐   SQL    ┌──────────────┐
│  Next.js   │ ───────▶ │  ASP.NET Core   │ ───────▶ │  PostgreSQL  │
│  Frontend  │          │   API Gateway   │          │  + pgvector  │
└────────────┘          │ (auth, docs,    │          └──────▲───────┘
                        │  conversations, │                 │ SQL
                        │  audit, RBAC)   │                 │
                        └────────┬────────┘          ┌──────┴───────┐
                                 │ REST / JSON       │   Python     │
                                 ▼                   │  ML Service  │
                        ┌─────────────────┐  HTTP    │  (FastAPI:   │
                        │   Python ML     │ ───────▶ │   chunk,     │
                        │   Service       │          │   embed,     │
                        │   (FastAPI)     │          │   retrieve,  │
                        └────────┬────────┘          │   rerank,    │
                                 │ HTTP              │   generate)  │
                                 ▼                   └──────────────┘
                        ┌─────────────────┐
                        │     Ollama      │
                        │  (embeddings +  │
                        │   chat LLM —    │
                        │   pluggable to  │
                        │   OpenAI /      │
                        │   Anthropic)    │
                        └─────────────────┘
```

**Key principle:** the C# gateway is the system of record for all user, auth,
and business state. The Python ML service is stateless and only performs ML
work (chunking, embedding, retrieval, reranking, generation). Neither service
knows about the other's domain.

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2
- [Git](https://git-scm.com/)
- ~8 GB free disk (for Ollama models and Postgres data volumes)

### Setup

```bash
git clone https://github.com/aiman-hakim-zahari/ai-engineering-copilot.git
cd ai-engineering-copilot
cp .env.example .env
# Edit .env with your values (DB password, JWT secret, etc.)
docker compose up --build
```

Once everything is healthy:

- Frontend: <http://localhost:3000>
- API Gateway: <http://localhost:5000>
- Swagger docs: <http://localhost:5000/swagger>
- ML Service (internal): <http://localhost:8001>
- ML Service docs: <http://localhost:8001/docs>

To pull the Ollama models on first run:

```bash
docker exec -it copilot_ollama ollama pull nomic-embed-text
docker exec -it copilot_ollama ollama pull llama3
```

---

## API Reference

See [docs/api-spec.md](docs/api-spec.md) for the full REST endpoint reference, request/response schemas, and auth flows.

---

## Project Structure

```
ai-engineering-copilot/
├── src/
│   ├── api/            # ASP.NET Core gateway (auth, EF Core, orchestration)
│   ├── ml/             # Python FastAPI service (RAG pipeline)
│   └── frontend/       # Next.js application
├── tests/
│   ├── unit/           # xUnit (C#) + pytest (Python)
│   └── integration/    # cross-service integration tests
├── docs/               # Architecture, API spec, RAG design, DB schema
├── scripts/            # setup / seed / reset helpers
├── .github/            # Issue and PR templates
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
└── README.md
```

---

## Development Roadmap

60-day plan — see [docs/prompts/60_day_roadmap.md](docs/prompts/60_day_roadmap.md).

- [x] **Phase 0** — Repository setup
- [ ] **Weeks 1–2** — Python ML service end-to-end (ingest → chunk → embed → retrieve → answer; validated with curl/Postman)
- [ ] **Weeks 3–4** — ASP.NET Core gateway (JWT, EF Core users/conversations, HttpClient to ML, Swagger)
- [ ] **Weeks 5–6** — Next.js chat UI (streaming responses, document upload, source citations)
- [ ] **Weeks 7–8** — Evaluation harness (`/evaluate`, recall@k, MRR, faithfulness) + production hardening (Serilog + structlog, Prometheus, tracing, rate limiting)
- [ ] **Weeks 9–10 (buffer)** — Docker Compose finalization, README with architecture diagram, blog post, demo video, "what I'd do at scale" notes

---

## Contributing

This is a portfolio project, but bug reports and suggestions are welcome via [issues](https://github.com/aiman-hakim-zahari/ai-engineering-copilot/issues).

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).

---

## License

[MIT](LICENSE) © Aiman Hakim Zahari
