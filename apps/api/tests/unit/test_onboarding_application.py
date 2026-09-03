from uuid import UUID, uuid4

from app.modules.onboarding.domain import OnboardingTitle
from app.modules.onboarding.use_cases.get_onboarding import GetOnboarding


class FakeRandomizer:
    def shuffle(self, items: list[OnboardingTitle]) -> None:
        items.reverse()


class IdentityRandomizer:
    def shuffle(self, items: list[OnboardingTitle]) -> None:
        return None


class FakeOnboardingRepository:
    def __init__(self, ratings: int) -> None:
        self.ratings = ratings
        self.titles = {
            "movie": [_title(index, "movie") for index in range(14)],
            "tv": [_title(index, "tv") for index in range(14)],
        }

    def rating_count(self, user_id: UUID) -> int:
        return self.ratings

    def popular_unrated_titles(
        self, user_id: UUID, title_type: str, limit: int
    ) -> list[OnboardingTitle]:
        assert limit == 120
        return list(self.titles[title_type])


def _title(index: int, title_type: str) -> OnboardingTitle:
    return OnboardingTitle(
        id=f"{title_type}-{index}",
        title=f"{title_type} {index}",
        title_type=title_type,  # type: ignore[arg-type]
        release_date=f"{2000 + index}-01-01",
        original_language="en",
        poster_path=None,
        popularity=float(index),
        genres=[f"Genre {index}"],
    )


def test_onboarding_reports_progress_and_selects_varied_titles_per_type() -> None:
    progress = GetOnboarding(FakeOnboardingRepository(ratings=9), FakeRandomizer()).execute(uuid4())

    assert progress.ratings_recorded == 9
    assert progress.ratings_remaining == 1
    assert not progress.is_complete
    assert len(progress.movies) == 12
    assert len(progress.tv_series) == 12
    assert len({title.id for title in progress.movies}) == 12
    assert {title.title_type for title in progress.movies} == {"movie"}
    assert {title.title_type for title in progress.tv_series} == {"tv"}


def test_onboarding_is_complete_after_at_least_ten_ratings() -> None:
    progress = GetOnboarding(FakeOnboardingRepository(ratings=11), FakeRandomizer()).execute(
        uuid4()
    )

    assert progress.is_complete
    assert progress.ratings_remaining == 0


def test_selection_prefers_new_genres_and_known_new_decades() -> None:
    repository = FakeOnboardingRepository(ratings=0)
    repository.titles["movie"] = [
        _candidate("first", ["Drama"], "2000-01-01"),
        _candidate("missing-year", ["Drama"], None),
        _candidate("new-decade", ["Drama"], "2010-01-01"),
        _candidate("new-genre", ["Comedy"], "2000-01-01"),
    ]
    repository.titles["tv"] = []

    progress = GetOnboarding(repository, IdentityRandomizer()).execute(uuid4())

    assert [title.id for title in progress.movies] == [
        "first",
        "new-genre",
        "new-decade",
        "missing-year",
    ]


def _candidate(title_id: str, genres: list[str], release_date: str | None) -> OnboardingTitle:
    return OnboardingTitle(
        id=title_id,
        title=title_id,
        title_type="movie",
        release_date=release_date,
        original_language="en",
        poster_path=None,
        popularity=1.0,
        genres=genres,
    )
