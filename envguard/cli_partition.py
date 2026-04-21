"""CLI entry point for the partition command."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict

from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.partitioner import partition


def build_partition_parser(sub=None) -> argparse.ArgumentParser:
    if sub is not None:
        parser = sub.add_parser("partition", help="Partition .env variables into named buckets")
    else:
        parser = argparse.ArgumentParser(
            prog="envguard-partition",
            description="Partition .env variables into named buckets based on key patterns.",
        )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--rule",
        metavar="BUCKET=PATTERN",
        action="append",
        dest="rules",
        default=[],
        help="Partition rule in BUCKET=PATTERN format (may be repeated)",
    )
    parser.add_argument(
        "--default-bucket",
        default="default",
        help="Bucket name for unmatched keys (default: 'default')",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    return parser


def _parse_rules(raw: list) -> Dict[str, str]:
    rules: Dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Invalid rule format (expected BUCKET=PATTERN): {item!r}")
        bucket, _, pattern = item.partition("=")
        rules[bucket.strip()] = pattern.strip()
    return rules


def run_partition(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        rules = _parse_rules(args.rules)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = partition(env, rules, default_bucket=args.default_bucket)

    if args.format == "json":
        data = {bucket: result.get_bucket(bucket) for bucket in result.bucket_names()}
        print(json.dumps(data, indent=2))
    else:
        print(result.summary())
        for bucket in result.bucket_names():
            print(f"\n[{bucket}]")
            for key in result.keys_for_bucket(bucket):
                print(f"  {key}")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_partition_parser()
    args = parser.parse_args()
    sys.exit(run_partition(args))


if __name__ == "__main__":  # pragma: no cover
    main()
