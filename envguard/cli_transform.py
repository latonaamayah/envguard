"""CLI entry point for the envguard transform command."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.transformer import transform


def build_transform_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard transform",
        description="Apply value transformations to an .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file.")
    parser.add_argument(
        "--rule",
        dest="rules",
        metavar="KEY=RULE",
        action="append",
        default=[],
        help="Transformation rule in KEY=RULE format. Can be repeated.",
    )
    parser.add_argument(
        "--show-only-changed",
        action="store_true",
        default=False,
        help="Only output keys whose values changed.",
    )
    return parser


def _parse_rules(raw: List[str]) -> dict:
    rules = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Invalid rule format (expected KEY=RULE): {item}")
        key, rule = item.split("=", 1)
        rules[key.strip()] = rule.strip()
    return rules


def run_transform(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        err.write(f"Error: {exc}\n")
        return 2

    try:
        rules = _parse_rules(args.rules)
    except argparse.ArgumentTypeError as exc:
        err.write(f"Error: {exc}\n")
        return 2

    result = transform(env, rules)

    entries = [e for e in result.entries if e.changed] if args.show_only_changed else result.entries

    if not entries and not args.show_only_changed:
        for key, value in result.vars.items():
            out.write(f"{key}={value}\n")
    else:
        for entry in entries:
            out.write(f"{entry.key}={entry.transformed}\n")

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_transform_parser()
    args = parser.parse_args(argv)
    sys.exit(run_transform(args))


if __name__ == "__main__":
    main()
