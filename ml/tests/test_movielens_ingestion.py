from recsys.ingestion.movielens import (
    CanonicalTitleIdentifiers,
    MovieLensLink,
    MovieLensRating,
    map_movie_links,
    select_popular_tmdb_movies,
)


def test_selects_most_rated_movies_with_tmdb_ids_deterministically() -> None:
    ratings = [
        MovieLensRating(user_id=1, movie_id=2, rating=4.0, timestamp=1),
        MovieLensRating(user_id=2, movie_id=2, rating=5.0, timestamp=2),
        MovieLensRating(user_id=3, movie_id=1, rating=4.0, timestamp=3),
        MovieLensRating(user_id=4, movie_id=3, rating=4.0, timestamp=4),
    ]
    links = {
        1: MovieLensLink(movie_id=1, imdb_id="0000001", tmdb_id=101),
        2: MovieLensLink(movie_id=2, imdb_id="0000002", tmdb_id=102),
        3: MovieLensLink(movie_id=3, imdb_id="0000003", tmdb_id=None),
    }

    selected = select_popular_tmdb_movies(ratings, links, limit=2)

    assert selected == [102, 101]


def test_maps_imdb_then_tmdb_and_reports_unmatched_and_conflicts() -> None:
    links = {
        1: MovieLensLink(movie_id=1, imdb_id="114709", tmdb_id=862),
        2: MovieLensLink(movie_id=2, imdb_id=None, tmdb_id=863),
        3: MovieLensLink(movie_id=3, imdb_id="123", tmdb_id=864),
        4: MovieLensLink(movie_id=4, imdb_id=None, tmdb_id=None),
    }
    identifiers = [
        CanonicalTitleIdentifiers(title_id="toy-story", imdb_id="tt0114709", tmdb_id=862),
        CanonicalTitleIdentifiers(title_id="tmdb-only", imdb_id=None, tmdb_id=863),
        CanonicalTitleIdentifiers(title_id="imdb-title", imdb_id="tt0000123", tmdb_id=999),
        CanonicalTitleIdentifiers(title_id="other-title", imdb_id=None, tmdb_id=864),
    ]

    result = map_movie_links(links, identifiers)

    assert result.title_ids == {1: "toy-story", 2: "tmdb-only"}
    assert result.unmatched_movie_ids == {4}
    assert result.conflicting_movie_ids == {3}
