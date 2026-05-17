#!/usr/bin/env bash
# First-time local setup for AI Engineering Copilot.
# Run from the repo root: ./scripts/setup.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Verifying prerequisites"
command -v docker >/dev/null 2>&1 || { echo "docker not found"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "docker compose v2 not found"; exit 1; }

if [[ ! -f .env ]]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
  echo "    Edit .env to set DB password, JWT secret, etc."
fi

echo "==> Building and starting the stack"
docker compose up --build -d

echo "==> Waiting for Postgres to become healthy"
until [[ "$(docker inspect -f '{{.State.Health.Status}}' copilot_postgres 2>/dev/null)" == "healthy" ]]; do
  sleep 2
done

echo "==> Pulling Ollama models (first run only)"
docker exec copilot_ollama ollama pull nomic-embed-text || true
docker exec copilot_ollama ollama pull llama3 || true

echo "==> Setup complete."
echo "    Frontend:    http://localhost:3000"
echo "    Backend API: http://localhost:5000"
