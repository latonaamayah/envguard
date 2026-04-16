from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envguard.freezer import freeze, load_freeze, save_freeze
from envguard.loader import EnvFileNotFoundError, load_env_file_safe


def build_freeze_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-freeze",
        description="Freeze .env variable checksums to detect future drift.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--output", "-o", default=".env.freeze", help="Output freeze file path"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current env against an existing freeze file",
    )
    parser.add_argument(
        "--freeze-file",
        default=".env.freeze",
        help="Existing freeze file to check against (used with --check)",
    )
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Specific keys to freeze (default: all)",
    )
    return parser


def run_freeze(args: argparse.Namespace) -> int:
    result, error = load_env_file_safe(args.env_file)
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.check:
        try:
            frozen = load_freeze(args.freeze_file)
        except FileNotFoundError:
            print(f"error: freeze file not found: {args.freeze_file}", file=sys.stderr)
            return 2
        drifted = frozen.drifted(result)
        if drifted:
            print(f"drift detected in {len(drifted)} key(s):")
            for key in drifted:
                print(f"  ! {key}")
            return 1
        print("no drift detected.")
        return 0

    freeze_result = freeze(result, keys=args.keys)
    save_freeze(freeze_result, args.output)
    print(f"frozen {len(freeze_result.entries)} key(s) to {args.output}")
    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_freeze_parser()
    args = parser.parse_args(argv)
    sys.exit(run_freeze(args))


if __name__ == "__main__":
    main()
