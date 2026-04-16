from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.scorer import score


def build_score_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard score",
        description="Score a .env file based on key/value quality heuristics.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show per-key breakdown"
    )
    return parser


def run_score(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = score(env)

    if args.verbose:
        for entry in result.entries:
            print(f"  {entry.key}: {entry.points}/10 — {entry.reason}")

    print(result.summary())
    return 0


def main() -> None:
    parser = build_score_parser()
    args = parser.parse_args()
    sys.exit(run_score(args))


if __name__ == "__main__":
    main()
