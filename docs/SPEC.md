# Movie List Recommendation System Specification

## Problem Statement

People who want to choose a film or TV series often face a large, unstructured catalogue and recommendations that either ignore their preferences or repeat content they have already watched. The project must demonstrate how a modern recommendation system can turn explicit ratings and catalogue metadata into useful, explainable suggestions.

The product is an English-language learning and portfolio application. Its primary goal is to make the complete lifecycle of a recommendation system visible and reproducible: catalogue ingestion, embedding generation, collaborative filtering, hybrid ranking, evaluation, model promotion, and product integration.

## Solution

The application will provide an authenticated movie and TV-series catalogue where a user completes a required onboarding flow by rating ten known titles. The application will use those ratings to provide two recommendation modes:

1. Personal recommendations for the user.
2. Titles similar to a selected film or TV series.

Content-based recommendations will use local Qwen3 embeddings generated through Ollama and stored in Qdrant Cloud. Collaborative filtering will be trained with LensKit on MovieLens latest-small. A hybrid recommender will merge content, collaborative, and popularity signals when collaborative data is sufficient; otherwise it will use content and popularity only. PostgreSQL remains the source of truth for application data, while Qdrant holds derived vectors and searchable metadata.

## User Stories

1. As a visitor, I want to register with an email and password, so that my preferences can be saved.
2. As a visitor, I want to sign in with Google OAuth, so that I can access the product without creating another password.
3. As an existing user, I want a verified Google email to connect to my existing email account, so that I have one profile regardless of sign-in method.
4. As an authenticated user, I want my session managed with access and refresh tokens in cookies, so that I can remain signed in securely.
5. As a new user, I want to complete onboarding by rating ten familiar titles, so that the first recommendations are personalized.
6. As a new user, I want onboarding to show popular movies and TV series and allow title search, so that I can quickly find known titles.
7. As a user, I want to rate a title from 0.5 to 5.0 in half-point increments, so that I can express my taste precisely.
8. As a user, I want each title to have one current rating that I may delete but not edit, so that my profile has no duplicate ratings.
9. As a user, I want to mark a title as watched, so that I can maintain viewing history and avoid repeated recommendations.
10. As a user, I want to save a title to my watchlist, so that I can remember what I plan to watch.
11. As a user, I want to mark a title as not interested, so that unwanted titles are excluded from recommendations.
12. As a user, I want watched titles to leave my watchlist automatically, so that the lists stay consistent.
13. As a user, I want not-interested titles to leave my watchlist automatically, so that my saved list stays meaningful.
14. As a user, I want a catalogue of both movies and TV series, so that I can discover either content type.
15. As a user, I want separate Movies and TV Series recommendation sections, so that I can choose the type of content I want.
16. As a user, I want search and filters for title, type, genre, language, and year, so that I can narrow the catalogue.
17. As a user, I want to open a title details page, so that I can understand a recommendation before acting on it.
18. As a user, I want to see titles similar to a selected title, so that I can discover content with related themes and metadata.
19. As a user, I want a personal recommendation feed, so that the application can suggest content aligned with my ratings.
20. As a user, I want watched and not-interested titles excluded from recommendation lists, so that recommendations remain actionable.
21. As a user, I want recommendation lists to avoid near-duplicate titles, so that the top results are diverse.
22. As a user, I want a short factual explanation for each recommendation, so that I understand why it appeared.
23. As a user, I want explanations such as a shared genre, similarity to a rated title, or similar-user preference, so that they are trustworthy.
24. As a user, I want a searched TMDB title missing from the local catalogue to become available for similarity search, so that the catalogue does not feel artificially limited.
25. As a user, I want the system to represent a TV series as one title rather than seasons or episodes, so that tracking stays simple.
26. As a developer, I want TMDB and IMDb identifiers normalized, so that catalogue records, MovieLens ratings, and current metadata can be linked reliably.
27. As a developer, I want embeddings generated locally with `qwen3-embedding:0.6b`, so that the project avoids per-request embedding costs.
28. As a developer, I want derived vectors stored in Qdrant Cloud, so that semantic nearest-neighbor search is efficient.
29. As a developer, I want PostgreSQL to remain the canonical catalogue and user-data store, so that vector storage can be rebuilt safely.
30. As a developer, I want collaborative filtering trained from MovieLens latest-small, so that the project can demonstrate CF before it has many product users.
31. As a developer, I want real product users kept separate from anonymized MovieLens profiles, so that unrelated user identities and data do not mix.
32. As a developer, I want CF disabled when data is insufficient, so that weak CF predictions do not degrade results.
33. As a developer, I want hybrid weights selected through evaluation rather than manual guesses, so that model selection is evidence-based.
34. As a developer, I want a temporal train/test split, so that offline evaluation resembles future recommendation.
35. As a developer, I want ratings of 3.5 or higher treated as relevant for ranking evaluation, so that ranking metrics have a consistent relevance rule.
36. As a developer, I want experiments, metrics, and model artifacts recorded in MLflow, so that model changes are reproducible.
37. As a developer, I want a model promoted manually only after it is not worse than the active model by NDCG@K, so that an experiment cannot silently replace a working model.
38. As a developer, I want catalogue sync, embedding generation, training, evaluation, and promotion to be explicit CLI commands, so that every state change is repeatable.
39. As a developer, I want the application to run locally and through Docker Compose, so that development and demonstration are reproducible.
40. As a developer, I want local Git hooks to block formatting, linting, and type-check failures, so that basic quality problems do not reach a push.
41. As a portfolio reviewer, I want architecture, data pipeline, library choices, setup, and evaluation results documented, so that I can assess the system quickly.

