from recsys.evaluation.ranking import score_rankings, split_last_rating_per_user
from recsys.ingestion.movielens import MovieLensRating


def test_temporal_split_holds_out_latest_rating_with_stable_tie_break() -> None:
    ratings = [
        MovieLensRating(1, 2, 4.0, 10),
        MovieLensRating(1, 1, 5.0, 10),
        MovieLensRating(2, 3, 4.0, 2),
    ]

    result = split_last_rating_per_user(ratings)

    assert [(rating.user_id, rating.movie_id) for rating in result.train] == [(1, 1)]
    assert [(rating.user_id, rating.movie_id) for rating in result.test] == [(1, 2)]


def test_ranking_metrics_use_relevant_held_out_titles_only() -> None:
    ratings = [
        MovieLensRating(1, 10, 4.0, 1),
        MovieLensRating(2, 11, 3.0, 1),
    ]

    result = score_rankings({1: ["other", "title-10"]}, ratings, {10: "title-10", 11: "title-11"})

    assert result.evaluated_users == 1
    assert result.precision_at_k == 1 / 12
    assert result.recall_at_k == 1.0
    assert result.ndcg_at_k == 1 / 1.584962500721156
