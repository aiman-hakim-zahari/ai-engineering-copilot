# 60-Day Development Roadmap — AI Engineering Copilot

> **Goal:** Build the AI Engineering Copilot project with consistent daily commits across 60 days.
> **Target outcome:** A production-quality portfolio project ready for the Intel AI Software Development Engineer application.

---

## Daily Commit Principles

- **One meaningful commit per day minimum.** Use Conventional Commits format.
- **Push every day** — the green squares on your GitHub profile matter.
- **If a task is too large, split it.** Better to commit a half-finished feature behind a feature flag than to skip a day.
- **If you're stuck, commit docs or tests.** Writing tests for existing code or documenting decisions in `docs/` is always valid progress.
- **Tag milestones.** Use `git tag v0.1`, `v0.2`, etc. at the end of each phase.

---

## Phase Overview

The plan is organised as **8 weeks of build** + **2 weeks of buffer / polish**.

| Phase                  | Weeks | Focus                                                                                              |
|------------------------|-------|----------------------------------------------------------------------------------------------------|
| **Phase 0**            | pre-1 | Repository setup and planning ✅                                                                   |
| **Phase 1 — ML core**  | 1–2   | Python FastAPI ML service end-to-end (ingest → chunk → embed → retrieve → answer). No auth, no UI. |
| **Phase 2 — Gateway**  | 3–4   | ASP.NET Core gateway: JWT auth, EF Core for users/conversations, HttpClient → ML service, Swagger. |
| **Phase 3 — Frontend** | 5–6   | Next.js chat UI: streaming responses, document upload, source citations.                           |
| **Phase 4 — Hardening**| 7–8   | Evaluation harness, observability, rate limiting, production hardening across both services.       |
| **Phase 5 — Polish**   | 9–10  | Docker Compose finalisation, README, architecture diagram, blog post, demo video, scale notes.     |

---

## Phase 1 — Python ML Service (Weeks 1–2)

End-to-end RAG pipeline in Python first. Validate every step with `curl` / Postman before any auth or UI exists.

### Week 1 — Ingest + embed
- **Day 1.** Scaffold FastAPI app in `src/ml/` (`uvicorn`, `pydantic`, `pytest`, `ruff`). Add Dockerfile. `GET /healthz`.
  - **Commit:** `feat(ml): scaffold FastAPI service with health endpoint`
- **Day 2.** Add Postgres + pgvector connection (`asyncpg` or SQLAlchemy 2.x async). Migration tooling (`alembic`). `chunks` table.
  - **Commit:** `feat(ml): wire up pgvector via asyncpg with alembic migrations`
- **Day 3.** Parsers: PDF (`pypdf`), DOCX (`python-docx`), TXT. Unit tests with fixtures in `tests/ml/fixtures/`.
  - **Commit:** `feat(ml): add multi-format document parsers with unit tests`
- **Day 4.** Recursive character chunker, 800-token target with 100-token overlap. `tiktoken` for counts. Unit tests.
  - **Commit:** `feat(ml): implement recursive character chunker with token-aware sizing`
- **Day 5.** Ollama client (`httpx`). Embedding generation (`nomic-embed-text`, 768-dim). Retry with `tenacity`.
  - **Commit:** `feat(ml): integrate Ollama embedding client with resilient HTTP`
- **Day 6.** `POST /ingest` endpoint: takes `document_id` + raw text → chunks → embeds → writes rows. Idempotent on `(document_id, chunk_index)`.
  - **Commit:** `feat(ml): implement idempotent ingest endpoint`
- **Day 7.** End-to-end ingest smoke test. Seed a real PDF and verify rows in `chunks`. Document curl recipe.
  - **Commit:** `test(ml): add end-to-end ingest smoke test`

### Week 2 — Retrieve + answer
- **Day 8.** Vector search: cosine similarity via pgvector HNSW, top-k = 20. `POST /retrieve` skeleton.
  - **Commit:** `feat(ml): add HNSW vector search with top-k retrieval`
- **Day 9.** Add lexical search (`tsvector`) and RRF fusion. `POST /retrieve` returns fused top-k = 8.
  - **Commit:** `feat(ml): add lexical search and RRF fusion to retrieval`
- **Day 10.** Reranker (`bge-reranker-base` via `sentence-transformers`). `POST /rerank`. Wire into `/retrieve`.
  - **Commit:** `feat(ml): add cross-encoder reranking pass`
