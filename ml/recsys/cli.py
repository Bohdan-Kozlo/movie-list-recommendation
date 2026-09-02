"""Console interface for reproducible recommendation-system workflows."""

import argparse
import json
import sys


def main() -> None:
    """Run a supported recommendation-system command."""
    parser = argparse.ArgumentParser(prog="recsys")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("diagnostics", help="report the active Python runtime")
    arguments = parser.parse_args()

    if arguments.command == "diagnostics":
        print(json.dumps({"status": "ok", "python": sys.version.split()[0]}))
