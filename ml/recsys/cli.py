"""Console interface for reproducible recommendation-system workflows."""

import argparse
import json
import sys
from pathlib import Path

from recsys.ingestion.movielens import CanonicalTitleIdentifiers

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
API_SOURCE_ROOT = REPOSITORY_ROOT / "apps" / "api"


def main() -> None:
    """Run a supported recommendation-system command."""
    parser = argparse.ArgumentParser(prog="recsys")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("diagnostics", help="report the active Python runtime")
    catalogue = commands.add_parser("catalog", help="manage the canonical title catalogue")
    catalogue_commands = catalogue.add_subparsers(dest="catalogue_command", required=True)
    sync = catalogue_commands.add_parser("sync", help="synchronize popular TMDB titles")
    sync.add_argument("--type", choices=["all", "movie", "tv"], default="all", dest="title_type")
    sync.add_argument("--pages", type=int, default=5)
    catalogue_commands.add_parser(
        "import-movielens", help="import popular MovieLens 32M movies from TMDB"
    ).add_argument("--source", type=Path, required=True)
    catalogue_commands.choices["import-movielens"].add_argument("--limit", type=int, default=5000)
    collaborative = commands.add_parser("cf", help="run collaborative-filtering workflows")
    collaborative_commands = collaborative.add_subparsers(
        dest="collaborative_command", required=True
    )
    ingest = collaborative_commands.add_parser(
        "ingest", help="map MovieLens 32M ratings to catalogue titles"
    )
    ingest.add_argument("--source", type=Path, required=True)
    train = collaborative_commands.add_parser("train", help="train and evaluate the CF baseline")
    train.add_argument("--input", type=Path, required=True)
    arguments = parser.parse_args()

    if arguments.command == "diagnostics":
        print(json.dumps({"status": "ok", "python": sys.version.split()[0]}))
    elif arguments.command == "catalog" and arguments.catalogue_command == "sync":
        if arguments.pages < 1:
            parser.error("--pages must be at least 1")
        sys.path.insert(0, str(API_SOURCE_ROOT))
        from app.adapters.ollama.client import OllamaEmbeddingClient
        from app.adapters.postgres.catalogue_repository import (
            SqlAlchemyCatalogueRepository,
        )
        from app.adapters.qdrant.client import QdrantClient
        from app.adapters.semantic import SemanticTitleIndexer
        from app.adapters.tmdb.client import TmdbClient
        from app.core.config import Settings
        from app.core.database import create_database_engine
        from app.modules.catalog.use_cases import SynchronizeCatalogue
        from app.modules.recommendations.use_cases import IndexCatalogue

        settings = Settings.from_environment()
        gateway = TmdbClient(settings.require_tmdb_api_key(), settings.tmdb_base_url)
        title_types = ["movie", "tv"] if arguments.title_type == "all" else [arguments.title_type]
        repository = SqlAlchemyCatalogueRepository(create_database_engine(settings.database_url))
        report = SynchronizeCatalogue(repository).execute(gateway, title_types, arguments.pages)
        index = SemanticTitleIndexer(
            OllamaEmbeddingClient(settings.ollama_base_url, settings.ollama_embedding_model),
            QdrantClient(
                settings.require_qdrant_url(),
                settings.require_qdrant_api_key(),
                settings.qdrant_collection,
            ),
        )
        indexed = IndexCatalogue(repository, index).execute()
        print(
            json.dumps({"created": report.created, "updated": report.updated, "indexed": indexed})
        )
    elif arguments.command == "catalog" and arguments.catalogue_command == "import-movielens":
        if arguments.limit < 1:
            parser.error("--limit must be at least 1")
        _import_movielens_catalogue(arguments.source, arguments.limit)
    elif arguments.command == "cf" and arguments.collaborative_command == "ingest":
        _ingest_movielens(arguments.source)
    elif arguments.command == "cf" and arguments.collaborative_command == "train":
        _train_collaborative_filter(arguments.input)


def _catalogue_identifiers() -> list[CanonicalTitleIdentifiers]:
    sys.path.insert(0, str(API_SOURCE_ROOT))
    from app.core.config import Settings
    from app.core.database import create_database_engine
    from app.modules.catalog.models import CatalogueTitle
    from sqlalchemy import select
    from sqlalchemy.orm import Session, selectinload


    with Session(create_database_engine(Settings.from_environment().database_url)) as session:
        titles = session.scalars(
            select(CatalogueTitle)
            .where(CatalogueTitle.title_type == "movie")
            .options(selectinload(CatalogueTitle.external_ids))
        ).all()
    return [
        CanonicalTitleIdentifiers(
            title_id=str(title.id),
            imdb_id=next(
                (item.value for item in title.external_ids if item.provider == "imdb"), None
            ),
            tmdb_id=next(
                (int(item.value) for item in title.external_ids if item.provider == "tmdb_movie"),
                None,
            ),
        )
        for title in titles
    ]


