"""CLI subcommand for merging .env files."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from typing import List

from envguard.merger import merge
from envguard.loader import EnvFileNotFoundError, EnvParseError


def build_merge_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "merge",
        help="Merge multiple .env files into one (last file wins by default)",
    )
    parser.add_argument(
        "sources",
        nargs="+",
        metavar="ENV_FILE",
        help="Env files to merge in order (lowest to highest precedence)",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT_FILE",
        default=None,
        help="Write merged result to file instead of stdout",
    )
    parser.add_argument(
        "--no-override",
        action="store_true",
        default=False,
        help="First file wins on conflict instead of last",
    )
    parser.add_argument(
        "--show-conflicts",
        action="store_true",
        default=False,
        help="Print conflict details to stderr",
    )


def run_merge(args: Namespace) -> int:
    try:
        result = merge(args.sources, override=not args.no_override)
    except EnvFileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 2

    if args.show_conflicts and result.has_conflicts:
        for conflict in result.conflicts:
            print(f"[conflict] {conflict.key}:", file=sys.stderr)
            for src, val in conflict.values:
                print(f"  {src} = {val}", file=sys.stderr)
            print(f"  => using: {conflict.winning_value}", file=sys.stderr)

    lines = [f"{k}={v}" for k, v in sorted(result.merged.items())]
    output = "\n".join(lines) + "\n" if lines else ""

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
        print(result.summary())
    else:
        sys.stdout.write(output)

    return 0
