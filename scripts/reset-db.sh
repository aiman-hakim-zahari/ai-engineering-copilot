#!/usr/bin/env bash
# Drop and recreate the Postgres database volume. Destructive — local only.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

read -rp "This will DELETE all local Postgres data. Continue? [y/N] " ans
if [[ "${ans,,}" != "y" ]]; then
  echo "Aborted."
  exit 0
fi

echo "==> Stopping Postgres"
docker compose stop postgres

echo "==> Removing Postgres data volume"
docker compose rm -fv postgres
docker volume rm "$(basename "$REPO_ROOT")_postgres_data" 2>/dev/null || true

echo "==> Restarting Postgres (fresh volume)"
docker compose up -d postgres

echo "==> Done. Re-run ./scripts/seed.sh to repopulate."
