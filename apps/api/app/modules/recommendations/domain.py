"""Recommendation values independent of HTTP and vector storage."""

from dataclasses import dataclass

from app.modules.catalog.domain import TitleDetails, TitleSummary


@dataclass(frozen=True)
class SimilarTitle:
    """A canonical title together with a factual similarity reason."""

    title: TitleSummary
    reason: str


def to_title_summary(title: TitleDetails) -> TitleSummary:
    """Project a canonical detail record into the recommendation card shape."""
    return TitleSummary(
        id=title.id,
        title=title.title,
        title_type=title.title_type,
        release_date=title.release_date,
        original_language=title.original_language,
        poster_path=title.poster_path,
        popularity=title.popularity,
        genres=title.genres,
    )


def similarity_reason(source: TitleDetails, candidate: TitleDetails) -> str:
    """Explain similarity from actual shared indexed metadata when available."""
    shared_genres = sorted(set(source.genres).intersection(candidate.genres))
    if shared_genres:
        return f"Shares the {shared_genres[0]} genre."
    shared_keywords = sorted(set(source.keywords).intersection(candidate.keywords))
    if shared_keywords:
        return f"Shares the {shared_keywords[0]} theme."
    shared_creators = sorted(set(source.creators).intersection(candidate.creators))
    if shared_creators:
        return f"Also created by {shared_creators[0]}."
    source_cast = {member["name"] for member in source.cast if member.get("name")}
    candidate_cast = {member["name"] for member in candidate.cast if member.get("name")}
    shared_cast = sorted(source_cast.intersection(candidate_cast))
    if shared_cast:
        return f"Also features {shared_cast[0]}."
    return "Similar in synopsis and indexed metadata."
