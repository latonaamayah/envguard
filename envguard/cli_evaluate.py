"""CLI entry point for the evaluate command."""
from __future__ import annotations

import argparse
import json
import sys

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.schema import Schema
from envguard.evaluator import evaluate


def build_evaluate_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Score an .env file against a schema and return a quality grade."
    if subparsers is not None:
        parser = subparsers.add_parser("evaluate", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard-evaluate", description=description)
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument("schema_file", help="Path to the schema YAML/JSON file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-below",
        type=int,
        default=0,
        metavar="SCORE",
        help="Exit with code 1 if score is below this threshold",
    )
    return parser


def run_evaluate(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except (EnvFileNotFoundError, EnvParseError) as exc:
        print(f"Error loading env file: {exc}", file=sys.stderr)
        return 2

    try:
        schema = Schema.from_file(args.schema_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    result = evaluate(env, schema)

    if args.format == "json":
        output = {
            "score": result.score,
            "grade": result.grade,
            "total_vars": result.total_vars,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "breakdown": result.breakdown,
            "notes": result.notes,
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        for note in result.notes:
            print(f"  • {note}")

    if args.fail_below and result.score < args.fail_below:
        return 1
    return 0


def main() -> None:
    parser = build_evaluate_parser()
    args = parser.parse_args()
    sys.exit(run_evaluate(args))


if __name__ == "__main__":
    main()
