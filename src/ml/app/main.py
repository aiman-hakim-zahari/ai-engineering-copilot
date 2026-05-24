"""FastAPI application entrypoint for the ML service."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app import __version__

app = FastAPI(
    title="AI Engineering Copilot — ML Service",
    description=(
        "Internal service owning the RAG pipeline: chunking, embedding, "
        "vector search, reranking, prompt construction, LLM inference, "
        "and evaluation. Called by the C# application backend over REST."
    ),
    version=__version__,
)


class HealthResponse(BaseModel):
    """Liveness payload returned by /healthz."""

    status: str
    service: str
    version: str


@app.get("/healthz", response_model=HealthResponse, tags=["ops"])
def healthz() -> HealthResponse:
    """Liveness probe.

    Returns 200 as long as the process is up and the ASGI app can serve
    requests. Readiness (`/readyz`) — which checks Postgres + Ollama
    connectivity — lands once those clients exist.
    """
    return HealthResponse(status="ok", service="ml", version=__version__)
