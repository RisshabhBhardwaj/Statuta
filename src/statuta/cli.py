"""Small, dependency-free public CLI for safe local inspection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from statuta.corpus import released_ruleset_paths, validate_catalog
from statuta.scenarios import generate_contexts


def main() -> None:
    parser = argparse.ArgumentParser(prog="statuta")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("scenarios-generate")
    generate.add_argument("--seed", type=int, required=True)
    generate.add_argument("--count", type=int, required=True)
    catalog = subparsers.add_parser("catalog")
    catalog.add_argument("--path", type=Path, default=Path("corpus/catalog.json"))
    args = parser.parse_args()
    if args.command == "scenarios-generate":
        print(json.dumps(generate_contexts(args.seed, args.count), indent=2))
        return
    loaded = json.loads(args.path.read_text())
    validate_catalog(loaded)
    print(
        json.dumps(
            {"released_rulesets": released_ruleset_paths(loaded), "status": loaded["status"]}
        )
    )
