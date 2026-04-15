"""CLI entry-point for the sort sub-command."""
from __future__ import annotations

import argparse
import sys

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.sorter import sort


def build_sort_parser(parent: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    parser = parent or argparse.ArgumentParser(
        prog="envguard sort",
        description="Sort variables in a .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file to sort.")
    parser.add_argument(
        "--strategy",
        choices=["alpha", "group", "length"],
        default="alpha",
        help="Sorting strategy (default: alpha).",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse the sort order.",
    )
    parser.add_argument(
        "--groups",
        nargs="*",
        metavar="PREFIX",
        help="Ordered group prefixes for the 'group' strategy (e.g. APP DB LOG).",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write sorted output back to the source file.",
    )
    return parser


def run_sort(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 2

    result = sort(env, strategy=args.strategy, reverse=args.reverse, groups=args.groups)
    print(result.summary)

    lines = [f"{k}={v}" for k, v in result.sorted_vars.items()]
    output = "\n".join(lines) + "\n"

    if args.in_place:
        with open(args.env_file, "w") as fh:
            fh.write(output)
        print(f"Written to {args.env_file}")
    else:
        print(output, end="")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_sort_parser()
    args = parser.parse_args()
    sys.exit(run_sort(args))


if __name__ == "__main__":  # pragma: no cover
    main()
