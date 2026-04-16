from __future__ import annotations
import argparse
import sys
from pathlib import Path
from envguard.archiver import archive, save_archive, load_archive, ArchiveResult
from envguard.loader import load_env_file, EnvFileNotFoundError


def build_archive_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-archive",
        description="Archive .env file snapshots with labels",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    save_p = sub.add_parser("save", help="Save current env to archive")
    save_p.add_argument("env_file", help="Path to .env file")
    save_p.add_argument("--label", required=True, help="Label for this archive entry")
    save_p.add_argument("--archive", default=".envarchive.json", help="Archive file path")

    list_p = sub.add_parser("list", help="List archived entries")
    list_p.add_argument("--archive", default=".envarchive.json", help="Archive file path")

    show_p = sub.add_parser("show", help="Show variables for a label")
    show_p.add_argument("label", help="Label to show")
    show_p.add_argument("--archive", default=".envarchive.json", help="Archive file path")

    return parser


def run_archive(args: argparse.Namespace) -> int:
    archive_path = Path(args.archive)

    if args.command == "save":
        try:
            env = load_env_file(args.env_file)
        except EnvFileNotFoundError:
            print(f"Error: file not found: {args.env_file}", file=sys.stderr)
            return 2
        result = load_archive(archive_path)
        entry = archive(env, label=args.label)
        result.entries.append(entry)
        save_archive(result, archive_path)
        print(f"Archived '{args.label}' ({len(env)} variables)")
        return 0

    if args.command == "list":
        result = load_archive(archive_path)
        if not result.has_entries():
            print("No archives found.")
        for e in result.entries:
            print(f"  {e.label}  ({e.timestamp})")
        return 0

    if args.command == "show":
        result = load_archive(archive_path)
        entry = result.get(args.label)
        if entry is None:
            print(f"Label '{args.label}' not found.", file=sys.stderr)
            return 1
        for k, v in entry.variables.items():
            print(f"{k}={v}")
        return 0

    return 0


def main() -> None:
    parser = build_archive_parser()
    args = parser.parse_args()
    sys.exit(run_archive(args))


if __name__ == "__main__":
    main()
