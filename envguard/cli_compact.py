import argparse
import sys

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.compactor import compact


def build_compact_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-compact",
        description="Compact .env file values by normalising whitespace.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--show-only-changed",
        action="store_true",
        help="Only output keys whose values changed",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line after output",
    )
    return parser


def run_compact(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = compact(env)

    for entry in result.entries:
        if args.show_only_changed and not entry.changed:
            continue
        print(f"{entry.key}={entry.compacted_value}")

    if args.summary:
        print(result.summary())

    return 0


def main() -> None:
    parser = build_compact_parser()
    args = parser.parse_args()
    sys.exit(run_compact(args))


if __name__ == "__main__":
    main()
