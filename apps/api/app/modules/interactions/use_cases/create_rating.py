"""Create a user's immutable rating for one title."""

from uuid import UUID

from app.modules.interactions.domain import (
    DuplicateRatingError,
    InvalidRatingError,
    rating_is_valid,
)
from app.modules.interactions.ports import InteractionRepository
from app.modules.interactions.use_cases._titles import require_title


class CreateRating:
    def __init__(self, repository: InteractionRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID, title_id: UUID, value: float) -> None:
        require_title(self._repository, title_id)
        if not rating_is_valid(value):
            raise InvalidRatingError
        if self._repository.rating_exists(user_id, title_id):
            raise DuplicateRatingError
        self._repository.create_rating(user_id, title_id, value)
