"""CLI entry point for envguard."""
import sys
import argparse
from typing import Optional, Sequence

from envguard.loader import EnvFileNotFoundError, EnvParseError, load_env_file
from envguard.schema import Schema
from envguard.validator import validate
from envguard.reporter import OutputFormat, render
from envguard.auditor import audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard",
        description="Validate and audit .env files against a schema.",
    )
    parser.add_argument("env_file", help="Path to the .env file to validate.")
    parser.add_argument("schema_file", help="Path to the schema YAML/JSON file.")
    parser.add_argument(
        "--format",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Also run an audit for undeclared or unused optional variables.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env_vars = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        schema = Schema.from_file(args.schema_file)
    except FileNotFoundError:
        print(f"error: schema file not found: {args.schema_file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: failed to load schema: {exc}", file=sys.stderr)
        return 2

    result = validate(env_vars, schema)
    fmt = OutputFormat(args.format)
    use_color = not args.no_color
    print(render(result, fmt, use_color=use_color))

    if args.audit:
        audit_result = audit(env_vars, schema)
        if audit_result.has_issues:
            print("\n[audit]")
            print(audit_result.summary())

    return 0 if result.is_valid else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
