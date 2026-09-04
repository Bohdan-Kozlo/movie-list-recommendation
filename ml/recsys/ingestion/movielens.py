"""MovieLens 32M parsing, catalogue mapping, and coverage selection."""

import csv
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile


@dataclass(frozen=True)
class MovieLensRating:
    """One anonymized MovieLens rating."""

    user_id: int
    movie_id: int
    rating: float
    timestamp: int


@dataclass(frozen=True)
class MovieLensLink:
    """External identifiers supplied for one MovieLens movie."""

    movie_id: int
    imdb_id: str | None
    tmdb_id: int | None


@dataclass(frozen=True)
class CanonicalTitleIdentifiers:
    """Identifiers belonging to one canonical movie title."""

    title_id: str
    imdb_id: str | None
    tmdb_id: int | None


@dataclass(frozen=True)
class MovieLinkMapping:
    """The safe MovieLens-to-canonical-title mapping outcome."""

    title_ids: dict[int, str]
    unmatched_movie_ids: set[int]
    conflicting_movie_ids: set[int]


@dataclass(frozen=True)
class MovieLensArchive:
    """Validated MovieLens source records and their immutable fingerprint."""

    ratings: list[MovieLensRating]
    links: dict[int, MovieLensLink]
    sha256: str


def read_archive(source: Path) -> MovieLensArchive:
    """Read the ratings and identifier links required from a local MovieLens ZIP."""
    if not source.is_file():
        raise ValueError(f"MovieLens source does not exist: {source}")
    digest = hashlib.file_digest(source.open("rb"), "sha256").hexdigest()
    with ZipFile(source) as archive:
        names = {Path(name).name: name for name in archive.namelist()}
        required = {"ratings.csv", "links.csv"}
        missing = required.difference(names)
        if missing:
            raise ValueError(f"MovieLens ZIP is missing: {', '.join(sorted(missing))}")
        ratings = [
            MovieLensRating(
                user_id=int(row["userId"]),
                movie_id=int(row["movieId"]),
                rating=float(row["rating"]),
                timestamp=int(row["timestamp"]),
            )
            for row in _rows(
                archive, names["ratings.csv"], {"userId", "movieId", "rating", "timestamp"}
            )
        ]
        links = {
            int(row["movieId"]): MovieLensLink(
                movie_id=int(row["movieId"]),
                imdb_id=row["imdbId"] or None,
                tmdb_id=int(row["tmdbId"]) if row["tmdbId"] else None,
            )
            for row in _rows(archive, names["links.csv"], {"movieId", "imdbId", "tmdbId"})
        }
    return MovieLensArchive(ratings=ratings, links=links, sha256=digest)


def archive_fingerprint(source: Path) -> str:
    """Return a content fingerprint without retaining source rows in memory."""
    with source.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def read_links(source: Path) -> dict[int, MovieLensLink]:
    """Read MovieLens links.csv from a validated local archive."""
    with ZipFile(source) as archive:
        names = {Path(name).name: name for name in archive.namelist()}
        if "links.csv" not in names:
            raise ValueError("MovieLens ZIP is missing: links.csv")
        return {
            int(row["movieId"]): MovieLensLink(
                movie_id=int(row["movieId"]),
                imdb_id=row["imdbId"] or None,
                tmdb_id=int(row["tmdbId"]) if row["tmdbId"] else None,
            )
            for row in _rows(archive, names["links.csv"], {"movieId", "imdbId", "tmdbId"})
        }


def iter_ratings(source: Path) -> Iterable[MovieLensRating]:
    """Stream MovieLens ratings so the 32M archive need not fit in memory."""
    with ZipFile(source) as archive:
        names = {Path(name).name: name for name in archive.namelist()}
        if "ratings.csv" not in names:
            raise ValueError("MovieLens ZIP is missing: ratings.csv")
        for row in _rows(
            archive, names["ratings.csv"], {"userId", "movieId", "rating", "timestamp"}
        ):
            yield MovieLensRating(
                user_id=int(row["userId"]),
                movie_id=int(row["movieId"]),
                rating=float(row["rating"]),
                timestamp=int(row["timestamp"]),
            )


