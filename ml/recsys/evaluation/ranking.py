"""Temporal splitting and transparent top-N ranking metrics."""

from dataclasses import dataclass
from math import log2
from typing import Iterable

from recsys.ingestion.movielens import MovieLensRating


@dataclass(frozen=True)
class TemporalSplit:
    train: list[MovieLensRating]
    test: list[MovieLensRating]


@dataclass(frozen=True)
class RankingMetrics:
    precision_at_k: float
    recall_at_k: float
    ndcg_at_k: float
    evaluated_users: int


def split_last_rating_per_user(ratings: Iterable[MovieLensRating]) -> TemporalSplit:
    """Hold out each user's latest rating, using movie ID as a stable timestamp tie-break."""
    by_user: dict[int, list[MovieLensRating]] = {}
    for rating in ratings:
        by_user.setdefault(rating.user_id, []).append(rating)
    train: list[MovieLensRating] = []
    test: list[MovieLensRating] = []
    for user_ratings in by_user.values():
        ordered = sorted(user_ratings, key=lambda rating: (rating.timestamp, rating.movie_id))
        if len(ordered) > 1:
            train.extend(ordered[:-1])
            test.append(ordered[-1])
    return TemporalSplit(train=train, test=test)


def score_rankings(
    recommendations: dict[int, list[str]],
    test_ratings: Iterable[MovieLensRating],
    title_ids: dict[int, str],
    k: int = 12,
) -> RankingMetrics:
    """Macro-average top-K metrics for users with one relevant held-out title."""
    if k < 1:
        raise ValueError("k must be at least 1")
    scores: list[tuple[float, float, float]] = []
    for rating in test_ratings:
        relevant = title_ids.get(rating.movie_id)
        if rating.rating < 3.5 or relevant is None:
            continue
        ranked = recommendations.get(rating.user_id, [])[:k]
        if relevant not in ranked:
            scores.append((0.0, 0.0, 0.0))
            continue
        rank = ranked.index(relevant) + 1
        scores.append((1 / k, 1.0, 1 / log2(rank + 1)))
    if not scores:
        return RankingMetrics(0.0, 0.0, 0.0, 0)
    return RankingMetrics(
        precision_at_k=sum(score[0] for score in scores) / len(scores),
        recall_at_k=sum(score[1] for score in scores) / len(scores),
        ndcg_at_k=sum(score[2] for score in scores) / len(scores),
        evaluated_users=len(scores),
    )
