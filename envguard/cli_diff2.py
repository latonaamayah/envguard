"""CLI command: envguard diff2 — structural diff of two .env files."""
from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file_safe, EnvFileNotFoundError, EnvParseError
from envguard.differ2 import struct_diff


def build_diff2_parser(sub=None) -> argparse.ArgumentParser:
    description = "Show structural diff between two .env files."
    if sub is not None:
        parser = sub.add_parser("diff2", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard diff2", description=description)
    parser.add_argument("left", help="Base .env file")
    parser.add_argument("right", help="Target .env file")
    parser.add_argument(
        "--no-unchanged",
        action="store_true",
        default=False,
        help="Suppress unchanged entries from output",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit 1 if any differences are found",
    )
    return parser


def run_diff2(args: argparse.Namespace) -> int:
    try:
        left_env = load_env_file_safe(args.left)
        right_env = load_env_file_safe(args.right)
    except (EnvFileNotFoundError, EnvParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = struct_diff(left_env, right_env)

    for entry in result.entries:
        if args.no_unchanged and entry.status == "unchanged":
            continue
        prefix = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}.get(
            entry.status, " "
        )
        print(f"{prefix} {entry.message}")

    print()
    print(result.summary())

    if args.strict and result.has_changes:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_diff2_parser()
    args = parser.parse_args()
    sys.exit(run_diff2(args))


if __name__ == "__main__":  # pragma: no cover
    main()
