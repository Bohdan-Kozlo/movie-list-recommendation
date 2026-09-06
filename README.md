# Movie List Recommendation

English-language movie and TV catalogue with ratings, a personal library, required taste onboarding, semantic similar titles and content-based personal recommendations.

Start with [Project Structure](docs/PROJECT_STRUCTURE.md) for the code reading path, [Architecture](docs/ARCHITECTURE.md) for the request flow, [Specification](docs/SPEC.md) for product rules and [Libraries](docs/LIBRARIES.md) for approved dependencies.

## Local development

Run commands from the repository root. Install Python 3.13+, uv, Node.js and the pnpm version declared in `package.json`. Copy `.env.example` to `.env` if you have not already configured it. Set the database connection, TMDB credentials, Qdrant Cloud URL/key and long random authentication secrets. Keep credentials local.

```powershell
uv sync --locked --group dev
pnpm install --frozen-lockfile
docker compose -f infra/compose.yaml --env-file .env --profile dependencies up -d postgres ollama
uv run --group dev alembic -c apps/api/alembic.ini upgrade head
docker compose -f infra/compose.yaml --env-file .env exec ollama ollama pull qwen3-embedding:0.6b
```

Start the API and web development server in separate terminals:

```powershell
uv run uvicorn app.main:app --app-dir apps/api --reload
pnpm run web:dev
```

The example configuration exposes the web application at `http://localhost:5173` and API documentation at `http://localhost:8000/docs`. On PowerShell installations that block the pnpm script shim, use `pnpm.cmd` for the same commands.

For Google sign-in, configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` and the exact registered `GOOGLE_REDIRECT_URI`. The local example is `http://localhost:8000/auth/google/callback`. Email/password authentication is also available. Access and refresh tokens use HttpOnly cookies; HTTPS deployments require `AUTH_COOKIE_SECURE=true`.

## Catalogue and vectors

```powershell
uv run recsys diagnostics
uv run recsys catalog sync
uv run recsys catalog sync --type movie --pages 2
uv run recsys catalog index
```

`catalog sync` defaults to five popularity-sorted TMDB discovery pages for each of English movies and TV series. It updates existing canonical records, then rebuilds vectors for the entire local catalogue, including previously indexed titles. Its JSON result contains `created`, `updated` and `indexed` counts.

`catalog index` checks existing vector IDs in batches and indexes only missing titles. It returns `scanned`, `indexed` and `skipped` counts. It does not refresh existing vectors after metadata changes; use synchronization when those need rebuilding.

Both indexing paths require Ollama with `qwen3-embedding:0.6b` and Qdrant Cloud. PostgreSQL is canonical; Qdrant stores derived vectors that can be rebuilt. There is no Qdrant fallback. Similar-title and personal recommendation logic lives in the API recommendation module; `ml/recsys` supplies the CLI.

Users can browse and manage their library during onboarding. Ten ratings unlock personal recommendations, with separate movie and TV sections. Collaborative filtering and its experiment infrastructure were removed; the rationale is recorded in the specification.

## Docker Compose

```powershell
docker compose -f infra/compose.yaml --env-file .env --profile full up --build -d
docker compose -f infra/compose.yaml --env-file .env exec api alembic -c apps/api/alembic.ini upgrade head
docker compose -f infra/compose.yaml --env-file .env exec ollama ollama pull qwen3-embedding:0.6b
docker compose -f infra/compose.yaml --env-file .env exec api recsys catalog sync
```

Compose runs PostgreSQL, Ollama, API and web. Qdrant remains external. Migrations and model downloading are explicit steps. The API image includes the local console package so catalogue commands use the same code as native execution.

## Verification

```powershell
uv run --group dev --locked pytest
uv run --group dev --locked ruff format --check .
uv run --group dev --locked ruff check .
uv run --group dev --locked mypy
pnpm run web:lint
pnpm run web:typecheck
pnpm run web:build
```

The web typecheck checks both application and Vite configuration sources. Enable the tracked local hook with `git config core.hooksPath .githooks`. Tests run manually; CI is outside the current scope.

Existing automated tests exercise REST contracts, use cases and isolated persistence. They do not establish live TMDB, Google OAuth, Ollama or Qdrant availability. Any additional Qdrant integration checks must use an isolated collection.
