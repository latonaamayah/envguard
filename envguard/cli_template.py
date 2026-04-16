from __future__ import annotations
import argparse
import json
import sys
from envguard.loader import load_env_file_safe
from envguard.templater import render_templates


def build_template_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-template",
        description="Render template strings using values from a .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file used as context.")
    parser.add_argument(
        "--template",
        action="append",
        metavar="KEY=TEMPLATE",
        dest="templates",
        default=[],
        help="Template entry in KEY=TEMPLATE format. May be repeated.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any placeholder cannot be resolved.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
    )
    return parser


def _parse_templates(raw: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            continue
        key, _, tmpl = item.partition("=")
        result[key.strip()] = tmpl
    return result


def run_template(args: argparse.Namespace) -> int:
    env, err = load_env_file_safe(args.env_file)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        return 2

    templates = _parse_templates(args.templates)
    if not templates:
        print("No templates provided. Use --template KEY={{VAR}}.", file=sys.stderr)
        return 2

    result = render_templates(templates, env, strict=args.strict)

    if args.output_format == "json":
        print(json.dumps(result.as_dict(), indent=2))
    else:
        for entry in result.entries:
            status = "[MISSING]" if entry.has_missing else "[OK]"
            print(f"{status} {entry.key}={entry.rendered}")

    if args.strict and result.has_errors:
        for e in result.errors:
            print(f"  ! {e}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    parser = build_template_parser()
    args = parser.parse_args()
    sys.exit(run_template(args))


if __name__ == "__main__":
    main()
