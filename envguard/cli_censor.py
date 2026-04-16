from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file_safe
from envguard.censor import censor


def build_censor_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-censor",
        description="Censor sensitive values in a .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--keys",
        nargs="*",
        metavar="KEY",
        help="Explicit keys to censor (default: auto-detect sensitive keys)",
    )
    parser.add_argument(
        "--show-summary",
        action="store_true",
        help="Print a summary line after output",
    )
    return parser


def run_censor(args: argparse.Namespace) -> int:
    env, err = load_env_file_safe(args.env_file)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        return 2

    result = censor(env, keys=args.keys if args.keys else None)

    for entry in result.entries:
        print(f"{entry.key}={entry.censored}")

    if args.show_summary:
        print(f"\n# {result.summary()}")

    return 0


def main() -> None:
    parser = build_censor_parser()
    args = parser.parse_args()
    sys.exit(run_censor(args))


if __name__ == "__main__":
    main()
