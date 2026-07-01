"""FastAPI application for the demo ML/RAG service."""

from __future__ import annotations

import json
import math
import os
import re
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app import __version__

app = FastAPI(
    title="AI Engineering Copilot - ML Service",
    description=(
        "Small demo service for document ingestion, keyword retrieval, and grounded "
        "answers. It stores chunks in memory so the portfolio slice runs without "
        "PostgreSQL, pgvector, Ollama, or paid API keys."
    ),
    version=__version__,
)

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9+#._-]*")
MAX_CHUNK_WORDS = 120
CHUNK_OVERLAP_WORDS = 24


@dataclass
class StoredChunk:
    """A single in-memory text chunk."""

    id: str
    document_id: str
    source: str
    text: str
    tokens: Counter[str]


DOCUMENT_IDS_BY_SOURCE: dict[str, str] = {}
CHUNKS: list[StoredChunk] = []


class HealthResponse(BaseModel):
    """Liveness payload returned by /healthz."""

    status: str
    service: str
    version: str


class IngestRequest(BaseModel):
    """Raw document text accepted from the ASP.NET Core gateway."""

    text: str = Field(min_length=1)
    source: str = Field(default="document", min_length=1)


class IngestResponse(BaseModel):
    """Summary of chunks indexed for a document."""

    document_id: str
    chunks_indexed: int
    sources: list[str]


class AnswerRequest(BaseModel):
    """Question payload for retrieval and answer generation."""

    question: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=8)


class Source(BaseModel):
    """Citation metadata for a retrieved chunk."""

    source: str
    chunk_id: str
    score: float


class MatchedChunk(Source):
    """Retrieved chunk with text for source display."""

    text: str


class AnswerResponse(BaseModel):
    """Grounded answer payload returned to the gateway."""

    answer: str
    sources: list[Source]
    matched_chunks: list[MatchedChunk]


@app.get("/healthz", response_model=HealthResponse, tags=["ops"])
def healthz() -> HealthResponse:
    """Liveness probe."""

    return HealthResponse(status="ok", service="ml", version=__version__)


@app.post("/ingest", response_model=IngestResponse, tags=["rag"])
def ingest(request: IngestRequest) -> IngestResponse:
    """Chunk and store document text in memory."""

    source = request.source.strip() or "document"
    document_id = str(uuid4())
    DOCUMENT_IDS_BY_SOURCE[source] = document_id

    chunks = chunk_text(request.text)
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = f"{document_id[:8]}-{index}"
        CHUNKS.append(
            StoredChunk(
                id=chunk_id,
                document_id=document_id,
                source=source,
                text=chunk,
                tokens=Counter(tokenize(chunk)),
            )
        )

    return IngestResponse(document_id=document_id, chunks_indexed=len(chunks), sources=[source])


@app.post("/answer", response_model=AnswerResponse, tags=["rag"])
def answer(request: AnswerRequest) -> AnswerResponse:
    """Retrieve matching chunks and produce a grounded answer."""

    question = request.question.strip()
    matches = retrieve(question, request.top_k)
    matched_chunks = [
        MatchedChunk(source=chunk.source, chunk_id=chunk.id, score=score, text=chunk.text)
        for chunk, score in matches
    ]
    sources = [
        Source(source=chunk.source, chunk_id=chunk.id, score=score)
        for chunk, score in matches
    ]

    generated = maybe_generate_with_ollama(question, matched_chunks)
    answer_text = generated or build_extractive_answer(question, matched_chunks)

    return AnswerResponse(answer=answer_text, sources=sources, matched_chunks=matched_chunks)


def chunk_text(text: str) -> list[str]:
    """Split text into small overlapping chunks."""

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = MAX_CHUNK_WORDS - CHUNK_OVERLAP_WORDS
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + MAX_CHUNK_WORDS]).strip()
        if chunk:
            chunks.append(chunk)
        if start + MAX_CHUNK_WORDS >= len(words):
            break

    return chunks


def retrieve(question: str, top_k: int) -> list[tuple[StoredChunk, float]]:
    """Rank chunks with simple lexical matching."""

    if not CHUNKS:
        return []

    query_terms = Counter(tokenize(question))
    if not query_terms:
        return [(chunk, 0.0) for chunk in CHUNKS[:top_k]]

    scored = [(chunk, score_chunk(chunk, query_terms)) for chunk in CHUNKS]
    scored.sort(key=lambda item: item[1], reverse=True)

    positive_matches = [item for item in scored if item[1] > 0]
    return (positive_matches or scored)[:top_k]


def score_chunk(chunk: StoredChunk, query_terms: Counter[str]) -> float:
    """Score a chunk using overlap, coverage, and term density."""

    query_set = set(query_terms)
    chunk_set = set(chunk.tokens)
    overlap_terms = query_set & chunk_set
    overlap_count = sum(min(chunk.tokens[term], query_terms[term]) for term in overlap_terms)

    if overlap_count == 0:
        return 0.0

    coverage = len(overlap_terms) / max(len(query_set), 1)
    density = overlap_count / max(sum(chunk.tokens.values()), 1)
    score = (coverage * 2.0) + math.log1p(overlap_count) + density
    return round(score, 4)


def build_extractive_answer(question: str, matches: list[MatchedChunk]) -> str:
    """Create a compact answer from retrieved chunks when no LLM is configured."""

    if not CHUNKS:
        return "No documents have been ingested yet. Add a document first, then ask again."

    if not matches:
        return "I could not find matching document chunks for that question."

    leading = matches[0]
    prefix = (
        "I could not find a strong keyword match, but the closest ingested context says:"
        if leading.score == 0
        else "Based on the matching document context:"
    )
    excerpts = " ".join(chunk.text for chunk in matches[:2])
    return f"{prefix} {trim_to_sentence(excerpts, 900)}"


def maybe_generate_with_ollama(question: str, matches: list[MatchedChunk]) -> str | None:
    """Use Ollama when configured; fall back silently to extractive answers."""

    base_url = os.getenv("OLLAMA_BASE_URL", "").rstrip("/")
    model = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
    if not base_url or not matches:
        return None

    context = "\n\n".join(
        f"[{chunk.source}#{chunk.chunk_id}]\n{chunk.text}" for chunk in matches
    )
    prompt = (
        "Answer the question using only the context below. Keep it concise and cite "
        "the source chunk ids in plain text.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
            generated = body.get("response")
            return generated.strip() if isinstance(generated, str) and generated.strip() else None
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def tokenize(text: str) -> list[str]:
    """Normalize text for lightweight keyword matching."""

    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def trim_to_sentence(text: str, max_length: int) -> str:
    """Trim long extractive answers without cutting awkwardly mid-word."""

    if len(text) <= max_length:
        return text

    trimmed = text[:max_length].rsplit(" ", 1)[0].rstrip()
    return f"{trimmed}..."
