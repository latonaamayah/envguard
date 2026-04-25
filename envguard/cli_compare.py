"""cli_compare.py — CLI entry point for comparing two .env files."""
from __future__ import annotations
import argparse
import sys

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.comparer import compare


def build_compare_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-compare",
        description="Compare two .env files and report differences.",
    )
    parser.add_argument("left", help="Path to the base .env file")
    parser.add_argument("right", help="Path to the target .env file")
    parser.add_argument(
        "--no-unchanged",
        action="store_true",
        help="Suppress unchanged keys from output",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any differences are found",
    )
    return parser


def run_compare(args: argparse.Namespace) -> int:
    try:
        left_env = load_env_file(args.left)
    except (EnvFileNotFoundError, EnvParseError) as exc:
        print(f"[error] Could not load left file: {exc}", file=sys.stderr)
        return 2

    try:
        right_env = load_env_file(args.right)
    except (EnvFileNotFoundError, EnvParseError) as exc:
        print(f"[error] Could not load right file: {exc}", file=sys.stderr)
        return 2

    include_unchanged = not args.no_unchanged
    report = compare(left_env, right_env, include_unchanged=include_unchanged)

    for change in report.changes:
        prefix = {
            "added": "[+]",
            "removed": "[-]",
            "changed": "[~]",
            "unchanged": "[=]",
        }.get(change.status, "[?]")
        print(f"{prefix} {change.message()}")

    print()
    print(f"Summary: {report.summary()}")

    if args.strict and report.has_diff():
        return 1
    return 0


def main() -> None:
    parser = build_compare_parser()
    args = parser.parse_args()
    sys.exit(run_compare(args))


if __name__ == "__main__":
    main()
