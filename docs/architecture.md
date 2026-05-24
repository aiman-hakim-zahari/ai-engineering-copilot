# Architecture

System design and component decisions for the AI Engineering Copilot.

## Goals

- **Local-first:** full stack runs offline via Docker Compose with no third-party API keys required.
- **Citable answers:** every LLM response must include source document references.
- **Composable:** frontend, application backend, ML service, vector store, and LLM provider are independent and replaceable.
- **Clean service boundary:** business state lives in the C# application backend; ML compute lives in the Python service. Neither knows about the other's domain.

## Service Map

The system runs as five Docker Compose services:

| Service    | Language / Runtime              | Role                                                                                      |
|------------|---------------------------------|-------------------------------------------------------------------------------------------|
| `frontend` | Next.js + TypeScript            | Chat UI, document upload, auth pages                                                      |
| `api`      | ASP.NET Core 8, C# 12, EF Core  | Auth, authorization, document metadata, conversation history, orchestration, audit, rate limiting |
| `ml`       | Python 3.12, FastAPI            | Chunking, embedding, vector search, reranking, prompt construction, LLM inference, evaluation |
| `postgres` | PostgreSQL 16 + pgvector        | Shared relational + vector store                                                          |
| `ollama`   | Ollama                          | Local embedding + chat model server (pluggable to OpenAI / Anthropic)                     |

## Component Responsibilities

| Component        | Owns                                                                                              | Does **not** own                                |
|------------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------|
| Frontend         | UI state, JWT storage, streaming response rendering, citation display                              | Any business logic, any direct DB access        |
| Application Backend (C#) | Users, roles, JWT issuance, RBAC, tenant scoping, document metadata (EF Core), conversations, messages, audit logs, rate limiting, orchestration of ML calls | Embedding math, vector search, LLM calls         |
| ML Service (Py)  | Document chunking, embedding generation, pgvector queries, reranking, prompt construction, LLM inference, evaluation harness | Users, auth, business state, persistence beyond `chunks` |
| PostgreSQL       | Source of truth for both business and vector data                                                 | Application logic                               |
| Ollama           | Local embedding + chat model inference                                                            | Anything else                                   |

## Data Flow — Authenticated Question

1. **Frontend → Application Backend.** Next.js sends an authenticated request (`POST /chat`) to the ASP.NET Core application backend with the user's question and `document_set_id`.
2. **Backend validates.** The application backend validates the JWT, checks tenant / RBAC, writes an audit log entry, and persists the user's message to `messages`.
3. **Backend → ML.** The application backend calls the Python ML service (`POST /answer`) over REST with `{ question, document_set_id, conversation_context }`.
4. **ML pipeline.** Python service embeds the query, retrieves top-k candidate chunks from pgvector, reranks, constructs a grounded prompt, calls Ollama (or pluggable cloud LLM), and returns `{ answer, sources[], metrics: { latency_ms, tokens_in, tokens_out, recall@k } }`.
5. **Backend persists.** The application backend writes the assistant response to `messages` (including `sources` JSON, latency, token usage) and updates the conversation.
6. **Frontend renders.** The application backend streams the response back to the frontend, which renders the answer with clickable source citations.

## Inter-service Contract

**REST over HTTP (JSON).** Chosen for:

- **Operational simplicity** — every developer can debug with curl/Postman.
- **Debuggability** — payloads are inspectable; no codegen required to read traffic.
- **Adequacy at expected scale** — the call path is request/response, low fan-out, and bounded by LLM latency (seconds), so HTTP+JSON overhead is negligible.

**Migration path.** If contract drift or throughput become bottlenecks:

- **gRPC** — for tighter contracts and lower per-call overhead on the backend → ML hop.
- **OpenAPI codegen** — generate typed clients in both C# and Python from a single spec; keeps HTTP/JSON but enforces the schema.

**Error format.** ML service returns RFC 7807 problem details (`application/problem+json`). The application backend translates 5xx into a single user-facing error and surfaces the correlation ID for tracing.

## Key Principle

> The C# application backend is the **system of record** for all user, auth, and business state.
> The Python service is **stateless** and only does ML work.
> Neither service knows about the other's domain.

Concretely:

- The Python service never reads or writes `users`, `documents`, `conversations`, `messages`, or `audit_logs`.
- The C# application backend never embeds, never queries `chunks.embedding`, never calls Ollama directly.
- The shared PostgreSQL database is the only place their concerns meet, and the table ownership in [database-schema.md](database-schema.md#service-ownership) is enforced by code review.

## Key Decisions (ADR-style)

| Decision                          | Choice                                    | Rationale                                                                                       |
|-----------------------------------|-------------------------------------------|-------------------------------------------------------------------------------------------------|
| Split into two backend languages  | C# for application backend, Python for ML | Each language is dominant in its lane; demonstrates polyglot service design                     |
| Shared PostgreSQL                 | Single Postgres + pgvector for both       | Avoids data-sync complexity; pgvector is sufficient for portfolio scale                         |
| Inter-service protocol            | REST + JSON over HTTP                     | Simplicity and debuggability; migration path to gRPC / OpenAPI codegen if needed                |
| LLM backend                       | Ollama local, pluggable to cloud          | Offline-capable for demo; cloud APIs swap in via a single client interface                       |
| Application backend = system of record | All business state in C#             | Clean ownership boundary; Python service stays stateless and horizontally scalable              |
| ORM choice (C#)                   | Entity Framework Core                     | Migrations, LINQ, idiomatic for ASP.NET Core                                                    |

See [docs/rag-pipeline.md](rag-pipeline.md) for retrieval/generation details and [docs/database-schema.md](database-schema.md) for the schema with service ownership annotations.
