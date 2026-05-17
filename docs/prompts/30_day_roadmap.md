# 30-Day Development Roadmap — AI Engineering Copilot

> **Goal:** Build the AI Engineering Copilot project with consistent daily commits across 30 days.
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

| Phase | Days | Focus |
|---|---|---|
| **Phase 0** | 1–2 | Repository setup and planning | ✅
| **Phase 1** | 3–8 | Backend foundation + authentication |
| **Phase 2** | 9–14 | Document upload + processing pipeline |
| **Phase 3** | 15–20 | RAG pipeline + AI chat |
| **Phase 4** | 21–25 | Frontend |
| **Phase 5** | 26–28 | Admin dashboard + observability |
| **Phase 6** | 29–30 | Polish, README, deployment |

---

## Phase 0 — Repository Setup (Days 1–2)

### Day 1 — Initialize repo
- Run the Git repo setup prompt
- Create folder structure, `.gitignore`, `.editorconfig`, `.env.example`
- Push initial commit to GitHub
- **Commit:** `chore: initialize repository structure`

### Day 2 — Documentation foundation
- Write `docs/architecture.md` with high-level architecture diagram (ASCII or Mermaid)
- Draft `docs/database-schema.md` with all 9 tables and relationships
- Draft `docs/api-spec.md` skeleton with endpoint list
- **Commit:** `docs: add architecture, schema, and API specification drafts`

---

## Phase 1 — Backend Foundation + Auth (Days 3–8)

### Day 3 — ASP.NET Core scaffolding
- Create solution: `dotnet new sln -n AiEngineeringCopilot`
- Create projects: `Api`, `Core` (domain), `Infrastructure` (EF Core, repos), `Application` (services)
- Wire up project references following Clean Architecture
- Configure Swagger
- **Commit:** `feat(backend): scaffold clean architecture solution with Swagger`

### Day 4 — PostgreSQL + EF Core
- Add `Npgsql.EntityFrameworkCore.PostgreSQL` and `Pgvector.EntityFrameworkCore`
- Create `AppDbContext` with `users` and `roles` entities
- Generate first migration
- Add `docker-compose.yml` PostgreSQL service and verify connection
- **Commit:** `feat(backend): configure EF Core with PostgreSQL and pgvector`

### Day 5 — User entity + repository pattern
- Implement `User` and `Role` entities with proper constraints
- Create `IUserRepository` and `UserRepository` with async methods
- Add `IUnitOfWork` pattern
- Write unit tests for `UserRepository`
- **Commit:** `feat(backend): implement user repository with unit tests`

### Day 6 — JWT authentication
- Add `Microsoft.AspNetCore.Authentication.JwtBearer`
- Implement `IJwtService` (token generation + validation)
- Configure JWT in `Program.cs` with options from `appsettings.json`
- Add `[Authorize]` test endpoint
- **Commit:** `feat(auth): implement JWT token generation and validation`

### Day 7 — Auth endpoints
- Build `AuthController` with `POST /api/auth/register` and `POST /api/auth/login`
- Add password hashing (BCrypt.Net-Next or ASP.NET Core Identity hasher)
- Add FluentValidation for register/login DTOs
- Write integration tests for both endpoints
- **Commit:** `feat(auth): add register and login endpoints with validation`

### Day 8 — Middleware + error handling
- Add global exception handling middleware
- Add request logging middleware (Serilog)
- Configure structured logging with JSON output
- Add rate limiting to auth endpoints
- **Commit:** `feat(backend): add global exception handling and structured logging`

**🏁 Milestone:** `git tag v0.1-auth`

---

## Phase 2 — Document Upload + Processing (Days 9–14)

### Day 9 — Document entity + storage
- Create `Document`, `DocumentChunk`, `ProcessingJob` entities
- Add migration for document tables
- Implement `IDocumentRepository`
- Create local file storage abstraction (`IFileStorageService`)
- **Commit:** `feat(documents): add document entities and file storage abstraction`

