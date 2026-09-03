"""Return semantically related canonical titles."""

from app.modules.recommendations.domain import SimilarTitle, similarity_reason, to_title_summary
from app.modules.recommendations.ports import SemanticTitleIndex, SimilarityCatalogue


class GetSimilarTitles:
    """Keep vector lookup and explanation details behind one small action."""

    def __init__(self, catalogue: SimilarityCatalogue, index: SemanticTitleIndex) -> None:
        self._catalogue = catalogue
        self._index = index

    def execute(self, title_id: str) -> list[SimilarTitle] | None:
        source = self._catalogue.details(title_id)
        if source is None:
            return None
        candidates = [
            candidate
            for candidate_id in self._index.similar(source, limit=12)
            if candidate_id != source.id
            if (candidate := self._catalogue.details(candidate_id)) is not None
        ]
        return [
            SimilarTitle(
                title=to_title_summary(candidate), reason=similarity_reason(source, candidate)
            )
            for candidate in candidates
        ]
