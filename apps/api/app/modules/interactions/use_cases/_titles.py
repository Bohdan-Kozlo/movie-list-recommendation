"""Shared title-existence guard for interaction use cases."""

from uuid import UUID

from app.modules.interactions.domain import TitleNotFoundError
from app.modules.interactions.ports import InteractionRepository


def require_title(repository: InteractionRepository, title_id: UUID) -> None:
    if not repository.title_exists(title_id):
        raise TitleNotFoundError
