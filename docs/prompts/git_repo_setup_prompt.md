# Git Repository Setup — AI Engineering Copilot

> **Run this before writing any code.**
> A clean repo structure signals professional engineering discipline to any hiring manager who browses your GitHub.

---

## Prompt

You are a senior software engineer setting up a professional GitHub repository for a portfolio project.

The project is an **AI Engineering Copilot** — a dual-language microservice document intelligence platform built with Next.js (TypeScript) frontend, an ASP.NET Core 8 (C#) API gateway, a Python FastAPI ML service, PostgreSQL + pgvector, and Ollama (pluggable to OpenAI / Anthropic).

Set up the Git repository from scratch following enterprise SDLC best practices. The repository must be ready for development immediately after setup, with no placeholder files and no loose ends.

---

## Repository Details

| Field | Value |
|---|---|
| **Repo name** | `ai-engineering-copilot` |
| **Visibility** | Public (portfolio) |
| **Primary languages** | C# (gateway), Python (ML service), TypeScript (frontend) |
| **License** | MIT |

---

## Tasks to Complete

### 1. Initialize the Repository

```bash
git init ai-engineering-copilot
cd ai-engineering-copilot
git branch -M main
```

### 2. Create the Top-Level Folder Structure

Generate the following structure before any code is written:

```
ai-engineering-copilot/
├── src/
│   ├── api/                      # ASP.NET Core gateway (C#)
│   ├── ml/                       # Python FastAPI ML service
│   └── frontend/                 # Next.js application (TypeScript)
├── tests/
│   ├── unit/                     # xUnit (C#) + pytest (Python) unit tests
│   ├── ml/                       # Python ML pipeline tests + fixtures
│   └── integration/              # cross-service integration tests
├── docs/
│   ├── architecture.md           # Architecture decisions and diagrams
│   ├── api-spec.md               # REST API endpoint reference (gateway + ML)
│   ├── rag-pipeline.md           # RAG pipeline design notes
│   └── database-schema.md        # SQL schema documentation
├── scripts/
│   ├── setup.sh                  # First-time local setup script
│   ├── seed.sh                   # Database seed script
│   └── reset-db.sh               # Drop and recreate database
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── docker-compose.yml            # Full local stack (5 services)
├── docker-compose.override.yml   # Dev overrides (hot reload, debug ports)
├── .env.example                  # Environment variable template
├── .gitignore
├── .editorconfig
├── LICENSE
└── README.md
```

### 3. Generate a Comprehensive `.gitignore`

Combine rules for:

- **C# / .NET:** `bin/`, `obj/`, `*.user`, `*.suo`, `.vs/`, `appsettings.Development.json`
- **Python:** `__pycache__/`, `*.pyc`, `*.pyo`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `*.egg-info/`
- **Next.js / Node:** `node_modules/`, `.next/`, `dist/`, `out/`, `.env.local`, `.env.*.local`, `npm-debug.log*`
- **Docker:** `.docker/`
- **IDE:** `.idea/`, `.vscode/` (keep `.vscode/extensions.json` and `.vscode/settings.json` for team consistency)
- **OS:** `.DS_Store`, `Thumbs.db`
- **Secrets:** `*.pem`, `*.key`, `*.pfx`, `secrets.json`
- **Uploads / generated:** `uploads/`, `*.log`, `ollama-models/`

### 4. Create `.editorconfig`

Enforce consistent formatting across C#, Python, and TypeScript:

```ini
root = true

[*]
indent_style = space
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.cs]
indent_size = 4

[*.py]
indent_size = 4

[*.{js,jsx,json,ts,tsx}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

### 5. Create `.env.example`

Document every required environment variable. **Never commit real values.**

```env
# PostgreSQL (shared by gateway and ML service)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ai_copilot
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password

# ASP.NET Core gateway
ASPNETCORE_ENVIRONMENT=Development
JWT_SECRET=your_jwt_secret_minimum_32_characters
JWT_ISSUER=ai-engineering-copilot
JWT_AUDIENCE=ai-engineering-copilot-client
JWT_EXPIRY_MINUTES=60
API_PORT=5000
ALLOWED_ORIGINS=http://localhost:3000

# Python ML service
ML_SERVICE_PORT=8001
ML_SERVICE_URL=http://ml:8001
ML_INTERNAL_TOKEN=your_shared_internal_service_token

# LLM provider (Ollama default; cloud keys optional)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_CHAT_MODEL=llama3
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Frontend (Next.js)
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

### 6. Create `docker-compose.yml` Skeleton

Set up the full local stack with correct service names, ports, and dependency ordering. Leave image/build context as placeholders to be filled during implementation.

```yaml
version: "3.9"

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: copilot_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    container_name: copilot_ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434"]
      interval: 15s
      timeout: 10s
      retries: 5

  ml:
    build:
      context: ./src/ml
      dockerfile: Dockerfile
    container_name: copilot_ml
    env_file: .env
    ports:
      - "${ML_SERVICE_PORT}:8001"
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/healthz"]
      interval: 15s
      timeout: 10s
      retries: 5

  api:
    build:
      context: ./src/api
      dockerfile: Dockerfile
    container_name: copilot_api
    env_file: .env
    ports:
      - "${API_PORT}:8080"
    depends_on:
      postgres:
        condition: service_healthy
      ml:
        condition: service_healthy
    volumes:
      - uploads:/app/uploads

  frontend:
    build:
      context: ./src/frontend
      dockerfile: Dockerfile
    container_name: copilot_frontend
    env_file: .env
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
  ollama_models:
  uploads:
```

### 7. Write the `README.md`

The README must be portfolio-quality. Include:

```markdown
# AI Engineering Copilot

> AI-powered document intelligence platform — upload engineering documents,
> ask questions, and receive contextual answers with source citations.

## Tech Stack
[badges for .NET 8, C#, Next.js, TypeScript, Python, FastAPI, PostgreSQL, Docker, Ollama]

## Features
- Document upload and parsing (PDF, DOCX, TXT)
- RAG-based Q&A with source citations
- Semantic + hybrid search via pgvector
- JWT authentication with role-based access
- Admin dashboard with processing metrics
- Fully containerized with Docker Compose (5 services)

## Architecture
Dual-language microservice architecture:
- **Frontend (Next.js + TypeScript)** — chat UI, document upload, auth pages.
- **API Gateway (ASP.NET Core, C#)** — auth, RBAC, document metadata via EF Core, conversation history, orchestration, audit, rate limiting. Persists to PostgreSQL.
- **ML Service (Python + FastAPI)** — chunking, embedding, vector search, reranking, prompt construction, LLM inference, evaluation. Reads/writes pgvector.
- **Inter-service:** REST over HTTP (JSON). Rationale: simplicity, debuggability, adequacy at expected scale. Migration path: gRPC or OpenAPI codegen.
- **Data layer:** PostgreSQL + pgvector (shared).
- **LLM backend:** Ollama local (default); pluggable to OpenAI / Anthropic.

[link to docs/architecture.md]

## Quick Start
### Prerequisites
- Docker and Docker Compose
- Git

### Setup
git clone https://github.com/YOUR_USERNAME/ai-engineering-copilot.git
cd ai-engineering-copilot
cp .env.example .env
# Edit .env with your values
docker compose up --build

## API Reference
[link to docs/api-spec.md]

## Project Structure
[folder tree]

## Development Roadmap
60-day plan — see docs/prompts/60_day_roadmap.md.
- [x] Phase 0: Repository setup
- [ ] Weeks 1–2: Python ML service end-to-end
- [ ] Weeks 3–4: ASP.NET Core gateway
- [ ] Weeks 5–6: Next.js chat UI
- [ ] Weeks 7–8: Evaluation harness + production hardening
- [ ] Weeks 9–10 (buffer): Docker Compose, README, demo

## License
MIT
```

### 8. Create GitHub Issue Templates

**`.github/ISSUE_TEMPLATE/bug_report.md`**
```markdown
---
name: Bug Report
about: Report a reproducible bug
labels: bug
---

## Description
<!-- Clear description of the bug -->

## Steps to Reproduce
1.
2.
3.

## Expected Behavior

## Actual Behavior

## Environment
- OS:
- Docker version:
- Browser (if frontend):
```

**`.github/ISSUE_TEMPLATE/feature_request.md`**
```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
labels: enhancement
---

## Problem Statement
<!-- What problem does this solve? -->

## Proposed Solution

## Acceptance Criteria
- [ ]
- [ ]

## Additional Context
```

**`.github/PULL_REQUEST_TEMPLATE.md`**
```markdown
## Summary
<!-- What does this PR do? -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Documentation

## Checklist
- [ ] Code follows project conventions
- [ ] Tests added or updated
- [ ] No secrets or credentials committed
- [ ] README updated if needed

## Related Issues
Closes #
```

### 9. Set Up Git Branching Strategy

Use **GitHub Flow** (simple, appropriate for a solo portfolio project):

```
main          ← always deployable, protected
└── feature/auth-jwt
└── feature/document-upload
└── feature/rag-pipeline
└── feature/chat-interface
└── feature/admin-dashboard
└── fix/embedding-timeout
```

**Branch naming convention:**
- `feature/<short-description>` — new functionality
- `fix/<short-description>` — bug fixes
- `chore/<short-description>` — tooling, config, docs
- `refactor/<short-description>` — code improvements without behaviour change

### 10. Make the Initial Commit

```bash
git add .
git commit -m "chore: initialize repository structure

- Add top-level folder structure (src/api, src/ml, src/frontend, tests, docs, scripts)
- Add .gitignore for C#, Python, Next.js / Node, Docker, and OS artifacts
- Add .editorconfig for consistent formatting (C#, Python, TypeScript)
- Add .env.example with all required environment variables
- Add docker-compose.yml skeleton with 5 services and health checks
- Add README.md with project overview and quick start
- Add GitHub issue and PR templates
- Add MIT license"

git remote add origin https://github.com/YOUR_USERNAME/ai-engineering-copilot.git
git push -u origin main
```

---

## Commit Message Convention

Follow **Conventional Commits** throughout the project:

| Prefix | Use for |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `chore:` | Tooling, config, dependencies |
| `refactor:` | Code restructure, no behaviour change |
| `docs:` | Documentation only |
| `test:` | Adding or updating tests |
| `perf:` | Performance improvement |

**Examples:**
```
feat: add JWT authentication middleware
fix: resolve embedding timeout on large documents
chore: add Docker health checks to compose file
docs: document RAG pipeline design in docs/rag-pipeline.md
test: add unit tests for document chunking service
```

---

## Output Required

Provide:

1. The complete `.gitignore` file content
2. The complete `.editorconfig` file content
3. The complete `.env.example` file content
4. The complete `docker-compose.yml` skeleton
5. The complete `README.md` (portfolio-ready, not placeholder)
6. All GitHub issue and PR templates
7. The exact sequence of shell commands to run, in order, to initialize the repo locally and push to GitHub
8. A checklist to verify the repo is correctly set up before writing the first line of application code

---

## Definition of Done

The repository setup is complete when:

- [ ] Repo is initialized on GitHub with `main` as the default branch
- [ ] All folders exist with `.gitkeep` where needed to preserve empty dirs
- [ ] `.gitignore` excludes all build artifacts, secrets, and OS files
- [ ] `.env.example` documents every variable with no real values committed
- [ ] `docker-compose.yml` skeleton runs without errors (`docker compose config` passes)
- [ ] README renders correctly on GitHub with no broken links
- [ ] Initial commit message follows Conventional Commits format
- [ ] `main` branch has at least one commit and is pushed to remote
