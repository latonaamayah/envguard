"""CLI entry point for envguard."""

import sys
import argparse

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.schema import Schema
from envguard.validator import validate
from envguard.reporter import render, OutputFormat


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard",
        description="Validate a .env file against a schema definition.",
    )
    parser.add_argument(
        "env_file",
        help="Path to the .env file to validate (e.g. .env or .env.production)",
    )
    parser.add_argument(
        "--schema",
        default="envguard.schema.json",
        metavar="SCHEMA_FILE",
        help="Path to the schema JSON file (default: envguard.schema.json)",
    )
    parser.add_argument(
        "--format",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        dest="output_format",
        help="Output format: text or json (default: text)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code even when only warnings are present",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Load .env file
    try:
        env_vars = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"[envguard] ERROR: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"[envguard] PARSE ERROR: {exc}", file=sys.stderr)
        return 2

    # Load schema
    try:
        schema = Schema.from_file(args.schema)
    except FileNotFoundError:
        print(
            f"[envguard] ERROR: Schema file not found: {args.schema}",
            file=sys.stderr,
        )
        return 2
    except (ValueError, KeyError) as exc:
        print(f"[envguard] ERROR: Invalid schema: {exc}", file=sys.stderr)
        return 2

    # Validate
    result = validate(schema, env_vars)

    # Render output
    output_format = OutputFormat(args.output_format)
    print(render(result, output_format))

    # Determine exit code
    if not result.is_valid:
        return 1
    if args.strict and result.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