### Day 10 — Upload endpoint
- Build `DocumentsController` with `POST /api/documents/upload`
- Validate file type (PDF, DOCX, TXT) and size limits
- Store file, create `Document` record, return metadata
- Add duplicate detection (SHA-256 hash check)
- **Commit:** `feat(documents): implement upload endpoint with duplicate detection`

### Day 11 — Text extraction
- Add `PdfPig` (PDF), `DocumentFormat.OpenXml` (DOCX), plain text reader
- Implement `ITextExtractionService` with strategy pattern per file type
- Write unit tests with sample documents in `tests/fixtures/`
- **Commit:** `feat(documents): add multi-format text extraction service`

### Day 12 — Chunking strategy
- Implement `IChunkingService` with configurable chunk size and overlap
- Support document-type-aware chunking (paragraphs for prose, sections for technical docs)
- Persist chunks to `document_chunks` table
- Write unit tests covering edge cases (empty, single-chunk, huge documents)
- **Commit:** `feat(rag): implement document chunking with configurable overlap`

### Day 13 — Background worker
- Add `BackgroundService` for document processing
- Implement job queue using `processing_jobs` table
- Add Polly retry policies for transient failures
- Add status tracking (pending → processing → completed/failed)
- **Commit:** `feat(backend): add background worker for async document processing`

### Day 14 — Document listing + management
- Add `GET /api/documents` with keyset pagination
- Add `GET /api/documents/{id}` for details
- Add `DELETE /api/documents/{id}` (soft delete)
- Write integration tests for full upload → process → list flow
- **Commit:** `feat(documents): add listing, detail, and delete endpoints`

**🏁 Milestone:** `git tag v0.2-documents`

---

## Phase 3 — RAG Pipeline + AI Chat (Days 15–20)

### Day 15 — Ollama integration
- Add Ollama service to `docker-compose.yml`
- Create `IOllamaClient` using `Microsoft.Extensions.Http.Resilience`
- Implement embedding generation method
- Test against running Ollama instance with `nomic-embed-text`
- **Commit:** `feat(ai): integrate Ollama client with resilient HTTP`

### Day 16 — Embedding storage with pgvector
- Add `Embedding` entity with `vector(768)` column
- Update background worker: after chunking → generate embeddings → store
- Add IVFFlat index on embedding column
- Verify embeddings persist correctly
- **Commit:** `feat(rag): generate and store chunk embeddings with pgvector`

### Day 17 — Semantic search endpoint
- Implement `IVectorSearchService` with cosine similarity query
- Add `POST /api/search` taking query + top-k parameter
- Return matching chunks with similarity scores and document references
- Write integration test with seeded data
- **Commit:** `feat(rag): implement semantic search with top-k retrieval`

### Day 18 — Chat session model
- Create `ChatSession` and `ChatMessage` entities
- Add `POST /api/chat/sessions` to create session
- Add `GET /api/chat/sessions` and `GET /api/chat/sessions/{id}/messages`
- Persist all messages with role (user/assistant) and timestamps
- **Commit:** `feat(chat): add chat session and message persistence`

### Day 19 — RAG-powered chat endpoint
- Implement `IRagOrchestrator` service
- Build pipeline: query → embed → retrieve top-k → construct prompt → call Ollama LLM
- Add `POST /api/chat/sessions/{id}/messages` returning AI response
- Include citation metadata linking to source chunks
- **Commit:** `feat(rag): implement full RAG chat orchestration with citations`

### Day 20 — Hybrid search + prompt refinement
- Add keyword filter alongside vector similarity
- Implement hybrid retrieval (vector + BM25-style keyword scoring)
- Refine system prompt with grounding instructions to reduce hallucination
- Write tests covering retrieval accuracy on known documents
- **Commit:** `feat(rag): add hybrid search and improved grounding prompts`

**🏁 Milestone:** `git tag v0.3-rag`

---

## Phase 4 — Frontend (Days 21–25)

### Day 21 — React scaffolding
- Run `npm create vite@latest frontend -- --template react`
- Install Tailwind CSS, Axios, TanStack Query, React Router
- Configure Tailwind, create base layout
- Set up Axios instance with auth interceptor
- **Commit:** `feat(frontend): scaffold React app with Tailwind and TanStack Query`