- **Day 11.** Prompt template with citation markers and grounding instructions. Ollama chat client.
  - **Commit:** `feat(ml): implement grounded prompt template and chat client`
- **Day 12.** `POST /answer` — end-to-end pipeline. Returns `{ answer, sources[], metrics }`.
  - **Commit:** `feat(ml): implement end-to-end /answer endpoint`
- **Day 13.** LLM provider abstraction: Ollama default, pluggable to OpenAI / Anthropic via env config.
  - **Commit:** `feat(ml): add pluggable LLM provider interface`
- **Day 14.** Document the Python service in `docs/`. Manual eval of 5 hand-picked questions.
  - **Commit:** `docs: document ML service endpoints and pipeline`

**🏁 Milestone:** `git tag v0.1-ml-core` — Python service answers questions over a real corpus, end-to-end, from curl.

---

## Phase 2 — ASP.NET Core Gateway (Weeks 3–4)

The gateway owns business state and orchestrates the Python service. No vector math here.

### Week 3 — Auth + persistence
- **Day 15.** Scaffold `src/api/`: Clean Architecture solution (`Api`, `Core`, `Infrastructure`, `Application`). Swagger.
  - **Commit:** `feat(api): scaffold clean architecture solution with Swagger`
- **Day 16.** EF Core + Npgsql. `users`, `refresh_tokens` entities + first migration. Reuse the shared Postgres.
  - **Commit:** `feat(api): configure EF Core with users and refresh tokens`
- **Day 17.** JWT (`Microsoft.AspNetCore.Authentication.JwtBearer`). `IJwtService` with options binding.
  - **Commit:** `feat(api): implement JWT token issuance and validation`
- **Day 18.** `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`. BCrypt hashing. FluentValidation.
  - **Commit:** `feat(api): add auth endpoints with hashed credentials`
- **Day 19.** Conversation + message entities. Migration. `POST /conversations`, `GET /conversations`, `GET /conversations/{id}/messages`.
  - **Commit:** `feat(api): add conversation and message persistence`
- **Day 20.** Document metadata entity. `POST /documents` (multipart). Stores the file, creates the row.
  - **Commit:** `feat(api): add document upload endpoint with metadata persistence`
- **Day 21.** Audit log entity + middleware. Every authenticated request writes an audit row.
  - **Commit:** `feat(api): add audit logging middleware`

### Week 4 — Orchestration
- **Day 22.** `IMlClient` (typed `HttpClient` with `Microsoft.Extensions.Http.Resilience`). Forward `X-Correlation-ID`.
  - **Commit:** `feat(api): add resilient HttpClient for ML service`
- **Day 23.** On document upload → call `POST /ingest` on ML service → update document status.
  - **Commit:** `feat(api): wire document upload to ML ingest pipeline`
- **Day 24.** `POST /chat` — orchestrates: persist user message → call `POST /answer` → persist assistant message with sources, latency, tokens.
  - **Commit:** `feat(api): implement chat orchestration with ML service`
- **Day 25.** SSE streaming from gateway to frontend; gateway proxies streaming responses from ML.
  - **Commit:** `feat(api): stream chat responses via server-sent events`
- **Day 26.** `POST /search` — gateway calls `POST /retrieve` on ML; gateway enforces tenant scoping on document_ids.
  - **Commit:** `feat(api): add search endpoint with tenant-scoped retrieval`
- **Day 27.** `[Authorize(Roles = "Admin")]` admin endpoints: `/admin/metrics`, `/admin/users`, `/admin/audit-logs`.
  - **Commit:** `feat(api): add admin endpoints with role-based authorization`
- **Day 28.** Integration tests against a Testcontainers Postgres + a fake ML service. Cover the happy paths end-to-end.
  - **Commit:** `test(api): add integration tests with Testcontainers`

**🏁 Milestone:** `git tag v0.2-gateway` — full gateway with auth, persistence, and ML orchestration, exercised via Swagger.

---

## Phase 3 — Next.js Frontend (Weeks 5–6)

User-facing chat application. Streaming responses, document upload, source citations.

### Week 5 — Foundation + auth
- **Day 29.** Scaffold Next.js 15 app in `src/frontend/` (App Router, TypeScript, Tailwind). Replace prior Vite scaffold.
  - **Commit:** `feat(frontend): scaffold Next.js app with App Router and Tailwind`