def write_mapped_ratings(
    destination: Path, archive: MovieLensArchive, mapping: MovieLinkMapping
) -> Path:
    """Write only product-displayable ratings and a reproducibility report."""
    destination.mkdir(parents=True, exist_ok=True)
    ratings_path = destination / "ratings.csv"
    with ratings_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output, fieldnames=["user_id", "movie_id", "title_id", "rating", "timestamp"]
        )
        writer.writeheader()
        for rating in archive.ratings:
            title_id = mapping.title_ids.get(rating.movie_id)
            if title_id:
                writer.writerow(
                    {
                        "user_id": rating.user_id,
                        "movie_id": rating.movie_id,
                        "title_id": title_id,
                        "rating": rating.rating,
                        "timestamp": rating.timestamp,
                    }
                )
    report = {
        "dataset": "movielens-32m",
        "sha256": archive.sha256,
        "sourceRatings": len(archive.ratings),
        "mappedRatings": sum(rating.movie_id in mapping.title_ids for rating in archive.ratings),
        "mappedMovies": len(mapping.title_ids),
        "unmatchedMovies": len(mapping.unmatched_movie_ids),
        "conflictingMovies": len(mapping.conflicting_movie_ids),
    }
    (destination / "metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return ratings_path


def write_mapped_ratings_from_source(
    source: Path, destination: Path, links: dict[int, MovieLensLink], mapping: MovieLinkMapping
) -> Path:
    """Stream a MovieLens archive into a product-safe intermediate dataset."""
    destination.mkdir(parents=True, exist_ok=True)
    ratings_path = destination / "ratings.csv"
    source_ratings = mapped_ratings = 0
    with ratings_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output, fieldnames=["user_id", "movie_id", "title_id", "rating", "timestamp"]
        )
        writer.writeheader()
        for rating in iter_ratings(source):
            source_ratings += 1
            title_id = mapping.title_ids.get(rating.movie_id)
            if title_id:
                mapped_ratings += 1
                writer.writerow(
                    {
                        "user_id": rating.user_id,
                        "movie_id": rating.movie_id,
                        "title_id": title_id,
                        "rating": rating.rating,
                        "timestamp": rating.timestamp,
                    }
                )
    report = {
        "dataset": "movielens-32m",
        "sha256": archive_fingerprint(source),
        "sourceRatings": source_ratings,
        "mappedRatings": mapped_ratings,
        "mappedMovies": len(mapping.title_ids),
        "unmatchedMovies": len(mapping.unmatched_movie_ids),
        "conflictingMovies": len(mapping.conflicting_movie_ids),
        "linkedMovies": len(links),
    }
    (destination / "metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return ratings_path


def select_popular_tmdb_movies(
    ratings: Iterable[MovieLensRating], links: dict[int, MovieLensLink], limit: int
) -> list[int]:
    """Return distinct linked TMDB movie IDs ordered by MovieLens rating support."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    counts = Counter(rating.movie_id for rating in ratings)
    eligible = [
        (movie_id, count)
        for movie_id, count in counts.items()
        if movie_id in links and links[movie_id].tmdb_id is not None
    ]
    selected = sorted(eligible, key=lambda item: (-item[1], item[0]))[:limit]
    tmdb_ids: list[int] = []
    for movie_id, _ in selected:
        tmdb_id = links[movie_id].tmdb_id
        if tmdb_id is not None:
            tmdb_ids.append(tmdb_id)
    return tmdb_ids


def map_movie_links(
    links: dict[int, MovieLensLink], identifiers: Iterable[CanonicalTitleIdentifiers]
) -> MovieLinkMapping:
    """Map MovieLens movies only when IMDb and TMDB identifiers agree."""
    imdb_titles = {
        _normalize_imdb(identifier.imdb_id): identifier.title_id
        for identifier in identifiers
        if identifier.imdb_id
    }
    tmdb_titles = {
        identifier.tmdb_id: identifier.title_id for identifier in identifiers if identifier.tmdb_id
    }
    title_ids: dict[int, str] = {}
    unmatched: set[int] = set()
    conflicts: set[int] = set()
    for movie_id, link in links.items():
        imdb_title = imdb_titles.get(_normalize_imdb(link.imdb_id)) if link.imdb_id else None
        tmdb_title = tmdb_titles.get(link.tmdb_id) if link.tmdb_id else None
        if imdb_title and tmdb_title and imdb_title != tmdb_title:
            conflicts.add(movie_id)
        elif imdb_title or tmdb_title:
            title_id = imdb_title if imdb_title is not None else tmdb_title
            assert title_id is not None
            title_ids[movie_id] = title_id
        else:
            unmatched.add(movie_id)
    return MovieLinkMapping(title_ids, unmatched, conflicts)


def _normalize_imdb(value: str | None) -> str | None:
    if not value:
        return None
    digits = value.strip().lower().removeprefix("tt")
    if not digits.isdigit():
        return None
    return f"tt{int(digits):07d}"


def _rows(archive: ZipFile, name: str, required: set[str]) -> Iterable[dict[str, str]]:
    with archive.open(name, "r") as file:
        reader = csv.DictReader((line.decode("utf-8") for line in file))
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"MovieLens file {Path(name).name} has an invalid header")
        yield from reader
