"""CLI entry point for env value validation."""
from __future__ import annotations

import argparse
import sys

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.validator_env import validate_env


def build_validate_env_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard validate-env",
        description="Validate .env file values against built-in runtime rules.",
    )
    parser.add_argument("env_file", help="Path to the .env file to validate.")
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=None,
        help="Restrict validation to specific keys.",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        metavar="N",
        help="Maximum allowed value length (default: 512).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any violations are found.",
    )
    return parser


def run_validate_env(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = validate_env(env, keys=args.keys, max_length=args.max_length)

    if result.has_violations():
        for violation in result.violations:
            print(str(violation))
        if args.strict:
            return 1
    else:
        print(result.summary())

    return 0


def main() -> None:
    parser = build_validate_env_parser()
    args = parser.parse_args()
    sys.exit(run_validate_env(args))


if __name__ == "__main__":
    main()
