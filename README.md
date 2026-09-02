# Movie List Recommendation System

A reproducible React/Vite, FastAPI, PostgreSQL, Ollama, MLflow, and Qdrant Cloud development environment for a movie and TV-series recommendation system.

## Prerequisites

- Git
- Python 3.13 and [uv](https://docs.astral.sh/uv/)
- Node.js 24 and pnpm 11 (`corepack enable`)
- Docker Desktop with Docker Compose for containerised dependencies and the full stack

## Configure the workspace

Copy `.env.example` to `.env` and replace the local-development password and Qdrant Cloud values as needed. Never commit `.env` or a real Qdrant API key.

```powershell
Copy-Item .env.example .env
uv sync --locked --group dev --group ml
pnpm install --frozen-lockfile
git config core.hooksPath .githooks
```

The repository tracks `uv.lock` and `pnpm-lock.yaml`. Use `uv sync --locked` and `pnpm install --frozen-lockfile` to reproduce the locked environment.

Check the installed recommendation-system command surface:

```powershell
uv run --group ml --locked recsys diagnostics
```

## Run locally (hybrid)

Start PostgreSQL, Ollama, and MLflow in containers:

```powershell
docker compose -f infra/compose.yaml --profile dependencies up -d
```

In separate terminals, start the API and web application:

```powershell
$env:PYTHONPATH = "apps/api"
uv run --locked uvicorn app.main:app --reload --port 8000
pnpm --dir apps/web dev
```

The API health endpoint is available at `http://localhost:8000/health`; the Vite application is available at `http://localhost:5173`.

Pull the required embedding model after Ollama has started:

```powershell
docker compose -f infra/compose.yaml exec ollama ollama pull qwen3-embedding:0.6b
```

## Run the full stack in Docker Compose

```powershell
docker compose -f infra/compose.yaml --profile full up --build
```

Open the web application at `http://localhost:5173` and the API health endpoint at `http://localhost:8000/health`.

## Quality checks

```powershell
uv run --group dev --locked ruff format --check .
uv run --group dev --locked ruff check .
uv run --group dev --locked mypy
uv run --group dev --locked pytest
pnpm --dir apps/web lint
pnpm --dir apps/web typecheck
pnpm --dir apps/web build
```

The tracked `.githooks/pre-commit` hook runs formatter, linter, and type-check commands before a commit. Configure `core.hooksPath` once per clone using the command above.