### Day 22 — Auth pages
- Build Login and Register pages
- Implement auth context with JWT storage (httpOnly cookie or localStorage)
- Add protected route wrapper
- Add form validation and error states
- **Commit:** `feat(frontend): implement login, register, and protected routes`

### Day 23 — Document upload page
- Build drag-and-drop upload component
- Show upload progress and processing status
- List existing documents with pagination
- Add delete confirmation modal
- **Commit:** `feat(frontend): add document upload and management page`

### Day 24 — Chat interface
- Build chat layout (sidebar with sessions, main panel with messages)
- Implement message streaming display (typewriter or chunk-based)
- Show citations as clickable references opening source chunks
- Add new session and session history
- **Commit:** `feat(frontend): implement chat interface with citations`

### Day 25 — Polish + UX
- Add loading skeletons, empty states, error boundaries
- Add toast notifications (success/error)
- Make responsive (mobile-friendly chat)
- Run accessibility audit (keyboard nav, focus states)
- **Commit:** `feat(frontend): add loading states, toasts, and responsive layout`

**🏁 Milestone:** `git tag v0.4-frontend`

---

## Phase 5 — Admin Dashboard + Observability (Days 26–28)

### Day 26 — Admin endpoints
- Add `[Authorize(Roles = "Admin")]` to admin routes
- `GET /api/admin/metrics` (document count, embedding count, jobs by status)
- `GET /api/admin/jobs` with filtering by status
- `POST /api/admin/jobs/{id}/retry` to reprocess failed jobs
- **Commit:** `feat(admin): add admin metrics and job management endpoints`

### Day 27 — Admin dashboard page
- Build dashboard with metric cards and charts (Recharts)
- Add jobs table with status filters and retry action
- Show real-time updates via polling (TanStack Query refetch interval)
- **Commit:** `feat(admin): implement admin dashboard with metrics and job table`

### Day 28 — Observability
- Add OpenTelemetry instrumentation (traces, metrics)
- Add Seq container to `docker-compose.yml` for log viewing
- Add health check endpoints (`/health`, `/health/ready`)
- Document observability setup in `docs/observability.md`
- **Commit:** `feat(observability): add OpenTelemetry and health checks`

**🏁 Milestone:** `git tag v0.5-admin`

---

## Phase 6 — Polish + Release (Days 29–30)

### Day 29 — Testing + CI
- Increase test coverage to 70%+ on services and repositories
- Add GitHub Actions workflow: build, test, and lint on push
- Add Dockerfile for production frontend build (multi-stage with nginx)
- Add Dockerfile for production backend (multi-stage with `dotnet publish`)
- **Commit:** `test: improve coverage and add GitHub Actions CI pipeline`

### Day 30 — README + portfolio polish
- Rewrite README with screenshots, architecture diagram, and demo GIF
- Record a 60-second demo video, link from README
- Update `docs/` with final API spec, RAG design, and lessons learned
- Add resume bullet points to `docs/resume-bullets.md`
- Final commit with version tag
- **Commit:** `docs: finalize README with screenshots and demo`

**🏁 Final Milestone:** `git tag v1.0`

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

- **End of Week 1 (Day 7):** Auth working end-to-end. Can you register, log in, and hit a protected endpoint?
- **End of Week 2 (Day 14):** Upload working. Can you upload a PDF and see chunks in the database?
- **End of Week 3 (Day 21):** RAG working. Can you ask a question and get a grounded answer with citations?
- **End of Week 4 (Day 28):** Full stack working. Can a non-technical person use the app via the UI?
- **End of Day 30:** Ship it. Is it on GitHub with a great README?

---

## Definition of Done for the 30 Days

- [ ] 30 consecutive days of commits on `main` (or merged feature branches)
- [ ] All 6 phases complete with milestone tags (`v0.1` through `v1.0`)
- [ ] `docker compose up` brings up the full stack with zero errors
- [ ] README is portfolio-quality with screenshots and demo
- [ ] At least 70% test coverage on backend services
- [ ] GitHub Actions CI passes on `main`
- [ ] Resume bullet points written and saved
- [ ] Ready to link in your Intel application
