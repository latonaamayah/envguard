"""CLI sub-command: patch a .env file with key=value overrides."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.patcher import patch


def build_patch_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Patch a .env file with one or more KEY=VALUE overrides."
    if subparsers is not None:
        parser = subparsers.add_parser("patch", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard-patch", description=description)
    parser.add_argument("env_file", help="Path to the .env file to patch")
    parser.add_argument(
        "overrides",
        nargs="+",
        metavar="KEY=VALUE",
        help="One or more KEY=VALUE pairs to apply",
    )
    parser.add_argument(
        "--in-place", action="store_true", help="Write result back to the source file"
    )
    return parser


def _parse_overrides(overrides: List[str]) -> dict:
    result = {}
    for item in overrides:
        if "=" not in item:
            print(f"[error] Invalid override (expected KEY=VALUE): {item}", file=sys.stderr)
            sys.exit(2)
        key, _, value = item.partition("=")
        result[key.strip()] = value
    return result


def run_patch(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except (EnvFileNotFoundError, EnvParseError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    updates = _parse_overrides(args.overrides)
    result = patch(env, updates)

    output_lines = [f"{k}={v}" for k, v in result.patched.items()]
    output = "\n".join(output_lines) + "\n"

    if getattr(args, "in_place", False):
        with open(args.env_file, "w") as fh:
            fh.write(output)
        print(f"[ok] Patched {args.env_file} — {result.summary()}")
    else:
        print(output, end="")

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_patch_parser()
    args = parser.parse_args(argv)
    sys.exit(run_patch(args))


if __name__ == "__main__":
    main()
