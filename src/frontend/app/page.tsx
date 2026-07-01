"use client";

import { ChangeEvent, FormEvent, useMemo, useState } from "react";

type IngestResponse = {
  document_id: string;
  chunks_indexed: number;
  sources: string[];
};

type Source = {
  source: string;
  chunk_id: string;
  score: number;
};

type MatchedChunk = Source & {
  text: string;
};

type ChatResponse = {
  answer: string;
  sources: Source[];
  matched_chunks: MatchedChunk[];
};

const sampleDocument = `AI Engineering Copilot vertical slice

The demo has a Next.js TypeScript frontend, an ASP.NET Core API gateway, and a Python FastAPI ML service.

The frontend sends document ingestion and chat requests to the gateway only. The gateway forwards document text to the ML service for chunking and asks the ML service for answers.

The Python service stores chunks in memory for local development. Retrieval uses simple keyword scoring so the demo works without paid API keys or local model downloads.

Future improvements include PostgreSQL with pgvector, optional Ollama or OpenAI generation, authentication, evaluation, and production observability.`;

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:5000";

export default function Home() {
  const [documentText, setDocumentText] = useState("");
  const [documentSource, setDocumentSource] = useState("pasted-note.md");
  const [question, setQuestion] = useState("");
  const [ingestResult, setIngestResult] = useState<IngestResponse | null>(null);
  const [chatResult, setChatResult] = useState<ChatResponse | null>(null);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canAsk = useMemo(
    () => question.trim().length > 0 && !isAsking,
    [isAsking, question],
  );

  async function readFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setError(null);
    setDocumentSource(file.name);
    setDocumentText(await file.text());
  }

  async function ingestDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setChatResult(null);

    const text = documentText.trim();
    if (!text) {
      setError("Add document text or upload a text/markdown file first.");
      return;
    }

    setIsIngesting(true);
    try {
      const response = await fetch(`${apiBaseUrl}/documents`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          source: documentSource.trim() || "pasted-note.md",
        }),
      });

      if (!response.ok) {
        throw new Error(await readProblem(response, "Document ingest failed."));
      }

      setIngestResult((await response.json()) as IngestResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Document ingest failed.");
    } finally {
      setIsIngesting(false);
    }
  }

  async function askQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      setError("Ask a question about the ingested document.");
      return;
    }

    setIsAsking(true);
    try {
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: trimmedQuestion }),
      });

      if (!response.ok) {
        throw new Error(await readProblem(response, "Question failed."));
      }

      setChatResult((await response.json()) as ChatResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Question failed.");
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="workspace" aria-label="AI Engineering Copilot workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Portfolio vertical slice</p>
            <h1>AI Engineering Copilot</h1>
          </div>
          <div className="service-pill">Gateway: {apiBaseUrl}</div>
        </header>

        <div className="grid">
          <form className="panel document-panel" onSubmit={ingestDocument}>
            <div className="panel-header">
              <div>
                <p className="eyebrow">Step 1</p>
                <h2>Document</h2>
              </div>
              <button
                className="ghost-button"
                type="button"
                onClick={() => {
                  setDocumentSource("sample-architecture.md");
                  setDocumentText(sampleDocument);
                  setError(null);
                }}
              >
                Load sample
              </button>
            </div>

            <label className="field">
              <span>Source name</span>
              <input
                value={documentSource}
                onChange={(event) => setDocumentSource(event.target.value)}
                placeholder="architecture-note.md"
              />
            </label>

            <label className="file-field">
              <span>Upload .txt or .md</span>
              <input accept=".txt,.md,text/plain,text/markdown" type="file" onChange={readFile} />
            </label>

            <label className="field stretch">
              <span>Document text</span>
              <textarea
                value={documentText}
                onChange={(event) => setDocumentText(event.target.value)}
                placeholder="Paste a short engineering note, design decision, or README excerpt."
              />
            </label>

            <button className="primary-button" disabled={isIngesting} type="submit">
              {isIngesting ? "Indexing..." : "Index document"}
            </button>

            {ingestResult ? (
              <div className="status-line" role="status">
                Indexed {ingestResult.chunks_indexed} chunks from {ingestResult.sources.join(", ")}.
              </div>
            ) : null}
          </form>

          <section className="panel chat-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Step 2</p>
                <h2>Question</h2>
              </div>
            </div>

            <form className="question-form" onSubmit={askQuestion}>
              <label className="field">
                <span>Ask about the document</span>
                <input
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="What services are in this demo?"
                />
              </label>
              <button className="primary-button" disabled={!canAsk} type="submit">
                {isAsking ? "Asking..." : "Ask"}
              </button>
            </form>

            {error ? (
              <div className="error-box" role="alert">
                {error}
              </div>
            ) : null}

            <article className="answer-surface" aria-live="polite">
              <p className="eyebrow">Answer</p>
              {chatResult ? (
                <p>{chatResult.answer}</p>
              ) : (
                <p className="muted">Index a document, ask a question, and the answer appears here.</p>
              )}
            </article>

            {chatResult?.sources.length ? (
              <div className="sources">
                <div className="section-heading">
                  <p className="eyebrow">Sources</p>
                  <span>{chatResult.sources.length}</span>
                </div>
                <div className="source-list">
                  {chatResult.matched_chunks.map((chunk) => (
                    <article className="source-card" key={chunk.chunk_id}>
                      <div className="source-meta">
                        <strong>{chunk.source}</strong>
                        <span>Score {chunk.score.toFixed(2)}</span>
                      </div>
                      <p>{chunk.text}</p>
                    </article>
                  ))}
                </div>
              </div>
            ) : null}
          </section>
        </div>
      </section>
    </main>
  );
}

async function readProblem(response: Response, fallback: string) {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    const body = (await response.json()) as { detail?: string; title?: string };
    return body.detail ?? body.title ?? fallback;
  }

  const text = await response.text();
  return text || fallback;
}
