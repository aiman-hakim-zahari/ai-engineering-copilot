# RAG Pipeline

The current RAG flow is intentionally simple and local-first.

## Ingestion

1. The gateway sends raw text and a source name to `POST /ingest`.
2. The ML service splits text into overlapping chunks of about 120 words.
3. Chunks are stored in a process-local Python list.

## Retrieval

1. `POST /answer` tokenizes the question.
2. Each chunk is scored by keyword overlap, coverage, and density.
3. The top chunks are returned as `matched_chunks` and `sources`.

## Answering

By default, the service builds an extractive answer from the best matching
chunks. If `OLLAMA_BASE_URL` is configured, it tries a local Ollama generation
request and falls back to the extractive answer if Ollama is unavailable.

## Limitations

- No embeddings yet
- No pgvector persistence yet
- No reranker yet
- No evaluation endpoint yet
- No streaming responses yet
