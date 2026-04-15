"""CLI commands for env variable pinning."""
from __future__ import annotations

import argparse
import sys

from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.pinner import pin, save_pin, load_pin


def build_pin_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard pin",
        description="Pin or verify env variable checksums.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    save_p = sub.add_parser("save", help="Save a new pin file from an env file.")
    save_p.add_argument("env_file", help="Path to the .env file.")
    save_p.add_argument("--output", default=".env.pin", help="Pin output file path.")

    check_p = sub.add_parser("check", help="Check env file against an existing pin.")
    check_p.add_argument("env_file", help="Path to the .env file.")
    check_p.add_argument("--pin", default=".env.pin", help="Pin file to compare against.")

    return parser


def run_pin(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.command == "save":
        result = pin(env)
        save_pin(result, args.output)
        print(f"Pinned {len(result.pinned)} variable(s) to {args.output}.")
        return 0

    if args.command == "check":
        try:
            existing = load_pin(args.pin)
        except FileNotFoundError:
            print(f"Error: pin file not found: {args.pin}", file=sys.stderr)
            return 2

        result = pin(env, existing)
        print(result.summary())

        if result.new_keys:
            for k in result.new_keys:
                print(f"  + {k} (new)")
        if result.changed:
            for k in result.changed:
                print(f"  ~ {k} (changed)")
        if result.removed_keys:
            for k in result.removed_keys:
                print(f"  - {k} (removed)")

        return 1 if result.has_drift() else 0

    return 0


def main() -> None:
    parser = build_pin_parser()
    args = parser.parse_args()
    sys.exit(run_pin(args))


if __name__ == "__main__":
    main()
