# RAG Pipeline

Design notes for the retrieval-augmented generation flow.

> **Service boundary.** The entire pipeline runs in the **Python ML service** (FastAPI). The C# gateway invokes it via `POST /answer` (end-to-end) or finer-grained endpoints (`/ingest`, `/embed`, `/retrieve`, `/rerank`). The gateway persists the inputs and outputs; the ML service does the math. See [architecture.md](architecture.md) and [api-spec.md](api-spec.md#ml-service-api-internal).

## Ingestion

1. **Parse** — PDF (`pypdf`), DOCX (`python-docx`), TXT (raw).
2. **Chunk** — recursive character splitter (`langchain-text-splitters` or in-house equivalent); target ~800 tokens with 100-token overlap. Token counts via `tiktoken`.
3. **Embed** — Ollama `nomic-embed-text` (768-dim) by default; pluggable to OpenAI / Anthropic embedding models via a single client interface.
4. **Persist** — `chunks` row written with `embedding vector(768)`, `document_id`, `page`, `text`. Idempotent on `(document_id, chunk_index)`.

## Retrieval

- **Vector search** — cosine similarity over `pgvector` HNSW index, top-k = 20.
- **Lexical search** — PostgreSQL full-text (`tsvector`), top-k = 20.
- **Fusion** — Reciprocal Rank Fusion (RRF) merges both rankings.
- **Rerank** — cross-encoder reranker (e.g. `BAAI/bge-reranker-base` via `sentence-transformers`) scores the fused top-N down to top-k = 8.

## Generation

- Prompt template constrains the model to cite by `[doc:id#chunk]` markers and to refuse when retrieval is empty or low-confidence.
- LLM call via Ollama by default; same interface routes to OpenAI / Anthropic when configured.
- Streamed back to the gateway, which streams to the frontend via SSE.
- Post-processing maps citation markers back to document + page anchors before the response is persisted to `messages.sources`.

## Evaluation (Weeks 7–8)

- Golden dataset of **20–30 Q/A pairs** covering the demo corpus, checked into the repo.
- Exposed via the ML service's `POST /evaluate` endpoint.
- Reports:
  - **recall@k** — was the gold chunk in the top-k retrieval?
  - **MRR** — mean reciprocal rank of the gold chunk.
  - **faithfulness** — does the answer cite only retrieved chunks, and do its claims appear in those chunks? Scored with an LLM judge prompt.
- The gateway exposes `/admin/metrics` to surface the latest evaluation run for the admin dashboard.
