"""Composition root for user-library interaction use cases."""

from dataclasses import dataclass

from app.adapters.postgres.interaction_repository import SqlAlchemyInteractionRepository
from app.core.config import Settings
from app.core.database import get_database_engine
from app.modules.interactions.use_cases import (
    AddNotInterested,
    AddWatchlist,
    CreateRating,
    DeleteRating,
    GetInteractionStatus,
    GetLibrary,
    MarkWatched,
    RemoveNotInterested,
    RemoveWatched,
    RemoveWatchlist,
)


@dataclass(frozen=True)
class InteractionUseCases:
    create_rating: CreateRating
    delete_rating: DeleteRating
    add_watchlist: AddWatchlist
    remove_watchlist: RemoveWatchlist
    mark_watched: MarkWatched
    remove_watched: RemoveWatched
    add_not_interested: AddNotInterested
    remove_not_interested: RemoveNotInterested
    get_interaction_status: GetInteractionStatus
    get_library: GetLibrary


def get_interaction_use_cases() -> InteractionUseCases:
    return configured_interaction_use_cases(Settings.from_environment().database_url)


def configured_interaction_use_cases(database_url: str) -> InteractionUseCases:
    repository = SqlAlchemyInteractionRepository(get_database_engine(database_url))
    return InteractionUseCases(
        create_rating=CreateRating(repository),
        delete_rating=DeleteRating(repository),
        add_watchlist=AddWatchlist(repository),
        remove_watchlist=RemoveWatchlist(repository),
        mark_watched=MarkWatched(repository),
        remove_watched=RemoveWatched(repository),
        add_not_interested=AddNotInterested(repository),
        remove_not_interested=RemoveNotInterested(repository),
        get_interaction_status=GetInteractionStatus(repository),
        get_library=GetLibrary(repository),
    )