- **Day 30.** API client (`fetch` wrapper) with JWT injection and refresh-on-401. TanStack Query setup.
  - **Commit:** `feat(frontend): add API client with auth interceptor and TanStack Query`
- **Day 31.** Login + Register pages. Form validation. Auth context with token storage.
  - **Commit:** `feat(frontend): implement login and register flows`
- **Day 32.** Protected route layout. Redirect to `/login` when unauthenticated.
  - **Commit:** `feat(frontend): add protected layout and auth guard`
- **Day 33.** Conversation list sidebar. `GET /conversations` with TanStack Query.
  - **Commit:** `feat(frontend): add conversation list sidebar`
- **Day 34.** Document upload page. Drag-and-drop. Show processing status (polls until `ready`).
  - **Commit:** `feat(frontend): add document upload with status polling`
- **Day 35.** Document list with delete confirmation.
  - **Commit:** `feat(frontend): add document management UI`

### Week 6 — Chat experience
- **Day 36.** Chat layout (sidebar + main pane). Empty state.
  - **Commit:** `feat(frontend): build chat layout shell`
- **Day 37.** Message rendering. User vs assistant styling. Markdown rendering.
  - **Commit:** `feat(frontend): render markdown chat messages`
- **Day 38.** Streaming responses via SSE / fetch streams. Show typing indicator.
  - **Commit:** `feat(frontend): implement streaming chat responses`
- **Day 39.** Source citation chips below each assistant message. Click → open document at the cited page.
  - **Commit:** `feat(frontend): add clickable source citations`
- **Day 40.** New conversation flow. Title auto-generation from first message.
  - **Commit:** `feat(frontend): add new-conversation flow`
- **Day 41.** Loading skeletons, toast notifications, error boundaries.
  - **Commit:** `feat(frontend): polish UX with skeletons, toasts, error states`
- **Day 42.** Responsive layout + accessibility audit (keyboard nav, focus rings, aria labels).
  - **Commit:** `feat(frontend): make chat responsive and accessible`

**🏁 Milestone:** `git tag v0.3-frontend` — full user-facing app: log in, upload documents, ask questions with streaming answers and citations.

---

## Phase 4 — Evaluation & Hardening (Weeks 7–8)

Quality gates and operational readiness across both services.

### Week 7 — Evaluation harness
- **Day 43.** Golden dataset: 20–30 hand-curated Q/A pairs over the demo corpus. Checked into `src/ml/eval/`.
  - **Commit:** `feat(ml): add golden Q/A dataset for evaluation`
- **Day 44.** `POST /evaluate` endpoint: runs retrieval for each Q, reports recall@k and MRR.
  - **Commit:** `feat(ml): implement /evaluate with recall@k and MRR`
- **Day 45.** Faithfulness scoring via LLM judge prompt. Add to `/evaluate` output.
  - **Commit:** `feat(ml): add faithfulness scoring to evaluation harness`
- **Day 46.** Admin dashboard tile in gateway + frontend surfacing the latest evaluation run.
  - **Commit:** `feat(admin): surface evaluation metrics on admin dashboard`
- **Day 47.** Regression: track week-over-week metric deltas in a small `evaluation_runs` table.
  - **Commit:** `feat(ml): persist evaluation runs for regression tracking`

