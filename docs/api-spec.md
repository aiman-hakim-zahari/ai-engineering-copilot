# API Specification

The system exposes two API surfaces:

- **Gateway API** (public) — ASP.NET Core, called by the frontend.
- **ML Service API** (internal) — Python FastAPI, called only by the gateway.

The frontend never calls the ML service directly. All authentication, authorization, and persistence happen in the gateway.

---

## Gateway API

Base URL: `http://localhost:5000`
Auth: Bearer JWT (issued by `POST /auth/login`)

Endpoints are documented here in addition to the live OpenAPI spec at `/swagger`.

### Auth

| Method | Path             | Description                              |
|--------|------------------|------------------------------------------|
| POST   | `/auth/register` | Create a new user account                |
| POST   | `/auth/login`    | Exchange credentials for a JWT pair      |
| POST   | `/auth/refresh`  | Rotate an access token via refresh token |

### Documents

| Method | Path                    | Description                                  |
|--------|-------------------------|----------------------------------------------|
| POST   | `/documents`            | Upload a document (multipart/form-data)      |
| GET    | `/documents`            | List user's documents                        |
| GET    | `/documents/{id}`       | Get document metadata + processing status    |
| DELETE | `/documents/{id}`       | Soft-delete a document and its embeddings    |

Document uploads are persisted by the gateway, then forwarded to the ML service for chunking and embedding via `POST /ingest` (see below).

### Conversations / Chat

| Method | Path                            | Description                                                          |
|--------|---------------------------------|----------------------------------------------------------------------|
| POST   | `/conversations`                | Create a new conversation                                            |
| GET    | `/conversations`                | List user's conversations                                            |
| GET    | `/conversations/{id}/messages`  | Get messages for a conversation                                      |
| POST   | `/chat`                         | Ask a question; gateway orchestrates ML call and streams back (SSE)  |
| POST   | `/search`                       | Hybrid semantic + keyword search (delegates to ML `POST /retrieve`)  |

### Admin

| Method | Path                    | Description                                  |
|--------|-------------------------|----------------------------------------------|
| GET    | `/admin/metrics`        | Ingestion + embedding throughput stats       |
| GET    | `/admin/users`          | List users (role: admin)                     |
| GET    | `/admin/audit-logs`     | Recent audit log entries                     |

Request and response schemas are defined alongside controllers and exposed via Swagger.

---

## ML Service API (internal)

Base URL: `http://ml:8001` (inside Docker network) / `http://localhost:8001` (host)
Auth: shared service token via `X-Internal-Token` header (not user JWT).
Docs: FastAPI auto-generated at `/docs` and `/redoc`.

The ML service is **stateless** with respect to user/business data. It reads document chunks and writes embeddings into the shared PostgreSQL database, but it does not know about users, auth, conversations, or audit logs.

### Pipeline endpoints

| Method | Path        | Description                                                                                          |
|--------|-------------|------------------------------------------------------------------------------------------------------|
| POST   | `/ingest`   | Accept a `document_id` + raw text; chunk, embed, write to `chunks`                                   |
| POST   | `/embed`    | Embed an arbitrary text payload, return the vector (used for ad-hoc retrieval and tests)             |
| POST   | `/retrieve` | Given a query + `document_set_id`, return top-k chunks (vector + lexical fusion)                     |
| POST   | `/rerank`   | Given a query + candidate chunks, return a reranked list with scores                                 |
| POST   | `/answer`   | End-to-end: embed → retrieve → rerank → construct prompt → call LLM → return `{ answer, sources[], metrics }` |

### Evaluation & ops

| Method | Path         | Description                                                                                  |
|--------|--------------|----------------------------------------------------------------------------------------------|
| POST   | `/evaluate`  | Run the golden Q/A dataset; return recall@k, MRR, faithfulness                               |
| GET    | `/healthz`   | Liveness probe                                                                               |
| GET    | `/readyz`    | Readiness probe (checks Postgres + Ollama connectivity)                                      |
| GET    | `/metrics`   | Prometheus scrape endpoint                                                                   |

---

## Inter-service Contract

- **Transport:** REST over HTTP, content type `application/json`.
- **Rationale:** chosen for operational simplicity, debuggability, and adequacy at expected scale. See [architecture.md](architecture.md#inter-service-contract) for the migration path to gRPC or OpenAPI codegen.
- **Idempotency:** `/ingest` is idempotent on `(document_id, chunk_index)`; safe to retry.
- **Correlation:** the gateway forwards `X-Correlation-ID` on every ML call; the ML service echoes it back in responses and logs.
- **Errors:** the ML service returns RFC 7807 problem details (`application/problem+json`). The gateway translates 5xx into a single user-facing error and surfaces the correlation ID for tracing.
- **Timeouts:** gateway → ML default timeout is 60s; `/answer` may stream partial results.
