# 08 — Deliver Collaborative-Filtering Experiment Pipeline

**What to build:** A developer can ingest MovieLens latest-small, train and evaluate LensKit collaborative filtering with a temporal split, and inspect reproducible runs in MLflow.

**Blocked by:** 02 — Deliver Catalogue Discovery.

**Status:** ready-for-agent

- [ ] The pipeline maps MovieLens identifiers to catalogue identities without mixing anonymized MovieLens users with product users.
- [ ] It records Precision@K, Recall@K, and NDCG@K using a relevance threshold of 3.5 or higher.

