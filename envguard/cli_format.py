"""CLI entry-point for the formatter sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envguard.formatter import format_env


def build_format_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: E501
    description = "Rewrite a .env file with consistent formatting."
    if parent is not None:
        parser = parent.add_parser("format", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard-format", description=description)

    parser.add_argument("env_file", help="Path to the .env file to format")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with code 1 if any changes would be made (dry-run).",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write the formatted output back to the original file.",
    )
    return parser


def run_format(args: argparse.Namespace) -> int:
    path = Path(args.env_file)
    if not path.exists():
        print(f"[error] File not found: {path}", file=sys.stderr)
        return 2

    raw_lines = path.read_text(encoding="utf-8").splitlines()
    result = format_env(raw_lines)

    if args.check:
        if result.has_changes:
            print(f"[check] {len(result.changed_keys)} line(s) would be reformatted.")
            return 1
        print("[check] File is already well-formatted.")
        return 0

    # Build the formatted file content
    formatted_lines: list[str] = []
    for raw in raw_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            formatted_lines.append(raw)
            continue
        key = stripped.partition("=")[0].strip()
        change = next((c for c in result.changes if c.key == key), None)
        formatted_lines.append(change.formatted_line if change else raw)

    output = "\n".join(formatted_lines) + "\n"

    if args.in_place:
        path.write_text(output, encoding="utf-8")
        print(f"[format] {path} updated. {result.summary()}")
    else:
        print(output, end="")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_format_parser()
    args = parser.parse_args()
    sys.exit(run_format(args))


if __name__ == "__main__":  # pragma: no cover
    main()
