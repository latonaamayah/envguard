"""CLI entry-point for the summarize sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.summarizer import summarize


def build_summarize_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Print a statistical summary of a .env file."
    if subparsers is not None:
        parser = subparsers.add_parser("summarize", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard summarize", description=description)

    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    return parser


def run_summarize(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        err.write(f"error: {exc}\n")
        return 2
    except EnvParseError as exc:
        err.write(f"error: {exc}\n")
        return 2

    result = summarize(env)

    if args.fmt == "json":
        payload = {
            "total": result.total,
            "empty_count": result.empty_count,
            "sensitive_count": result.sensitive_count,
            "longest_key": result.longest_key,
            "longest_value_key": result.longest_value_key,
            "prefix_distribution": result.prefix_distribution,
        }
        out.write(json.dumps(payload, indent=2) + "\n")
    else:
        out.write(result.summary() + "\n")

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_summarize_parser()
    args = parser.parse_args(argv)
    sys.exit(run_summarize(args))


if __name__ == "__main__":
    main()
