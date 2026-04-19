from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.tracker import track


def build_track_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-track",
        description="Track changes between two .env files.",
    )
    parser.add_argument("before", help="Path to the baseline .env file")
    parser.add_argument("after", help="Path to the updated .env file")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any changes detected")
    return parser


def run_track(args: argparse.Namespace) -> int:
    try:
        before = load_env_file(args.before)
        after = load_env_file(args.after)
    except EnvFileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = track(before, after)

    if not result.has_changes():
        print("No changes detected.")
        return 0

    print(f"Changes: {result.summary()}")
    for entry in result.entries:
        print(f"  {entry.message()}")

    if args.strict and result.has_changes():
        return 1
    return 0


def main() -> None:
    parser = build_track_parser()
    args = parser.parse_args()
    sys.exit(run_track(args))


if __name__ == "__main__":
    main()