## Implementation Decisions

- The repository is a monorepo with a React/Vite web application, a FastAPI application, a local Python recommendation package, infrastructure definitions, data manifests, and documentation.
- The FastAPI application uses vertical modules for auth, users, onboarding, catalogue, interactions, and recommendations. A caller interacts with a module through its interface rather than reaching into its implementation.
- The recommendation module is the primary deep module. Its interface exposes personal recommendations, similar-title recommendations, and project refresh. Its implementation hides candidate generation, Qdrant querying, CF availability checks, exclusion rules, diversity reranking, and explanation generation.
- PostgreSQL is the source of truth for users, identities, sessions, catalogue metadata, normalized external IDs, ratings, watched history, watchlist entries, not-interested entries, and active model metadata.
- Qdrant Cloud Free Tier contains one collection for movies and TV series. Each vector payload includes the canonical project ID, TMDB ID, type, genres, year, and data needed for filtering.
- Qdrant is a derived store. Rebuilding the vector collection from PostgreSQL and the active embedding configuration must be possible at any time.
- TMDB provides current metadata and poster assets. Kaggle/IMDb data supports repeatable catalogue experiments. MovieLens latest-small provides CF ratings and identifier links.
- Catalogue import is idempotent and maps MovieLens, IMDb, and TMDB identifiers where available. A manual catalogue sync command performs updates.
- If a title is absent from the local catalogue, a search may retrieve it from TMDB, normalize it, create its embedding synchronously, store it, and then return similar titles.
- The embedding text includes overview, genres, keywords, cast, director, type, and year. Overview, keywords, and genres have semantic priority; year is also retained as structured filtering metadata.
- Ollama runs `qwen3-embedding:0.6b`. The same embedding model and vector dimension are used for all vectors in an active Qdrant collection.
- Content-based recommendations compare title and user-profile embeddings. A user profile is derived primarily from explicit ratings; watched status is tracking and exclusion data rather than a strong preference signal.
- The application accepts ratings from 0.5 to 5.0 in half-point increments. Zero represents no rating. One current rating exists per user/title pair; it may be deleted but not replaced.
- Watchlist, watched, and not-interested states have consistency rules. Marking watched or not interested removes an item from watchlist. Watched and not-interested items are excluded from recommendation candidates.
- Collaborative filtering uses LensKit and MovieLens latest-small. Product-user records stay separate from MovieLens users. CF is omitted from a response when it lacks enough evidence.
- Hybrid ranking combines normalized content, collaborative, and popularity scores. Evaluation selects candidate weights using temporal data splits and NDCG@K; popularity-by-preferred-genres is the baseline.
- A lightweight diversity reranking step prevents a single franchise, genre, or near-identical set of titles from occupying a complete recommendation list.
- Recommendation explanations are deterministic templates based on actual signals. The product does not use an LLM to invent explanations.
- MLflow records dataset identity, split configuration, embedding model, model parameters, ranking metrics, and artifacts. Promotion is explicit and only activates a run that is not worse than the active model by NDCG@K.
- The `recsys` console interface is the only interface for catalogue ingestion, embedding creation, CF training, hybrid evaluation, model promotion, and environment diagnostics. It supports safe options such as dry-run and limited processing.
- `uv` manages Python dependencies, virtual environments, dependency groups, commands, and the committed lockfile. Runtime, ML, and development dependencies are separated into groups.
- Docker Compose runs the web application, API, PostgreSQL, Ollama, and MLflow. It connects to Qdrant Cloud rather than starting a local Qdrant container.
- The web application is a React SPA built with Vite, managed with pnpm, and styled with Tailwind CSS. It uses vertical modules mirroring product capabilities, shadcn/ui primitives for reusable accessible UI, and TanStack Query for REST server state, caching, and invalidation. Shared code remains limited to truly common UI, REST-client, utility, and type concerns.
- REST is the integration interface between the web application and FastAPI. OpenAPI documentation is generated by FastAPI.
- Authentication includes email/password and Google OAuth. Access and refresh tokens are stored in cookies. Automatic identity linking is allowed only for a verified Google email that exactly matches an existing account email.
- The initial release has no CI. Local hooks run formatter, linter, and type checks. Tests remain runnable manually.

