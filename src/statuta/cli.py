"""Small, dependency-free public CLI for safe local inspection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from statuta.corpus import coverage_summary, released_ruleset_paths, validate_catalog
from statuta.log.merkle import MerkleTree
from statuta.log.storage import append_leaf, read_leaves
from statuta.scenarios import generate_contexts


def main() -> None:
    parser = argparse.ArgumentParser(prog="statuta")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("scenarios-generate")
    generate.add_argument("--seed", type=int, required=True)
    generate.add_argument("--count", type=int, required=True)
    catalog = subparsers.add_parser("catalog")
    catalog.add_argument("--path", type=Path, default=Path("corpus/catalog.json"))
    log_append = subparsers.add_parser("log-append")
    log_append.add_argument("--path", type=Path, required=True)
    log_append.add_argument("--opaque-event", required=True)
    log_root = subparsers.add_parser("log-checkpoint")
    log_root.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "scenarios-generate":
        print(json.dumps(generate_contexts(args.seed, args.count), indent=2))
        return
    if args.command == "log-append":
        print(json.dumps({"index": append_leaf(args.path, args.opaque_event.encode())}))
        return
    if args.command == "log-checkpoint":
        leaves = read_leaves(args.path)
        print(
            json.dumps({"tree_size": len(leaves), "root_hash": MerkleTree(leaves).root_hash.hex()})
        )
        return
    loaded = json.loads(args.path.read_text())
    validate_catalog(loaded)
    print(
        json.dumps(
            {
                "released_rulesets": released_ruleset_paths(loaded),
                "status": loaded["status"],
                "coverage": coverage_summary(loaded),
            }
        )
    )
