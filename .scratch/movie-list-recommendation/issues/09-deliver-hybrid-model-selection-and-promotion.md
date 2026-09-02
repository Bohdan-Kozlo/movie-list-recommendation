# 09 — Deliver Hybrid Model Selection and Promotion

**What to build:** The product selects and serves a hybrid recommender that combines semantic content, collaborative filtering when evidence is sufficient, and popularity-by-preferred-genres.

**Blocked by:** 07 — Deliver Content-Based Personal Recommendations; 08 — Deliver Collaborative-Filtering Experiment Pipeline.

**Status:** ready-for-agent

- [ ] Hybrid weights are evaluated against the popularity baseline and the selected configuration is recorded in MLflow.
- [ ] A model can be promoted manually only when it is not worse than the active model by NDCG@K; requests omit CF when evidence is insufficient.

