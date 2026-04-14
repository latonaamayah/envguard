"""CLI sub-commands for snapshot management."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envguard.loader import load_env_file_safe
from envguard.snapshotter import (
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


def build_snapshot_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is not None:
        parser = subparsers.add_parser(
            "snapshot", help="Snapshot and compare .env files"
        )
    else:
        parser = argparse.ArgumentParser(
            prog="envguard snapshot",
            description="Snapshot and compare .env files",
        )

    sub = parser.add_subparsers(dest="snapshot_cmd", required=True)

    # save
    save_p = sub.add_parser("save", help="Save a snapshot of an .env file")
    save_p.add_argument("env_file", help="Path to the .env file")
    save_p.add_argument("output", help="Path to write the snapshot JSON")

    # diff
    diff_p = sub.add_parser("diff", help="Compare two snapshots")
    diff_p.add_argument("old", help="Path to the older snapshot JSON")
    diff_p.add_argument("new", help="Path to the newer snapshot JSON")

    return parser


def run_snapshot(args: argparse.Namespace) -> int:
    if args.snapshot_cmd == "save":
        result = load_env_file_safe(args.env_file)
        if result is None:
            print(f"error: could not load env file: {args.env_file}", file=sys.stderr)
            return 2
        snap = take_snapshot(result, source=args.env_file)
        save_snapshot(snap, args.output)
        print(f"Snapshot saved to {args.output} ({len(snap.variables)} variables)")
        return 0

    if args.snapshot_cmd == "diff":
        try:
            old_snap = load_snapshot(args.old)
            new_snap = load_snapshot(args.new)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        diff = diff_snapshots(old_snap, new_snap)
        if not diff.has_changes:
            print("No changes between snapshots.")
            return 0

        print(f"Changes: {diff.summary()}")
        for key, value in diff.added.items():
            print(f"  + {key}={value}")
        for key, value in diff.removed.items():
            print(f"  - {key}={value}")
        for key, (old_val, new_val) in diff.changed.items():
            print(f"  ~ {key}: {old_val!r} -> {new_val!r}")
        return 1  # non-zero when changes exist

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_snapshot_parser()
    args = parser.parse_args(argv)
    sys.exit(run_snapshot(args))


if __name__ == "__main__":
    main()