def _import_movielens_catalogue(source: Path, limit: int) -> None:
    sys.path.insert(0, str(API_SOURCE_ROOT))
    from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
    from app.adapters.tmdb.client import TmdbClient, TmdbNotFoundError
    from app.core.config import Settings
    from app.core.database import create_database_engine

    from recsys.ingestion.movielens import (
        archive_fingerprint,
        iter_ratings,
        read_links,
        select_popular_tmdb_movies,
    )

    settings = Settings.from_environment()
    repository = SqlAlchemyCatalogueRepository(create_database_engine(settings.database_url))
    gateway = TmdbClient(settings.require_tmdb_api_key(), settings.tmdb_base_url)
    selected = select_popular_tmdb_movies(iter_ratings(source), read_links(source), limit)
    created = updated = 0
    skipped: dict[str, list[int]] = {}
    for tmdb_id in selected:
        try:
            if repository.upsert(gateway.title_details("movie", tmdb_id)):
                created += 1
            else:
                updated += 1
        except TmdbNotFoundError:
            skipped.setdefault("tmdb_not_found", []).append(tmdb_id)
    report = {
        "dataset": "movielens-32m",
        "sha256": archive_fingerprint(source),
        "selectedTmdbIds": selected,
        "created": created,
        "updated": updated,
        "skipped": skipped,
    }
    destination = REPOSITORY_ROOT / "data" / "interim" / "movielens-32m" / report["sha256"]
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "catalogue-import.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report))


def _ingest_movielens(source: Path) -> None:
    from recsys.ingestion.movielens import (
        archive_fingerprint,
        map_movie_links,
        read_links,
        write_mapped_ratings_from_source,
    )

    links = read_links(source)
    mapping = map_movie_links(links, _catalogue_identifiers())
    destination = (
        REPOSITORY_ROOT / "data" / "interim" / "movielens-32m" / archive_fingerprint(source)
    )
    ratings_path = write_mapped_ratings_from_source(source, destination, links, mapping)
    print((destination / "metadata.json").read_text(encoding="utf-8"))
    print(json.dumps({"ratingsPath": str(ratings_path)}))


def _train_collaborative_filter(dataset_directory: Path) -> None:
    """Train the fixed LensKit ItemKNN baseline and register one MLflow run."""
    import pickle
    from tempfile import TemporaryDirectory

    import mlflow
    import pandas as pd
    from lenskit.batch import recommend
    from lenskit.data import from_interactions_df
    from lenskit.knn import ItemKNNConfig, ItemKNNScorer
    from lenskit.pipeline import topn_pipeline

    from recsys.evaluation.ranking import score_rankings, split_last_rating_per_user
    from recsys.ingestion.movielens import MovieLensRating

    ratings_path = dataset_directory / "ratings.csv"
    metadata_path = dataset_directory / "metadata.json"
    if not ratings_path.is_file() or not metadata_path.is_file():
        raise ValueError("--input must contain ratings.csv and metadata.json from recsys cf ingest")
    frame = pd.read_csv(ratings_path)
    ratings = [
        MovieLensRating(int(row.user_id), int(row.movie_id), float(row.rating), int(row.timestamp))
        for row in frame.itertuples(index=False)
    ]
    split = split_last_rating_per_user(ratings)
    train_users = {rating.user_id for rating in split.train}
    test = [rating for rating in split.test if rating.user_id in train_users]
    train_frame = frame[frame.user_id.isin(train_users)].copy()
    held_out = {(rating.user_id, rating.movie_id) for rating in test}
    train_frame = train_frame[
        ~train_frame.apply(lambda row: (int(row.user_id), int(row.movie_id)) in held_out, axis=1)
    ]
    pipeline = topn_pipeline(
        ItemKNNScorer(ItemKNNConfig(max_nbrs=20, min_nbrs=1)), n=12, name="item-knn"
    )
    pipeline.train(
        from_interactions_df(
            train_frame,
            user_col="user_id",
            item_col="title_id",
            rating_col="rating",
            timestamp_col="timestamp",
        )
    )
    recommendations_frame = recommend(
        pipeline, sorted({rating.user_id for rating in test}), n=12
    ).to_df()
    recommendations = {
        int(user_id): group["item_id"].astype(str).tolist()
        for user_id, group in recommendations_frame.groupby("user_id")
    }
    movie_to_title = dict(zip(frame.movie_id.astype(int), frame.title_id.astype(str), strict=True))
    metrics = score_rankings(recommendations, test, movie_to_title, k=12)
    evaluation_report = {
        "trainRatings": len(split.train),
        "testRatings": len(test),
        "trainUsers": len(train_users),
        "evaluatedUsers": metrics.evaluated_users,
        "candidateShortfalls": sum(len(items) < 12 for items in recommendations.values()),
        "metrics": metrics.__dict__,
    }
    mlflow.set_experiment("collaborative-filtering")
    with mlflow.start_run(run_name="movielens-32m-item-knn") as run:
        mlflow.log_params(
            {
                "algorithm": "ItemKNN",
                "max_neighbors": 20,
                "ranking_k": 12,
                "relevance_threshold": 3.5,
                "temporal_split": "last_rating_per_user",
            }
        )
        mlflow.log_dict(
            json.loads(metadata_path.read_text(encoding="utf-8")), "dataset/metadata.json"
        )
        mlflow.log_dict(evaluation_report, "evaluation/report.json")
        mlflow.log_metrics(
            {
                "precision_at_12": metrics.precision_at_k,
                "recall_at_12": metrics.recall_at_k,
                "ndcg_at_12": metrics.ndcg_at_k,
                "evaluated_users": metrics.evaluated_users,
            }
        )
        with TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "item-knn.pkl"
            artifact.write_bytes(pickle.dumps(pipeline))
            mlflow.log_artifact(str(artifact), "model")
        print(json.dumps({"runId": run.info.run_id, "metrics": metrics.__dict__}))
