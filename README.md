# Movie List Recommendation

A movie and TV-series discovery app built around a local catalogue. Visitors can browse titles, search by name or English description, and find semantically similar titles. Signed-in users can rate titles, manage a personal library, complete taste onboarding, and receive content-based recommendations or a short “Tonight” shortlist.

PostgreSQL is the canonical catalogue and user-data store. Ollama creates embeddings, while Qdrant stores derived vectors for semantic search and recommendations.

## Technology

- **Web:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query
- **API:** FastAPI, SQLAlchemy, Alembic, Authlib, JWT cookies
- **Data and AI:** PostgreSQL, Ollama (`qwen3-embedding:0.6b`), Qdrant Cloud, TMDB
- **Tooling:** Python 3.13, uv, pnpm, Docker Compose, pytest, Ruff, mypy

## Run locally

### Prerequisites

Install Python 3.13+, [uv](https://docs.astral.sh/uv/), Node.js, pnpm 11, and Docker Desktop. You also need a Qdrant Cloud URL and API key for semantic features. A TMDB v3 API key is required only when synchronizing the catalogue; Google credentials are optional.

Create a local configuration file and fill in the required values. Never commit secrets.

```bash
cp .env.example .env
```

At minimum, set secure values for `AUTH_JWT_SECRET` and `AUTH_SESSION_SECRET`, plus `QDRANT_URL`, `QDRANT_API_KEY`, and `QDRANT_COLLECTION`. Set `TMDB_API_KEY` before running catalogue synchronization.

Install project dependencies and start PostgreSQL and Ollama:

```bash
uv sync --locked --group dev
pnpm install --frozen-lockfile
docker compose -f infra/compose.yaml --env-file .env --profile dependencies up -d postgres ollama
uv run alembic -c apps/api/alembic.ini upgrade head
docker compose -f infra/compose.yaml --env-file .env exec ollama ollama pull qwen3-embedding:0.6b
```

Start the API and web app in separate terminals:

```bash
uv run uvicorn app.main:app --app-dir apps/api --reload
pnpm run web:dev
```

Open the web app at `http://localhost:5173`. The API documentation is available at `http://localhost:8000/docs`.

## CLI

Run these commands from the repository root with `uv run recsys`.

| Command | Purpose |
| --- | --- |
| `uv run recsys diagnostics` | Prints the active Python runtime as JSON. |
| `uv run recsys catalog sync` | Imports popular English movies and TV series from TMDB, updates PostgreSQL, then rebuilds their Qdrant vectors. Defaults to five pages of each type. |
| `uv run recsys catalog sync --type movie --pages 2` | Synchronizes only movies and limits TMDB discovery to two pages. `--type` accepts `all`, `movie`, or `tv`; `--pages` must be at least 1. |
| `uv run recsys catalog index` | Indexes only canonical titles that do not yet have a Qdrant vector. It does not call TMDB or refresh existing vectors. |

`catalog sync` requires PostgreSQL, Ollama, Qdrant, and `TMDB_API_KEY`. `catalog index` requires PostgreSQL, Ollama, and Qdrant, but not TMDB. Both commands return JSON reports. Qdrant is derived storage and can be rebuilt; PostgreSQL remains the source of truth.

## Verification

```bash
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy
pnpm run web:lint
pnpm run web:typecheck
pnpm run web:build
```