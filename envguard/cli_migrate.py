from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file_safe
from envguard.migrator import migrate


def build_migrate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard migrate",
        description="Rename keys in a .env file according to a mapping.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        help="Key rename rule (repeatable)",
    )
    parser.add_argument(
        "--keep-old",
        action="store_true",
        default=False,
        help="Retain original key alongside renamed key",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit non-zero if any source keys are missing",
    )
    return parser


def _parse_renames(raw: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            continue
        old, new = item.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping


def run_migrate(args: argparse.Namespace) -> int:
    env, err = load_env_file_safe(args.env_file)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    mapping = _parse_renames(args.rename)
    result = migrate(env, mapping, keep_old=args.keep_old)

    for key, value in result.output.items():
        print(f"{key}={value}")

    if args.strict and result.skipped:
        print(f"warning: skipped keys: {', '.join(result.skipped)}", file=sys.stderr)
        return 1

    return 0


def main() -> None:
    parser = build_migrate_parser()
    args = parser.parse_args()
    sys.exit(run_migrate(args))


if __name__ == "__main__":
    main()
