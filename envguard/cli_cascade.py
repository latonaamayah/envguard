from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envguard.cascader import cascade
from envguard.loader import load_env_file_safe


def build_cascade_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard cascade",
        description="Merge multiple .env files in cascade order (later files override earlier).",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to cascade (first = lowest priority).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any overrides are detected.",
    )
    parser.add_argument(
        "--show-overrides",
        action="store_true",
        default=False,
        help="Print keys that were overridden during cascading.",
    )
    return parser


def run_cascade(args: argparse.Namespace) -> int:
    layers = []
    names = []

    for path in args.files:
        env, err = load_env_file_safe(path)
        if err is not None:
            print(f"[error] {err}", file=sys.stderr)
            return 2
        layers.append(env)
        names.append(path)

    result = cascade(layers, layer_names=names)

    if args.show_overrides and result.has_overrides:
        print("[overrides]")
        for key in result.overridden_keys:
            entry = next(
                e for e in result.entries if e.key == key and e.was_overridden
            )
            print(f"  {entry.message}")

    print("[merged]")
    for key, value in sorted(result.merged.items()):
        print(f"  {key}={value}")

    print(result.summary())

    if args.strict and result.has_overrides:
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_cascade_parser()
    args = parser.parse_args(argv)
    sys.exit(run_cascade(args))


if __name__ == "__main__":
    main()
