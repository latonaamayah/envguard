"""CLI sub-command: envguard duplicates — find duplicate keys in .env files."""
from __future__ import annotations

import argparse
import sys

from envguard.duplicates import find_duplicates


def build_duplicates_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Detect duplicate keys within one or more .env files."
    if subparsers is not None:
        parser = subparsers.add_parser("duplicates", help=description)
    else:
        parser = argparse.ArgumentParser(
            prog="envguard-duplicates",
            description=description,
        )
    parser.add_argument(
        "env_files",
        nargs="+",
        metavar="ENV_FILE",
        help="One or more .env files to scan.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any duplicates are found (default: 0).",
    )
    return parser


def run_duplicates(args: argparse.Namespace) -> int:
    """Execute the duplicates command; returns an exit code."""
    try:
        result = find_duplicates(*args.env_files)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(result.summary())

    if args.strict and result.has_duplicates:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_duplicates_parser()
    args = parser.parse_args()
    sys.exit(run_duplicates(args))


if __name__ == "__main__":  # pragma: no cover
    main()
