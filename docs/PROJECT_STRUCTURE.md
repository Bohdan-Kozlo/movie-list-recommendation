# Project Structure

## Repository Layout

```text
movie-list-recommendation/
├── apps/
│   ├── api/                    # FastAPI application
│   │   ├── app/
│   │   │   ├── core/           # configuration, errors, middleware
│   │   │   ├── adapters/       # PostgreSQL, TMDB, Qdrant, Ollama, OAuth
│   │   │   └── modules/        # vertical product modules
│   │   └── tests/
│   │       ├── unit/
│   │       └── integration/
│   └── web/                    # React SPA built with Vite
│       ├── src/
│       │   ├── app/            # bootstrap, routing, providers
│       │   ├── modules/        # vertical product modules
│       │   └── shared/         # shared UI, REST client, types, utilities
│       └── tests/
├── ml/
│   ├── recsys/                 # reusable, testable recommendation package
│   │   ├── ingestion/
│   │   ├── embeddings/
│   │   ├── collaborative/
│   │   ├── hybrid/
│   │   ├── evaluation/
│   │   ├── registry/
│   │   └── cli/
│   ├── notebooks/              # exploration only, never production logic
│   └── tests/
├── data/
│   ├── manifests/              # committed dataset metadata and checksums
│   ├── raw/                    # ignored downloaded data
│   ├── interim/                # ignored normalized data
│   └── processed/              # ignored training-ready data
├── artifacts/                  # ignored local exports and reports
├── docs/                       # product and technical documentation
├── infra/                      # Dockerfiles and Docker Compose
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
├── pnpm-lock.yaml
└── README.md
```

## Vertical Modules

The API and web applications organize code by product capability, not by technical role. This keeps a module's interface, implementation, tests, and local rules close together.

API modules are:

- `auth`: registration, email/password login, Google OAuth, identity linking, and cookies.
- `users`: profile and authenticated-user information.
- `onboarding`: mandatory initial ratings and progress rules.
- `catalog`: search, filters, details, TMDB synchronization, and on-demand title import.
- `interactions`: ratings, watched history, watchlist, and not-interested state transitions.
- `recommendations`: personal and similar-title recommendation requests, explanation rendering, and response shaping.

Web modules follow the same product vocabulary. Tailwind CSS provides styling, shadcn/ui primitives belong in shared UI code only when reused, and TanStack Query hooks remain with the module that owns their server state. The `shared` area must not become a dumping ground: it only contains code genuinely reused by multiple modules.

## Recommendation Package

`ml/recsys` is a local Python package, not a separate network service. FastAPI imports its online recommendation functionality and its CLI exposes offline operations.

Notebooks may explore a hypothesis, but a result becomes production behavior only after moving its logic into a tested module under `ml/recsys`.

## Data and Artifact Policy

Only manifests and code are committed. Downloaded data, transformed datasets, vector exports, local model artifacts, and MLflow state are ignored. A developer can reproduce them using documented `recsys` commands.

Qdrant Cloud is a derived vector store. PostgreSQL remains the canonical record of a project and its external identifiers.

## Command Surface

The project has no Windows-specific wrapper scripts. The documented command surfaces are:

- `uv run ...` for Python and ML tasks.
- `pnpm run ...` for the Vite web application.
- `docker compose ...` for containerized execution.
- `recsys ...` for data and model lifecycle operations.

The `recsys` interface owns diagnostics, catalogue synchronization, embedding generation, CF training, hybrid evaluation, and model promotion.
