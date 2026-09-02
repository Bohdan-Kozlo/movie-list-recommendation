# Architecture

## System View

```text
React + Vite SPA
        |
        | REST / OpenAPI
        v
FastAPI application
  |        |          |          |
  |        |          |          +--> TMDB API
  |        |          +-------------> Ollama / qwen3-embedding:0.6b
  |        +------------------------> Qdrant Cloud
  +---------------------------------> PostgreSQL
        |
        +---------------------------> MLflow

MovieLens latest-small / Kaggle / IMDb
        |
        v
recsys CLI and ML package
```

## Core Seams

The application uses a small number of high-leverage seams.

### Recommendation Module

The recommendation module is the central deep module. Callers request personal recommendations, similar titles, or a project refresh. The module hides the details of content retrieval, collaborative filtering, hybrid score normalization, candidate exclusion, diversity reranking, and deterministic explanations.

The REST recommendation interface is the highest test seam. It allows tests to exercise visible product behavior without coupling to the Qdrant client, the Ollama client, LensKit internals, or private ranking steps.

### Catalogue Module

The catalogue module owns canonical project records and normalized TMDB, IMDb, and MovieLens identifiers. It can synchronize known projects and import a missing TMDB search result on demand. Its callers do not need to understand upstream provider formats.

### Interaction Module

The interaction module owns the consistency rules for a user's rating, watched history, watchlist, and not-interested state. It makes list transitions atomic and exposes clear outcomes to the REST layer.

## Recommendation Flow

1. A user completes required onboarding with ten ratings.
2. The application persists ratings and interaction states in PostgreSQL.
3. The personal recommendation request loads the user's eligible preference signals.
4. The recommendation module obtains semantic candidates from Qdrant using content embeddings.
5. If CF evidence is sufficient, the module obtains collaborative candidates from the active LensKit artifact.
6. The module combines normalized content, CF, and popularity-by-preferred-genres scores using the active MLflow-promoted configuration.
7. Watched and not-interested titles are removed. Diversity reranking reduces near duplicates.
8. The API returns separate movie and TV-series results with factual explanations.

If CF evidence is insufficient, the module omits CF rather than returning a low-confidence result. If a title is absent from the local catalogue, the catalogue module imports TMDB metadata, creates a Qwen3 embedding through Ollama, writes the derived vector to Qdrant, and then supports similarity search.

## Persistence Responsibilities

| Store | Responsibility |
|---|---|
| PostgreSQL | Canonical users, identities, sessions, projects, external IDs, interaction states, active-model metadata |
| Qdrant Cloud | Derived title vectors and filterable vector payloads |
| MLflow | Experiment parameters, metrics, artifacts, and promotion records |
| Local ignored data directories | Downloaded source datasets and processing stages |

## Authentication

Email/password and Google OAuth create or access the same user profile. Automatic identity linking is allowed only when Google returns a verified email that exactly matches an existing account. Access and refresh tokens are stored in cookies.

## Deployment and Runtime

Docker Compose starts the web application, FastAPI, PostgreSQL, Ollama, and MLflow. Qdrant is intentionally external and configured by environment variables. The same Python project can also run natively with `uv`.

There is no Qdrant availability fallback in the MVP. Recommendation functionality depends on Qdrant Cloud being available.
