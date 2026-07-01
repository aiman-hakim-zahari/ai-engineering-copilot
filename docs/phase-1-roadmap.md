# Phase 1: Portfolio-Ready Vertical Slice

Goal: complete the project as a polished, honest one-week portfolio demo. This
phase should finish the working end-to-end slice, not turn the repo into a
production platform.

## Day 1: Stabilize The Stack

- Run `docker compose up --build` from a clean state.
- Fix any Compose, port, or environment issues.
- Confirm:
  - frontend at `http://localhost:3000`
  - gateway Swagger at `http://localhost:5000/swagger`
  - FastAPI docs at `http://localhost:8001/docs`
- Add a short `docs/demo-script.md` with the exact demo flow.

## Day 2: Polish The Frontend

- Improve empty states, success messages, and error messages.
- Keep the sample document path foolproof.
- Make source chunks easier to scan.
- Check mobile and desktop layouts.
- Add screenshots or GIF-ready demo notes.

## Day 3: Strengthen The Gateway

- Add focused ASP.NET Core tests for:
  - `GET /health`
  - `POST /documents` validation
  - `POST /chat` validation
  - ML-service-unavailable handling
- Keep the gateway thin.
- Make Swagger descriptions clearer.

## Day 4: Improve The ML/RAG Service

- Improve chunk ranking slightly:
  - ignore common stopwords
  - boost exact phrase or important term matches
  - return clearer no-match answers
- Add tests for chunking, retrieval, empty state, and answer shape.
- Keep the fallback extractive path as the default.

## Day 5: Add Lightweight Persistence Or Document The Fallback

- Preferred one-week choice: either add simple local JSON/file persistence for
  chunks or keep in-memory storage and clearly document the limitation.
- Do not add full PostgreSQL/pgvector unless the rest of the demo is already
  solid.
- Update docs to explain the current storage approach and future pgvector path.

## Day 6: Portfolio Cleanup

- Final README pass:
  - screenshots
  - architecture diagram
  - demo script
  - what is implemented
  - what is intentionally out of scope
  - future improvements
- Remove stale generated files or unused assets.
- Ensure old roadmap/prompts are clearly archived.

## Day 7: Final QA And Demo Prep

- Run:
  - `npm run typecheck`
  - `npm run build`
  - `dotnet build`
  - `uv run pytest`
  - `docker compose config`
  - full manual ingest/chat smoke test
- Record a 60-90 second demo flow.
- Prepare a short portfolio blurb explaining the architecture and tradeoffs.

## Phase 1 Acceptance Bar

- A hiring manager can run it locally.
- The UI looks clean.
- The end-to-end flow works reliably.
- README matches reality.
- No claims about auth, RBAC, advanced RAG, observability, streaming, or
  pgvector unless actually implemented.
