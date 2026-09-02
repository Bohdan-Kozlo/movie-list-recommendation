"""Independently invocable user-library actions."""

from app.modules.interactions.use_cases.add_not_interested import AddNotInterested
from app.modules.interactions.use_cases.add_watchlist import AddWatchlist
from app.modules.interactions.use_cases.create_rating import CreateRating
from app.modules.interactions.use_cases.delete_rating import DeleteRating
from app.modules.interactions.use_cases.get_interaction_status import GetInteractionStatus
from app.modules.interactions.use_cases.get_library import GetLibrary
from app.modules.interactions.use_cases.mark_watched import MarkWatched
from app.modules.interactions.use_cases.remove_not_interested import RemoveNotInterested
from app.modules.interactions.use_cases.remove_watched import RemoveWatched
from app.modules.interactions.use_cases.remove_watchlist import RemoveWatchlist

__all__ = [
    "AddNotInterested",
    "AddWatchlist",
    "CreateRating",
    "DeleteRating",
    "GetInteractionStatus",
    "GetLibrary",
    "MarkWatched",
    "RemoveNotInterested",
    "RemoveWatchlist",
    "RemoveWatched",
]
