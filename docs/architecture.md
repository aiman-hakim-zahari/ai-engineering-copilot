# Architecture

System design and component decisions for the AI Engineering Copilot.

## Goals

- Local-first: full stack runs offline via Docker Compose with no third-party API keys.
- Citable answers: every LLM response must include source document references.
- Composable: backend, frontend, vector store, and LLM provider are independent services.

## Components

| Component       | Role                                                                          |
|-----------------|-------------------------------------------------------------------------------|
| Frontend (React)| Document upload UI, chat interface, admin dashboard                           |
| Backend (.NET 8)| REST API, auth, document parsing, chunking, embedding orchestration, RAG     |
| PostgreSQL      | Relational state + `pgvector` extension for embedding storage and search     |
| Ollama          | Local model server for embeddings (`nomic-embed-text`) and chat (`llama3`)   |

## Data Flow

1. User uploads a document via the frontend.
2. Backend parses (PDF/DOCX/TXT) → splits into chunks → requests embeddings from Ollama.
3. Chunks + embeddings + metadata are persisted to PostgreSQL.
4. On a chat query: backend embeds the question, performs hybrid search (vector + BM25),
   constructs a prompt with top-k chunks, and streams the LLM response to the client
   with citation anchors.

## Key Decisions (ADR-style)

_Filled in as decisions are made. See `docs/rag-pipeline.md` for retrieval/generation details
and `docs/database-schema.md` for the relational + vector schema._
