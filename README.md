# AI Engineering Copilot

A compact full-stack portfolio demo for document Q&A.

The project intentionally implements one honest vertical slice: a Next.js UI sends
document text and questions to an ASP.NET Core gateway, which forwards the work
to a Python FastAPI service. The Python service chunks documents in memory,
retrieves matching chunks with keyword scoring, and returns an answer with
source chunks.

No auth, roles, admin dashboard, streaming, paid APIs, or database setup is
required for the current demo.

## Architecture

```text
Next.js frontend
        |
        v
ASP.NET Core API gateway
        |
        v
Python FastAPI ML/RAG service
        |
        v
In-memory chunks
```

PostgreSQL with pgvector and local LLM generation are good future improvements,
but the demo works without them.

## What Is Implemented

- Next.js App Router frontend with TypeScript
- Document text input and `.txt` / `.md` upload in the browser
- Chat/question form with loading and error states
- Source chunk display
- ASP.NET Core gateway endpoints:
  - `GET /health`
  - `POST /documents`
  - `POST /chat`
- Swagger for the gateway at `http://localhost:5000/swagger`
- FastAPI ML service endpoints:
  - `GET /healthz`
  - `POST /ingest`
  - `POST /answer`
- FastAPI docs at `http://localhost:8001/docs`
- In-memory chunk storage and lightweight keyword retrieval
- Optional Ollama answer generation when configured, with extractive fallback

## Demo Flow

```text
Open the Next.js UI
-> paste or upload a short engineering document
-> click "Index document"
-> ask a question
-> frontend calls ASP.NET Core /chat
-> gateway calls FastAPI /answer
-> FastAPI returns answer + matched chunks
-> frontend displays answer and sources
```

## Run With Docker Compose

Prerequisites: Docker and Docker Compose v2.

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Frontend: `http://localhost:3000`
- Gateway Swagger: `http://localhost:5000/swagger`
- FastAPI docs: `http://localhost:8001/docs`

Docker Compose starts three services: `frontend`, `backend`, and `ml`.

## Run Locally Without Docker

Start the ML service:

```bash
cd src/ml
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

Start the ASP.NET Core gateway:

```bash
cd src/backend
dotnet run --urls http://localhost:5000
```

Start the frontend:

```bash
cd src/frontend
npm install
npm run dev
```

If ports differ, set:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
ML_SERVICE_BASE_URL=http://localhost:8001
ALLOWED_ORIGINS=http://localhost:3000
```

## API Shape

### Gateway

`POST /documents`

```json
{
  "source": "architecture-note.md",
  "text": "The gateway is ASP.NET Core and the ML service is FastAPI."
}
```

`POST /chat`

```json
{
  "question": "What is the gateway built with?",
  "topK": 4
}
```

### ML service

`POST /ingest`

```json
{
  "source": "architecture-note.md",
  "text": "The gateway is ASP.NET Core and the ML service is FastAPI."
}
```

`POST /answer`

```json
{
  "question": "What is the gateway built with?",
  "top_k": 4
}
```

## Project Structure

```text
src/
  frontend/   Next.js TypeScript UI
  backend/    ASP.NET Core gateway
  ml/         Python FastAPI RAG service
docs/         Notes for the implemented slice and future direction
```

## Intentionally Out Of Scope

- Authentication and JWTs
- Role-based access control
- Admin dashboards
- Conversation persistence
- PostgreSQL / pgvector persistence
- Advanced embeddings, reranking, and evaluation
- Streaming responses
- Production observability

## Future Improvements

- Persist documents and chunks in PostgreSQL with pgvector
- Add embeddings and hybrid search
- Add optional Ollama/OpenAI providers behind a clear interface
- Save conversations and source metadata
- Add evaluation fixtures for retrieval quality
- Add integration and end-to-end tests
