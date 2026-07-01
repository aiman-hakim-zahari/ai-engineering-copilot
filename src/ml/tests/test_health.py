"""Smoke tests for the demo ML service."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import __version__
from app.main import CHUNKS, DOCUMENT_IDS_BY_SOURCE, app

client = TestClient(app)


def setup_function() -> None:
    CHUNKS.clear()
    DOCUMENT_IDS_BY_SOURCE.clear()


def test_healthz_returns_200() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200


def test_healthz_payload_shape() -> None:
    response = client.get("/healthz")
    body = response.json()
    assert body == {"status": "ok", "service": "ml", "version": __version__}


def test_ingest_indexes_chunks() -> None:
    response = client.post(
        "/ingest",
        json={
            "source": "demo.md",
            "text": "The gateway is written in ASP.NET Core. The ML service uses FastAPI.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["chunks_indexed"] == 1
    assert body["sources"] == ["demo.md"]
    assert body["document_id"]


def test_answer_returns_sources_from_ingested_text() -> None:
    client.post(
        "/ingest",
        json={
            "source": "architecture.md",
            "text": "The frontend is Next.js. The gateway is ASP.NET Core. The RAG service is FastAPI.",
        },
    )

    response = client.post("/answer", json={"question": "What is the gateway built with?"})

    assert response.status_code == 200
    body = response.json()
    assert "ASP.NET Core" in body["answer"]
    assert body["sources"][0]["source"] == "architecture.md"
    assert body["matched_chunks"][0]["text"]
