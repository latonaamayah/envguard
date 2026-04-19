from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.tokenizer import tokenize


def build_tokenize_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-tokenize",
        description="Tokenize .env values by common delimiters.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--key", metavar="KEY", help="Show tokens only for a specific key"
    )
    parser.add_argument(
        "--multi-only",
        action="store_true",
        help="Only show keys with more than one token",
    )
    return parser


def run_tokenize(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2

    result = tokenize(env)

    entries = result.entries
    if args.key:
        entries = [e for e in entries if e.key == args.key]
    if args.multi_only:
        entries = [e for e in entries if e.token_count > 1]

    for entry in entries:
        tokens_str = ", ".join(entry.tokens) if entry.tokens else "(empty)"
        print(f"{entry.key} [{entry.token_count}]: {tokens_str}")

    print()
    print(result.summary())
    return 0


def main() -> None:
    parser = build_tokenize_parser()
    args = parser.parse_args()
    sys.exit(run_tokenize(args))


if __name__ == "__main__":
    main()
