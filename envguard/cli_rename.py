"""CLI sub-command: envguard rename — rename keys in a .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.renamer import rename


def build_rename_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Rename one or more keys inside a .env file."
    if subparsers is not None:
        parser = subparsers.add_parser("rename", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard rename", description=description)

    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--rename",
        metavar="OLD:NEW",
        action="append",
        dest="renames",
        required=True,
        help="Rename OLD key to NEW key (repeatable)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any key was not found",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output",
    )
    return parser


def run_rename(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    pairs: List[tuple] = []
    for item in args.renames:
        if ":" not in item:
            print(f"error: invalid rename spec '{item}' (expected OLD:NEW)", file=sys.stderr)
            return 2
        old, new = item.split(":", 1)
        pairs.append((old.strip(), new.strip()))

    result = rename(env, pairs)

    for key, value in result.output.items():
        print(f"{key}={value}")

    if not args.quiet:
        print(f"# {result.summary()}", file=sys.stderr)

    if args.strict and result.skipped:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_rename_parser()
    args = parser.parse_args()
    sys.exit(run_rename(args))


if __name__ == "__main__":  # pragma: no cover
    main()
