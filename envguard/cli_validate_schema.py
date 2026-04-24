"""CLI entry point for schema-based validation."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envguard.loader import EnvFileNotFoundError, load_env_file
from envguard.schema import Schema
from envguard.validator_schema import validate_schema


def build_validate_schema_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Validate a .env file against a schema definition."
    if sub is not None:
        parser = sub.add_parser("validate-schema", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard validate-schema", description=description)

    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument("schema_file", help="Path to the schema JSON file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code even for warnings",
    )
    return parser


def run_validate_schema(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except (EnvFileNotFoundError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        schema = Schema.from_file(args.schema_file)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    result = validate_schema(env, schema)

    if args.format == "json":
        output = {
            "passed": result.passed,
            "violations": [
                {"key": v.key, "rule": v.rule, "message": v.message}
                for v in result.violations
            ],
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        for v in result.violations:
            print(f"  {v}")

    if result.has_violations():
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_validate_schema_parser()
    args = parser.parse_args(argv)
    sys.exit(run_validate_schema(args))


if __name__ == "__main__":
    main()