### Week 8 — Observability + rate limiting
- **Day 48.** Structured logging: Serilog (C# gateway) + `structlog` (Python ML). JSON output, correlation IDs.
  - **Commit:** `feat(observability): add structured logging across services`
- **Day 49.** Prometheus metrics from both services. `/metrics` scrape endpoints.
  - **Commit:** `feat(observability): expose Prometheus metrics`
- **Day 50.** OpenTelemetry tracing across services — gateway → ML calls show as one trace.
  - **Commit:** `feat(observability): add distributed tracing across services`
- **Day 51.** Rate limiting (ASP.NET built-in) per user on `/chat`, `/documents`, `/search`. Audit limit hits.
  - **Commit:** `feat(api): add per-user rate limiting on heavy endpoints`
- **Day 52.** Global exception handling + RFC 7807 problem-details on both services.
  - **Commit:** `feat(api,ml): standardise error responses on RFC 7807`
- **Day 53.** Health + readiness probes wired into Docker Compose `healthcheck` blocks.
  - **Commit:** `feat(infra): add health and readiness probes`
- **Day 54.** Backend test coverage push: target 70%+ on services and repositories.
  - **Commit:** `test: increase backend coverage to 70%+`

**🏁 Milestone:** `git tag v0.4-hardening` — evaluated, observable, rate-limited, and tested across both services.

---

## Phase 5 — Polish & Release (Weeks 9–10, buffer)

Catch-up time for anything that slipped, plus portfolio polish.

### Week 9 — Infra + docs
- **Day 55.** Finalise `docker-compose.yml`: all 5 services, healthchecks, `depends_on` conditions, volumes.
  - **Commit:** `chore(infra): finalise docker-compose with healthchecks and ordering`
- **Day 56.** Production Dockerfiles: multi-stage `dotnet publish` for gateway, slim Python image for ML, nginx for Next.js static.
  - **Commit:** `chore(infra): add multi-stage production Dockerfiles`
- **Day 57.** GitHub Actions CI: build, test, lint for C#, Python, and frontend on every push.
  - **Commit:** `ci: add GitHub Actions for all three services`
- **Day 58.** `docs/` cleanup: ensure architecture, API spec, RAG, schema all reflect the shipped system.
  - **Commit:** `docs: align all docs with shipped architecture`
- **Day 59.** README rewrite: screenshots, architecture diagram (Mermaid), badges, quick start.
  - **Commit:** `docs: rewrite README with screenshots and architecture diagram`

### Week 10 — Portfolio polish
- **Day 60.** Record a 60-second demo video. Link from README. Write resume bullet points.
  - **Commit:** `docs: add demo video and resume bullets`

Days 55–60 leave deliberate slack — if any prior phase ran over, absorb it here. Otherwise, use the spare days for:

- A short blog post on the dual-service architecture and the C# ↔ Python boundary.
- A README "What I'd do at scale" section: gRPC migration, separate vector DB, async ingest queue, multi-tenant data isolation.
- A short ADR for each pre-decided trade-off.

**🏁 Final Milestone:** `git tag v1.0` — shipped.

---

## Backup Tasks for Stuck Days

If you hit a blocker on any day, these are always valid commits to keep the streak alive:

| Task | Commit message |
|---|---|
| Add unit tests for existing code | `test: add unit tests for {component}` |
| Document a design decision in `docs/decisions/` | `docs: document {decision} ADR` |
| Refactor for clarity without behaviour change | `refactor: extract {component}` |
| Update README progress checklist | `docs: update roadmap progress` |
| Add inline code comments to complex logic | `docs: add inline documentation to {file}` |
| Improve `.env.example` documentation | `docs: clarify environment variables` |
| Add a small UX improvement (loading text, label) | `feat(ui): improve {component} affordance` |
| Bump a dependency | `chore: update {package} to {version}` |

---

## Daily Routine Suggestion

| Time | Activity |
|---|---|
| **0:00–0:15** | Review yesterday's commit, plan today's task |
| **0:15–2:00** | Focused development |
| **2:00–2:30** | Write tests for what you built |
| **2:30–2:45** | Commit with proper Conventional Commits message |
| **2:45–3:00** | Push to GitHub, update progress checklist in README |

---

## Weekly Checkpoints

At the end of each week, do a self-review:

- **End of Week 2 (Day 14):** Python ML service answers a question over a real PDF from curl, end-to-end, with citations.
- **End of Week 4 (Day 28):** Gateway exposes auth + chat orchestration via Swagger; integration tests pass against Testcontainers.
- **End of Week 6 (Day 42):** Non-technical person can log in, upload a document, and chat with streamed answers + citations.
- **End of Week 8 (Day 54):** `/evaluate` reports recall@k, MRR, and faithfulness; traces cross both services in your observability stack.
- **End of Week 10 (Day 60):** Ship it. README is portfolio-quality. Demo video recorded. Resume bullets written.

---

## Definition of Done for the 60 Days

- [ ] 60 consecutive days of commits on `main` (or merged feature branches)
- [ ] All 5 phases complete with milestone tags (`v0.1` through `v1.0`)
- [ ] `docker compose up` brings up the full 5-service stack with zero errors
- [ ] README is portfolio-quality with screenshots and demo
- [ ] At least 70% test coverage on backend services
- [ ] GitHub Actions CI passes on `main`
- [ ] `/evaluate` reports baseline retrieval and faithfulness metrics
- [ ] Resume bullet points written and saved
- [ ] Ready to link in your Intel application
