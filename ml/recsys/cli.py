"""Console interface for reproducible recommendation-system workflows."""

import argparse
import json
import sys
from pathlib import Path

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
    catalogue_commands.add_parser("index", help="index local catalogue titles missing from Qdrant")
    arguments = parser.parse_args()

    if arguments.command == "diagnostics":
        print(json.dumps({"status": "ok", "python": sys.version.split()[0]}))
    else:
        if arguments.catalogue_command == "sync" and arguments.pages < 1:
            parser.error("--pages must be at least 1")
        # The console package is run from this monorepo, where the API owns use cases.
        if str(API_SOURCE_ROOT) not in sys.path:
            sys.path.insert(0, str(API_SOURCE_ROOT))
        from recsys.catalogue import index_catalogue, sync_catalogue

        if arguments.catalogue_command == "sync":
            result = sync_catalogue(arguments.title_type, arguments.pages)
        else:
            result = index_catalogue()
        print(json.dumps(result))
