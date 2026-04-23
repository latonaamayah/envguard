"""CLI entry-point for the expander module."""
from __future__ import annotations

import argparse
import sys
from typing import Dict

from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.expander import expand


def build_expand_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-expand",
        description="Expand abbreviated env var keys to their canonical names.",
    )
    parser.add_argument("env_file", help="Path to the .env file to expand.")
    parser.add_argument(
        "--map",
        metavar="ABBREV=CANONICAL",
        action="append",
        default=[],
        help="Expansion mapping, e.g. DB_PWD=DB_PASSWORD. May be repeated.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any expansions were performed.",
    )
    return parser


def _parse_mapping(pairs: list) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid mapping pair: {pair!r}. Expected ABBREV=CANONICAL.")
        abbrev, canonical = pair.split("=", 1)
        mapping[abbrev.strip()] = canonical.strip()
    return mapping


def run_expand(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        mapping = _parse_mapping(args.map)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = expand(env, mapping)

    for key, value in result.as_dict().items():
        print(f"{key}={value}")

    if result.has_expansions():
        print(f"# {result.summary()}", file=sys.stderr)
        if args.strict:
            return 1

    return 0


def main() -> None:  # pragma: no cover
    parser = build_expand_parser()
    args = parser.parse_args()
    sys.exit(run_expand(args))


if __name__ == "__main__":  # pragma: no cover
    main()
