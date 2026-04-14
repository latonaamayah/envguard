"""CLI sub-command: envguard profile — show statistics for a .env file."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envguard.loader import load_env_file
from envguard.profiler import profile


def build_profile_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Display statistics and insights for a .env file."
    if subparsers is not None:
        parser = subparsers.add_parser("profile", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard profile", description=description)

    parser.add_argument("env_file", help="Path to the .env file to profile")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    return parser


def run_profile(args: argparse.Namespace) -> int:
    """Execute the profile command; returns an exit code."""
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = profile(env)

    if args.output_format == "json":
        data = {
            "total": result.total,
            "empty_count": result.empty_count,
            "sensitive_count": result.sensitive_count,
            "long_value_count": result.long_value_count,
            "numeric_count": result.numeric_count,
            "boolean_count": result.boolean_count,
            "avg_key_length": round(result.avg_key_length, 2),
            "avg_value_length": round(result.avg_value_length, 2),
        }
        print(json.dumps(data, indent=2))
    else:
        print(result.summary())

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_profile_parser()
    args = parser.parse_args(argv)
    sys.exit(run_profile(args))


if __name__ == "__main__":
    main()
