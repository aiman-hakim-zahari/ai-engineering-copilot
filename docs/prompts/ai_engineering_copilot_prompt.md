# AI Engineering Copilot — Project Planning Prompt

> **Target Role:** AI Software Development Engineer (Intel, Penang — JR0283812)
> **Purpose:** Portfolio project demonstrating enterprise-grade AI/backend engineering skills

---

## Overview

You are a senior software architect and AI platform engineer.

Design a **production-quality AI Engineering Copilot** — a document intelligence platform built to demonstrate enterprise-grade engineering skills aligned with the following competencies: C# / .NET, ASP.NET Core Web API, Python / FastAPI, advanced SQL and database optimization, Next.js + TypeScript frontend, LLM/RAG integration, REST API design between polyglot services, Docker containerization, and full SDLC best practices.

---

## Application Purpose

Users can:

- Upload engineering documents (PDF, DOCX, TXT)
- Ask natural language questions about their documents
- Perform semantic and hybrid search across indexed content
- Receive AI-generated answers with source citations
- Manage documents, chat sessions, and history

---

## Tech Stack

| Layer | Technology |
|---|---|
| **API Gateway** | ASP.NET Core 8 Web API, C#, Entity Framework Core |
| **ML Service** | Python 3.12, FastAPI, sentence-transformers / PyTorch, pgvector via `asyncpg` (or SQLAlchemy async) |
| **Inter-service** | REST over HTTP (JSON) — rationale: simplicity, debuggability, adequacy at expected scale. Migration path to gRPC or OpenAPI codegen if needed. |
| **Database** | PostgreSQL + pgvector (shared between gateway and ML service) |
| **Auth** | JWT authentication |
| **API Docs** | Swagger / OpenAPI (gateway); FastAPI auto-docs (ML service) |
| **Frontend** | Next.js, TypeScript, Tailwind CSS |
| **HTTP / Data Fetching** | Native `fetch` + TanStack Query |
| **AI** | Ollama (local LLM + embedding model) by default; pluggable to OpenAI / Anthropic via single provider interface. RAG pipeline with pgvector. |
| **Resilience** | `Microsoft.Extensions.Http.Resilience` (gateway → ML, gateway → Ollama); `tenacity` (Python ML retries) |
| **Logging** | Serilog (C#) + `structlog` (Python), JSON output; OpenTelemetry for cross-service tracing |
| **DevOps** | Docker, Docker Compose |
| **Testing** | xUnit + FluentAssertions (C#); pytest (Python); Playwright (E2E) |

---

## Architecture Requirements

Follow clean architecture principles in the C# gateway and idiomatic FastAPI module layout in the Python ML service:

- Service / repository pattern (gateway)
- Clear pipeline stages (ML service: parse → chunk → embed → retrieve → rerank → generate)
- Separation of concerns
- Modular API structure
- Scalable design with stateless ML service

The system must include **five containers**:

1. `frontend` — Next.js (TypeScript)
2. `api` — ASP.NET Core gateway
3. `ml` — Python FastAPI ML service
4. `postgres` — PostgreSQL + pgvector (shared)
5. `ollama` — local LLM + embedding server (pluggable to OpenAI / Anthropic)

### Service boundaries

- The **C# gateway** is the system of record for all user, auth, and business state (users, documents, conversations, messages, audit logs, refresh tokens, rate-limit counters). It owns authentication, authorization, document metadata via EF Core, conversation history, request orchestration, audit logging, and rate limiting. Persists to PostgreSQL.
- The **Python ML service** is **stateless** with respect to business data. It owns chunking, embedding generation, vector search, reranking, prompt construction, LLM inference, and the evaluation harness. Reads/writes only the `chunks` table (with the `embedding vector` column) and reads `documents` read-only.
- **Inter-service communication is REST over HTTP (JSON)**, chosen for operational simplicity, debuggability, and adequacy at expected scale. Migration path: gRPC or OpenAPI codegen if throughput or contract enforcement become bottlenecks.
- Neither service knows about the other's domain. The shared PostgreSQL database is the only place their concerns meet.

---

## Core Features

### 1. Authentication
- User registration and login
- JWT tokens (access + refresh)
- Role-based authorization: `User` / `Admin`

### 2. Document Upload Pipeline
- File upload (PDF, DOCX, TXT)
- Metadata storage
- Duplicate detection
- Async processing queue

### 3. AI Processing Pipeline
- Text extraction
- Chunking (document-type-aware)
- Embedding generation via Ollama
- pgvector indexing

### 4. AI Chat System
- RAG-based question answering
- Contextual answers with source citations
- Persistent chat history per session

### 5. Semantic + Hybrid Search
- pgvector cosine similarity search
- Keyword filtering
- Hybrid retrieval combining both

### 6. Admin Dashboard
- Document status and indexing metrics
- AI request logs
- Failed job tracking and reprocessing

---

## Database Design (PostgreSQL + pgvector)

Design a normalized relational schema with the following tables:

| Table | Purpose |
|---|---|
| `users` | User accounts and credentials |
| `roles` | Role definitions |
| `documents` | Uploaded document metadata |
| `document_chunks` | Parsed text segments |
| `embeddings` | Vector representations (`vector(1536)`) |
| `chat_sessions` | Conversation sessions per user |
| `chat_messages` | Individual messages within sessions |
| `audit_logs` | System activity tracking |
| `processing_jobs` | Async job queue and status |

**For each table, specify:**
- Primary keys, foreign keys, constraints
- Index strategy (B-tree, GIN, IVFFlat for vectors)
- Query optimization approach

**Vector storage decision:**
Use **pgvector** within PostgreSQL. Provide a tradeoff analysis comparing pgvector against dedicated external vector databases (Qdrant, Weaviate, Pinecone) and justify the choice for this architecture.

**Pagination strategy:**
Use keyset (cursor-based) pagination over `OFFSET` for large datasets.

---

## Backend Design

### Components to Design
- Controllers
- Services
- Repositories
- DTOs
- Middleware
- Background workers (`IHostedService` or Hangfire)

### Non-Functional Requirements
- `async`/`await` throughout
- Retry logic: `Microsoft.Extensions.Http.Resilience` for HTTP (Ollama), standalone Polly for job pipeline
- Structured logging: Serilog with JSON output + Seq sink
- Observability: OpenTelemetry (logs, traces, metrics)
- Input validation: FluentValidation
- Global exception handling middleware
- API rate limiting (ASP.NET Core built-in rate limiter)

### Provide
- Full REST API endpoint list with HTTP method, route, auth requirement
- Request / response body examples
- Authentication flow (register → login → JWT → refresh)
- Document upload flow (upload → parse → chunk → embed → index)
- AI orchestration flow (query → retrieve → prompt → respond → cite)

---

## RAG Pipeline Design

Design a complete, production-quality Retrieval-Augmented Generation pipeline:

| Stage | Details |
|---|---|
| **Chunking** | Document-type-aware splitting; define chunk size and overlap strategy |
| **Embedding** | Generate via Ollama embedding model; store as `vector(1536)` in pgvector |
| **Retrieval** | Top-k cosine similarity via pgvector; define k and similarity threshold |
| **Prompt construction** | Inject retrieved chunks + recent chat history into system prompt |
| **Response synthesis** | Generate answer via Ollama LLM |
| **Hallucination mitigation** | Techniques: grounding instructions, confidence thresholding, source-only answers |
| **Citation generation** | Link answer segments back to source `document_chunk` records |

---

## Frontend Design

### Pages
- Login / Register
- Dashboard (document list, recent chats)
- Document Upload (drag-and-drop, progress, status)
- Chat Interface (streaming responses, citations panel)
- Admin Analytics (metrics, job queue, logs)

### Technical Approach
- **Axios** as the HTTP adapter
- **TanStack Query** for server state (caching, background refetch, loading/error states)
- **useState / useContext** for local UI state
- Streaming response handling for the chat interface (SSE or chunked transfer)
- Component hierarchy documented per page

---

## DevOps Design

Design a complete Docker Compose setup including:

- Service definitions for all five containers
- Environment variable management (`.env` files, secrets)
- Health checks and dependency ordering (`depends_on` + `condition`)
- Volume mounts (PostgreSQL data, Ollama models, uploaded files)
- Local development setup instructions
- Production hardening notes (reverse proxy, TLS, resource limits)

---

## Testing Strategy

| Layer | Approach |
|---|---|
| **Unit tests** | Services and repositories with mocked dependencies |
| **Integration tests** | API endpoints against a test database |
| **Database tests** | EF Core migrations, query correctness |
| **AI pipeline tests** | Chunking logic unit tests; embedding and retrieval with mocked Ollama |

Use **xUnit** and **FluentAssertions** throughout.

---

## Required Output

Generate the following as a senior engineering planning document. Provide implementation-quality detail — no placeholders.

1. **High-level architecture diagram** (ASCII or described component map)
2. **Backend folder structure** (solution layout, project structure, namespace conventions)
3. **Frontend folder structure** (component hierarchy, page organization)
4. **Full SQL schema** (column types, constraints, indexes for all tables)
5. **API specification** (all endpoints, methods, auth requirements, request/response shapes)
6. **pgvector indexing and query optimization recommendations** (IVFFlat vs HNSW, index tuning)
7. **RAG pipeline step-by-step design** (each stage with implementation notes)
8. **Docker Compose architecture** (full `docker-compose.yml` structure with annotations)
9. **Phased development roadmap** — 60-day plan: Weeks 1–2 Python ML core, Weeks 3–4 ASP.NET gateway, Weeks 5–6 Next.js frontend, Weeks 7–8 evaluation harness + production hardening, Weeks 9–10 buffer/polish. See `docs/prompts/60_day_roadmap.md`.
10. **GitHub README outline** (sections, badges, setup instructions, architecture overview)
11. **Resume bullet points** targeting enterprise AI/backend engineering roles (C#, SQL, RAG, LLM, Docker, Web API)
12. **Suggested future enhancements** (MongoDB/NoSQL integration, multi-tenancy, real-time streaming LLM responses, fine-tuning pipeline, VSTO integration)

---

## Key Design Decisions (Pre-decided)

| Decision | Choice | Rationale |
|---|---|---|
| Vector storage | pgvector (in PostgreSQL) | Avoids separate service, sufficient for portfolio scale, native SQL joins |
| HTTP resilience | `Microsoft.Extensions.Http.Resilience` | Built into .NET 8, wraps Polly v8, idiomatic |
| Job pipeline resilience | Polly standalone | Richer policy composition for background workers |
| Logging | Serilog + Seq | Structured JSON, rich sink ecosystem, interview-visible output |
| Observability | OpenTelemetry | Cloud-native signal, demonstrates enterprise platform awareness |
| Pagination | Keyset / cursor-based | Performant at scale vs OFFSET degradation |
| Frontend data layer | Axios + TanStack Query | Axios for HTTP, TanStack Query for caching and server state |
