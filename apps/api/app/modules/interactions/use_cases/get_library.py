"""Read one named collection from a user's library."""

from uuid import UUID

from app.modules.interactions.domain import LibraryItem
from app.modules.interactions.ports import InteractionRepository, LibraryCollection


class GetLibrary:
    def __init__(self, repository: InteractionRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID, collection: LibraryCollection) -> list[LibraryItem]:
        return self._repository.library(user_id, collection)
