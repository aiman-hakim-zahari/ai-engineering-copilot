#!/usr/bin/env bash
# Seed the database with sample users and documents for local development.
# Requires the stack to be running (./scripts/setup.sh).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck disable=SC1091
[[ -f .env ]] && source .env

: "${POSTGRES_DB:?POSTGRES_DB not set}"
: "${POSTGRES_USER:?POSTGRES_USER not set}"

echo "==> Seeding ${POSTGRES_DB} via copilot_postgres"

docker exec -i copilot_postgres psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" <<'SQL'
-- Placeholder seed. Replace with real fixtures once schema lands.
SELECT 'seed.sh ran against ' || current_database() AS status;
SQL

echo "==> Seed complete."
