# AI Engineering Copilot

> AI-powered document intelligence platform — upload engineering documents,
> ask questions, and receive contextual answers with source citations.

[![.NET 8](https://img.shields.io/badge/.NET-8.0-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![C#](https://img.shields.io/badge/C%23-12-239120?logo=csharp&logoColor=white)](https://learn.microsoft.com/dotnet/csharp/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
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

| Layer            | Technology                                  |
|------------------|---------------------------------------------|
| Backend API      | ASP.NET Core 8, C# 12                       |
| Frontend         | React 18, Vite, TypeScript 5                |
| Database         | PostgreSQL 16 + pgvector                    |
| LLM / Embeddings | Ollama (`llama3`, `nomic-embed-text`)       |
| Auth             | JWT (access + refresh)                      |
| Testing          | xUnit (unit + integration)                  |
| Orchestration    | Docker Compose                              |

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for system design, data flow, and component diagrams.

```
┌──────────┐   HTTPS    ┌───────────────┐   SQL    ┌──────────────┐
│  React   │ ─────────▶ │  ASP.NET Core │ ───────▶ │  PostgreSQL  │
│ Frontend │            │   Backend     │          │  + pgvector  │
└──────────┘            └───────┬───────┘          └──────────────┘
                                │ HTTP
                                ▼
                        ┌───────────────┐
                        │    Ollama     │
                        │  (embeddings  │
                        │  + chat LLM)  │
                        └───────────────┘
```

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
- Backend API: <http://localhost:5000>
- Swagger docs: <http://localhost:5000/swagger>

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
│   ├── backend/        # ASP.NET Core solution
│   └── frontend/       # React (Vite) application
├── tests/
│   ├── unit/           # xUnit unit tests
│   └── integration/    # xUnit integration tests
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

- [x] **Phase 0** — Repository setup
- [ ] **Phase 1** — Auth + document upload
- [ ] **Phase 2** — AI processing pipeline + RAG
- [ ] **Phase 3** — Chat interface + semantic search
- [ ] **Phase 4** — Admin dashboard + observability

---

## Contributing

This is a portfolio project, but bug reports and suggestions are welcome via [issues](https://github.com/aiman-hakim-zahari/ai-engineering-copilot/issues).

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).

---

## License

[MIT](LICENSE) © Aiman Hakim Zahari
