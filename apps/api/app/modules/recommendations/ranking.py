"""Pure profile arithmetic and diversity rules; no database or provider calls."""

from math import sqrt

from app.modules.catalog.domain import TitleDetails

NEUTRAL_RATING = 3.0
MAX_RESULTS_PER_GENRE = 3


def profile_vector(weighted_vectors: list[tuple[float, list[float]]]) -> list[float]:
    if not weighted_vectors:
        return []
    dimensions = len(weighted_vectors[0][1])
    if dimensions == 0 or any(len(vector) != dimensions for _, vector in weighted_vectors):
        raise RuntimeError("Semantic title embeddings have incompatible dimensions.")
    profile = [
        sum(weight * vector[index] for weight, vector in weighted_vectors)
        for index in range(dimensions)
    ]
    magnitude = sqrt(sum(component * component for component in profile))
    return [component / magnitude for component in profile] if magnitude else []


def is_near_duplicate(candidate: TitleDetails, accepted: TitleDetails) -> bool:
    if candidate.title.casefold().strip() == accepted.title.casefold().strip():
        return True
    if _franchise_key(candidate.title) == _franchise_key(accepted.title):
        return True
    candidate_genres = set(candidate.genres)
    accepted_genres = set(accepted.genres)
    shared_creators = set(candidate.creators).intersection(accepted.creators)
    return bool(candidate_genres and candidate_genres == accepted_genres and shared_creators)


def _franchise_key(title: str) -> str:
    words = [word for word in title.casefold().replace(":", " ").split() if word]
    if words[:1] in (["the"], ["a"], ["an"]):
        words = words[1:]
    return " ".join(words[:2])


def fits_diversity(candidate: TitleDetails, selected: list[TitleDetails]) -> bool:
    if any(is_near_duplicate(candidate, accepted) for accepted in selected):
        return False
    return not any(
        sum(genre in accepted.genres for accepted in selected) >= MAX_RESULTS_PER_GENRE
        for genre in candidate.genres
    )
