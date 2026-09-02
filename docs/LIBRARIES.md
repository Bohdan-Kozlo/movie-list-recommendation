# Library and Platform Usage

## Python Runtime and Tooling

| Tool or library | Purpose | Usage policy |
|---|---|---|
| uv | Python dependency management, environments, lockfile, and command execution | `pyproject.toml` and `uv.lock` are authoritative; use `uv run` for Python commands. |
| FastAPI | REST application and OpenAPI documentation | Exposes the product interface; routers stay thin and delegate to vertical modules. |
| LensKit | Collaborative filtering experiments and ranking evaluation support | Used with MovieLens latest-small; never mixes anonymous MovieLens users with product users. |
| MLflow | Experiment tracking, artifacts, and model promotion | Every training and evaluation run records data identity, parameters, and ranking metrics. |
| pytest | Python test execution | Used for unit and integration suites. |
| Ruff and a type checker | Formatting, linting, and static validation | Run through local Git hooks before a normal push. |

## Data and Recommendation Platforms

| Tool or platform | Purpose | Usage policy |
|---|---|---|
| TMDB API | Current catalogue metadata, details, search results, and poster paths | Metadata is normalized into PostgreSQL. A missing searched title may be imported on demand. |
| Kaggle / IMDb datasets | Repeatable catalogue and metadata experiments | Store only manifests in Git; downloaded data remains ignored. |
| MovieLens latest-small | Explicit rating data for CF and offline experiments | Normalize identifiers through its links data; use a temporal split for evaluation. |
| Ollama | Local model runtime | Runs locally or in Docker Compose and is addressed through configuration. |
| `qwen3-embedding:0.6b` | Local title-embedding model | Embeds a normalized text representation of project metadata. Keep one active embedding configuration per Qdrant collection. |
| Qdrant Cloud Free Tier | Vector search and metadata filtering | Holds derived vectors only. Never treat it as the canonical catalogue database. |

## Web Application

| Tool or library | Purpose | Usage policy |
|---|---|---|
| React | Interactive web interface | Organize UI by product module. |
| Vite | React SPA development and build tooling | Provides the frontend development server and production build. |
| Tailwind CSS | Utility-first styling | Integrates with Vite and provides the styling foundation for the web application. |
| shadcn/ui | Reusable accessible UI primitives | Add only the primitives a product module needs; generated source remains owned and customizable by this repository. |
| TanStack Query | REST server-state fetching, caching, and invalidation | Keep query keys and query hooks close to the product modules that own the data. |
| pnpm | JavaScript dependency management and project commands | Keep web dependencies in the web application manifest and commit `pnpm-lock.yaml`. |

## Docker Runtime

Docker Compose orchestrates the FastAPI application, React application, PostgreSQL, Ollama, and MLflow. It does not start Qdrant because the project uses Qdrant Cloud.

## Dependency Boundaries

- The web application only communicates with the backend through documented REST endpoints.
- FastAPI reaches external platforms through adapters, not from route handlers.
- The recommendation module hides Qdrant, Ollama, LensKit, hybrid ranking, and exclusion logic behind a small interface.
- The ML package owns offline ingestion, embedding creation, training, evaluation, and promotion. Notebooks are not an execution dependency.