## Testing Decisions

- The highest test seam is the REST recommendation interface. Tests should request recommendations and assert externally observable outcomes, not Qdrant query implementation details or private ranking steps.
- Recommendation tests verify that watched and not-interested titles never appear, type filtering works, explanations match real signals, and a low-evidence request omits CF instead of pretending it is available.
- Catalogue tests verify idempotent imports, external-ID normalization, and on-demand title addition.
- Interaction tests verify rating range, one-rating-per-title behavior, rating deletion, and watchlist transitions caused by watched and not-interested actions.
- Auth tests verify registration, login, verified-email account linking, and cookie session behavior.
- ML tests verify temporal splitting, relevance threshold configuration, metric calculation, experiment metadata, and that promotion does not activate an inferior model.
- Integration tests use isolated Qdrant test collections and clean them up afterward; they never access the production collection.
- Web tests cover required onboarding, catalogue search, rating and list actions, recommendation display, and explanations.
- Local hooks run formatter, linter, and type checks. Unit and integration tests are run manually until CI is deliberately introduced.
- There is no existing test prior art because the repository is currently empty. Test organization starts with unit and integration suites under the API, web, and ML areas.

## Out of Scope

- Training a custom neural recommendation model or neural collaborative filtering model.
- Password reset, email verification, and account deletion.
- Editing an existing rating; deletion is supported instead.
- Tracking seasons or episodes separately from a TV series.
- Social features, comments, shared lists, trailers, and an admin panel.
- Automatic catalogue scheduling; catalogue updates are manual CLI operations.
- Manual recommendation evaluation during the first implementation phase.
- Clickstream-based preference learning.
- A Qdrant fallback if Qdrant Cloud is unavailable.
- CI/CD and cloud deployment beyond Docker Compose reproducibility.

## Further Notes

- The application and initial catalogue experience are English-language only.
- Raw, interim, processed datasets, generated artifacts, model files, and local MLflow state are not committed to Git. Versioned manifests and reproducible CLI commands are committed instead.
- The repository should include an environment example, an architecture document, a project-structure document, a library-usage document, a data-pipeline document, a recommendation-system document, and an evaluation report.
- The proposed test seam is the REST recommendation interface. It is intentionally high-level so the web application and tests are insulated from storage and model changes.
