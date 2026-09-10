"""Behavior checks for the dependency, ranking and CLI seams changed by refactoring."""

import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.database import dispose_database_engines, get_database_engine
from app.main import app
from app.modules.catalog.dependencies import get_search_external_titles_use_case
from app.modules.catalog.domain import ExternalTitle
from app.modules.recommendations.domain import RatedTitle
from app.modules.recommendations.use_cases import GetPersonalRecommendations
from recsys import catalogue, cli
from test_recommendations_application import FakePersonalIndex, FakePersonalRepository, title


def test_api_reuses_one_engine_across_threads_and_disposes_on_shutdown(monkeypatch):
    dispose_database_engines()
    with TestClient(app):
        with ThreadPoolExecutor(max_workers=8) as workers:
            engines = list(workers.map(lambda _: get_database_engine("sqlite://"), range(16)))
        assert all(engine is engines[0] for engine in engines)
        disposed = []
        monkeypatch.setattr(engines[0], "dispose", lambda: disposed.append(True))
    assert disposed == [True]
    replacement = get_database_engine("sqlite://")
    assert replacement is not engines[0]
    dispose_database_engines()


def test_external_search_does_not_construct_vector_dependencies(monkeypatch):
    from app.modules.catalog import dependencies

    settings = SimpleNamespace(require_tmdb_api_key=lambda: "test-key", tmdb_base_url="test")
    monkeypatch.setattr(dependencies.Settings, "from_environment", lambda: settings)
    gateway = SimpleNamespace(search_titles=lambda query, kind: [])
    monkeypatch.setattr(dependencies, "TmdbClient", lambda *args: gateway)
    monkeypatch.setattr(
        dependencies, "create_semantic_index", lambda _: pytest.fail("No vectors needed")
    )
    assert get_search_external_titles_use_case().execute("Arrival", "movie") == []


def test_external_search_rest_contract():
    use_case = SimpleNamespace(
        execute=lambda query, kind: [
            ExternalTitle(
                tmdb_id=42,
                title_type="movie",
                title="Arrival",
                release_date=None,
                poster_path=None,
            )
        ]
    )
    app.dependency_overrides[get_search_external_titles_use_case] = lambda: use_case
    try:
        response = TestClient(app).get("/catalogue/tmdb-search?query=Arrival&type=movie")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "tmdbId": 42,
                "type": "movie",
                "title": "Arrival",
                "releaseDate": None,
                "posterPath": None,
            }
        ]
    }


def test_personal_profile_uses_stored_vectors_and_preserves_normalization():
    loved = title("loved", "Loved", genres=[], keywords=[])
    candidate = title("candidate", "Candidate", genres=[], keywords=[])

    class Index(FakePersonalIndex):
        def vectors(self, ids):
            return {"loved": [3.0, 4.0]}

        def embed(self, source):
            pytest.fail("Stored vectors must be reused")

        def search_profile(self, vector, title_type, limit, excluded_ids):
            assert vector == pytest.approx([0.6, 0.8])
            return super().search_profile(vector, title_type, limit, excluded_ids)

    result = GetPersonalRecommendations(
        FakePersonalRepository([RatedTitle(loved, 4.0)], [candidate]),
        Index({"movie": ["candidate"], "tv": []}),
    ).execute(object())
    assert [item.title.id for item in result.movies] == ["candidate"]


@pytest.mark.parametrize("vectors", [([1.0], [1.0, 2.0]), ([], [])])
def test_personal_profile_rejects_incompatible_embeddings(vectors):
    first = title("first", "First", genres=[], keywords=[])
    second = title("second", "Second", genres=[], keywords=[])

    class Index(FakePersonalIndex):
        def embed(self, source):
            return vectors[0] if source.id == "first" else vectors[1]

    with pytest.raises(RuntimeError, match="incompatible dimensions"):
        GetPersonalRecommendations(
            FakePersonalRepository([RatedTitle(first, 4.0), RatedTitle(second, 4.0)], []),
            Index({"movie": [], "tv": []}),
        ).execute(object())


def test_personal_results_preserve_genre_limit_and_candidate_order():
    loved = title("loved", "Loved", genres=[], keywords=[])
    candidates = [title(str(i), f"Story{i}", genres=["Drama"], keywords=[]) for i in range(5)]
    result = GetPersonalRecommendations(
        FakePersonalRepository([RatedTitle(loved, 4.0)], candidates),
        FakePersonalIndex({"movie": [item.id for item in candidates], "tv": []}),
    ).execute(object())
    assert [item.title.id for item in result.movies] == ["0", "1", "2"]


@pytest.mark.parametrize(
    "command,expected,indexed",
    [
        ("sync", {"created": 1, "updated": 0, "indexed": 2}, ["one", "two"]),
        ("index", {"scanned": 2, "indexed": 1, "skipped": 1}, ["two"]),
    ],
)
def test_cli_preserves_json_and_full_versus_missing_only_indexing(
    monkeypatch, capsys, command, expected, indexed
):
    titles = [title(name, name, genres=[], keywords=[]) for name in ["one", "two"]]
    disposed = []
    stored = []
    engine = SimpleNamespace(dispose=lambda: disposed.append(True))
    settings = SimpleNamespace(
        database_url="test", require_tmdb_api_key=lambda: "test", tmdb_base_url="test"
    )
    repository = SimpleNamespace(all_details=lambda: titles, upsert=lambda value: True)
    gateway = SimpleNamespace(
        popular_ids=lambda kind, page: [42], title_details=lambda *args: object()
    )
    index = SimpleNamespace(
        existing_ids=lambda ids: {"one"}, index=lambda value: stored.append(value.id)
    )
    monkeypatch.setattr(catalogue.Settings, "from_environment", lambda: settings)
    monkeypatch.setattr(catalogue, "create_database_engine", lambda url: engine)
    monkeypatch.setattr(catalogue, "SqlAlchemyCatalogueRepository", lambda engine: repository)
    monkeypatch.setattr(catalogue, "TmdbClient", lambda *args: gateway)
    monkeypatch.setattr(catalogue, "create_semantic_index", lambda settings: index)
    arguments = ["recsys", "catalog", command]
    if command == "sync":
        arguments.extend(["--pages", "1", "--type", "movie"])
    monkeypatch.setattr("sys.argv", arguments)
    cli.main()
    assert json.loads(capsys.readouterr().out) == expected
    assert stored == indexed
    assert disposed == [True]


def test_cli_disposes_database_after_index_failure(monkeypatch):
    disposed = []
    monkeypatch.setattr(
        catalogue.Settings, "from_environment", lambda: SimpleNamespace(database_url="test")
    )
    monkeypatch.setattr(
        catalogue,
        "create_database_engine",
        lambda _: SimpleNamespace(dispose=lambda: disposed.append(True)),
    )
    monkeypatch.setattr(catalogue, "SqlAlchemyCatalogueRepository", lambda _: object())

    def fail(settings):
        raise RuntimeError("unavailable")

    monkeypatch.setattr(catalogue, "create_semantic_index", fail)
    with pytest.raises(RuntimeError, match="unavailable"):
        catalogue.index_catalogue()
    assert disposed == [True]
