"""REST transport for authenticated title-library interactions."""

from typing import Annotated, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.domain import User
from app.modules.interactions.dependencies import InteractionUseCases, get_interaction_use_cases
from app.modules.interactions.domain import DuplicateRatingError, TitleNotFoundError
from app.modules.interactions.dto import (
    InteractionStatusResponse,
    LibraryResponse,
    RatingRequest,
    to_library_response,
    to_status_response,
)
from app.modules.interactions.ports import LibraryCollection

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("/titles/{title_id}", response_model=InteractionStatusResponse)
def get_title_interactions(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> InteractionStatusResponse:
    try:
        return to_status_response(use_cases.get_interaction_status.execute(user.id, title_id))
    except TitleNotFoundError as error:
        raise title_not_found() from error


@router.post("/titles/{title_id}/ratings", status_code=status.HTTP_201_CREATED)
def create_rating(
    title_id: UUID,
    rating: RatingRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    try:
        use_cases.create_rating.execute(user.id, title_id, rating.value)
    except DuplicateRatingError as error:
        raise HTTPException(
            status_code=409, detail="A rating already exists for this title."
        ) from error
    except TitleNotFoundError as error:
        raise title_not_found() from error
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/titles/{title_id}/ratings", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    return execute_title_action(use_cases.delete_rating.execute, user, title_id)


@router.post("/titles/{title_id}/watchlist", status_code=status.HTTP_204_NO_CONTENT)
def add_watchlist(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    return execute_title_action(use_cases.add_watchlist.execute, user, title_id)


@router.delete("/titles/{title_id}/watchlist", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    return execute_title_action(use_cases.remove_watchlist.execute, user, title_id)


@router.post("/titles/{title_id}/watched", status_code=status.HTTP_204_NO_CONTENT)
def mark_watched(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    return execute_title_action(use_cases.mark_watched.execute, user, title_id)


@router.delete("/titles/{title_id}/watched", status_code=status.HTTP_204_NO_CONTENT)
def remove_watched(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    return execute_title_action(use_cases.remove_watched.execute, user, title_id)


@router.post("/titles/{title_id}/not-interested", status_code=status.HTTP_204_NO_CONTENT)
def add_not_interested(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    return execute_title_action(use_cases.add_not_interested.execute, user, title_id)


@router.delete("/titles/{title_id}/not-interested", status_code=status.HTTP_204_NO_CONTENT)
def remove_not_interested(
    title_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> Response:
    return execute_title_action(use_cases.remove_not_interested.execute, user, title_id)


@router.get("/library/{collection}", response_model=LibraryResponse)
def get_library(
    collection: LibraryCollection,
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[InteractionUseCases, Depends(get_interaction_use_cases)],
) -> LibraryResponse:
    return to_library_response(collection, use_cases.get_library.execute(user.id, collection))


def execute_title_action(
    action: Callable[[UUID, UUID], None], user: User, title_id: UUID
) -> Response:
    try:
        action(user.id, title_id)
    except TitleNotFoundError as error:
        raise title_not_found() from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def title_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Catalogue title not found.")
