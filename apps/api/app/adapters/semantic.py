"""Composition of Ollama embeddings and Qdrant vector persistence."""

from app.adapters.ollama.client import OllamaEmbeddingClient
from app.adapters.qdrant.client import QdrantClient
from app.core.config import Settings
from app.modules.catalog.domain import TitleDetails


class SemanticTitleIndexer:
    """Build stable title text and keep its derived Qdrant point current."""

    def __init__(self, embeddings: OllamaEmbeddingClient, vectors: QdrantClient) -> None:
        self._embeddings = embeddings
        self._vectors = vectors

    def index(self, title: TitleDetails) -> None:
        vector = self._embeddings.embed(self._text(title))
        self._vectors.upsert(title.id, vector, self._payload(title))

    def existing_ids(self, title_ids: list[str]) -> set[str]:
        return self._vectors.existing_ids(title_ids)

    def similar(self, source: TitleDetails, limit: int) -> list[str]:
        return self._vectors.search(self.embed(source), limit=limit, excluded_id=source.id)

    def embed(self, title: TitleDetails) -> list[float]:
        return self._embeddings.embed(self._text(title))

    def vectors(self, title_ids: list[str]) -> dict[str, list[float]]:
        return self._vectors.vectors(title_ids)

    def search_profile(
        self, vector: list[float], title_type: str, limit: int, excluded_ids: set[str]
    ) -> list[str]:
        return self._vectors.search(
            vector, limit=limit, title_type=title_type, excluded_ids=excluded_ids
        )

    @staticmethod
    def _text(title: TitleDetails) -> str:
        cast_names = [member["name"] for member in title.cast if member.get("name")]
        sections = [
            f"Title: {title.title}",
            f"Type: {title.title_type}",
            f"Year: {title.release_date.year}" if title.release_date else "",
            f"Overview: {title.overview}" if title.overview else "",
            f"Genres: {', '.join(title.genres)}" if title.genres else "",
            f"Keywords: {', '.join(title.keywords)}" if title.keywords else "",
            f"Cast: {', '.join(cast_names)}" if cast_names else "",
            f"Creators: {', '.join(title.creators)}" if title.creators else "",
        ]
        return "\n".join(section for section in sections if section)

    @staticmethod
    def _payload(title: TitleDetails) -> dict[str, object]:
        return {
            "title_id": title.id,
            "tmdb_id": title.tmdb_id,
            "type": title.title_type,
            "genres": title.genres,
            "year": title.release_date.year if title.release_date else None,
        }


def create_semantic_index(settings: Settings) -> SemanticTitleIndexer:
    """Assemble the same embedding configuration for HTTP and CLI callers."""
    return SemanticTitleIndexer(
        OllamaEmbeddingClient(settings.ollama_base_url, settings.ollama_embedding_model),
        QdrantClient(
            settings.require_qdrant_url(),
            settings.require_qdrant_api_key(),
            settings.qdrant_collection,
        ),
    )
