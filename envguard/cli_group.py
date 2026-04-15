"""CLI entry point for the group subcommand."""
from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.grouper import group


def build_group_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Group environment variables by key prefix."
    if subparsers is not None:
        parser = subparsers.add_parser("group", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard group", description=description)

    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--separator",
        default="_",
        help="Separator character used to split key prefixes (default: '_')",
    )
    parser.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        dest="min_group_size",
        help="Minimum variables required to form a group (default: 1)",
    )
    parser.add_argument(
        "--show-ungrouped",
        action="store_true",
        default=False,
        help="Also print ungrouped variables",
    )
    return parser


def run_group(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 2

    result = group(env, separator=args.separator, min_group_size=args.min_group_size)

    print(result.summary())

    for group_name in result.group_names:
        print(f"\n[{group_name}]")
        for key, value in sorted(result.groups[group_name]):
            print(f"  {key}={value}")

    if args.show_ungrouped and result.ungrouped:
        print("\n[ungrouped]")
        for key, value in sorted(result.ungrouped):
            print(f"  {key}={value}")

    return 0


def main() -> None:
    parser = build_group_parser()
    args = parser.parse_args()
    sys.exit(run_group(args))


if __name__ == "__main__":
    main()
