# RAG Pipeline

Design notes for the retrieval-augmented generation flow.

## Ingestion

1. **Parse** — PDF (`PdfPig`), DOCX (`OpenXml`), TXT (raw).
2. **Chunk** — recursive character splitter; target ~800 tokens with 100-token overlap.
3. **Embed** — Ollama `nomic-embed-text` (768-dim).
4. **Persist** — `chunks` row with `embedding vector(768)`, `document_id`, `page`, `text`.

## Retrieval

- **Vector search** — cosine similarity over `pgvector` HNSW index, top-k = 20.
- **Lexical search** — PostgreSQL full-text (`tsvector`), top-k = 20.
- **Fusion** — Reciprocal Rank Fusion (RRF) merges both rankings, takes top-k = 8.

## Generation

- Prompt template constrains the model to cite by `[doc:id#chunk]` markers.
- Streamed via SSE to the frontend.
- Post-processing maps citation markers back to document + page anchors.

## Evaluation (Phase 2+)

- Manual eval set of ~30 Q/A pairs per domain.
- Track: retrieval@k, answer faithfulness, citation correctness.
