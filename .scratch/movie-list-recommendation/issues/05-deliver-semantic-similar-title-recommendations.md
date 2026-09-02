# 05 — Deliver Semantic Similar-Title Recommendations

**What to build:** A visitor can request titles similar to a selected movie or TV series using local Qwen3 embeddings and Qdrant Cloud, including a factual reason for each result and on-demand import of a missing TMDB title.

**Blocked by:** 02 — Deliver Catalogue Discovery.

**Status:** ready-for-agent

- [ ] Similar-title results are returned from semantic vector search with title metadata and factual similarity explanations.
- [ ] A searched TMDB title absent from the catalogue becomes available for similarity recommendations after normalized import and embedding creation.

