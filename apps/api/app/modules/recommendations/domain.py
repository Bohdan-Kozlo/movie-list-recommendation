"""Recommendation values independent of HTTP and vector storage."""

from dataclasses import dataclass

from app.modules.catalog.domain import TitleDetails, TitleSummary


@dataclass(frozen=True)
class SimilarTitle:
    """A canonical title together with a factual similarity reason."""

    title: TitleSummary
    reason: str


@dataclass(frozen=True)
class RatedTitle:
    """An explicit user rating paired with the canonical title it describes."""

    title: TitleDetails
    value: float


@dataclass(frozen=True)
class PersonalRecommendation:
    """A recommended title with a factual, rating-grounded explanation."""

    title: TitleSummary
    reason: str


@dataclass(frozen=True)
class PersonalRecommendations:
    """Personalized results kept separate by catalogue title type."""

    movies: list[PersonalRecommendation]
    tv_series: list[PersonalRecommendation]


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


def personal_reason(ratings: list[RatedTitle], candidate: TitleDetails) -> str:
    """Explain a personal result using one actual positive rating where possible."""
    for rated in sorted(ratings, key=lambda item: (-item.value, item.title.id)):
        if rated.value <= 3.0:
            continue
        shared_genres = sorted(set(rated.title.genres).intersection(candidate.genres))
        if shared_genres:
            return (
                f"Matches the {shared_genres[0]} genre in {rated.title.title}, "
                f"rated {rated.value:.1f}/5."
            )
        shared_keywords = sorted(set(rated.title.keywords).intersection(candidate.keywords))
        if shared_keywords:
            return (
                f"Matches the {shared_keywords[0]} theme in {rated.title.title}, "
                f"rated {rated.value:.1f}/5."
            )
        shared_creators = sorted(set(rated.title.creators).intersection(candidate.creators))
        if shared_creators:
            return (
                f"Shares creator {shared_creators[0]} with {rated.title.title}, "
                f"rated {rated.value:.1f}/5."
            )
    positive = next(
        (
            rated
            for rated in sorted(ratings, key=lambda item: (-item.value, item.title.id))
            if rated.value > 3.0
        ),
        None,
    )
    if positive is not None:
        return f"Personalized from your {positive.value:.1f}/5 rating for {positive.title.title}."
    negative = min(ratings, key=lambda item: (item.value, item.title.id), default=None)
    if negative is not None:
        return f"Balances against your {negative.value:.1f}/5 rating for {negative.title.title}."
    return "Personalized from your ratings."
