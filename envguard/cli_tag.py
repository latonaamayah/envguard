"""CLI interface for the tagger module."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.tagger import tag


def build_tag_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Tag environment variables by key patterns."
    if subparsers is not None:
        parser = subparsers.add_parser("tag", description=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard-tag", description=description)

    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--rule",
        action="append",
        dest="rules",
        metavar="LABEL:PATTERN",
        default=[],
        help="Tag rule in LABEL:PATTERN format (repeatable)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="Output as JSON"
    )
    return parser


def _parse_rules(raw: List[str]) -> dict:
    rules: dict = {}
    for item in raw:
        if ":" not in item:
            continue
        label, _, pattern = item.partition(":")
        rules.setdefault(label.strip(), []).append(pattern.strip())
    return rules


def run_tag(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    rules = _parse_rules(args.rules)
    result = run_tag_logic(env, rules, as_json=args.as_json)
    return result


def run_tag_logic(env, rules, *, as_json=False) -> int:
    from envguard.tagger import tag

    result = tag(env, rules)

    if as_json:
        data = {
            "tagged": [
                {"key": e.key, "value": e.value, "tags": e.tags}
                for e in result.tagged
            ],
            "untagged": result.untagged_keys,
            "summary": result.summary(),
        }
        print(json.dumps(data, indent=2))
    else:
        for entry in result.tagged:
            print(f"{entry.key}={entry.value}  [{', '.join(entry.tags)}]")
        if result.untagged_keys:
            print(f"\nUntagged: {', '.join(result.untagged_keys)}")
        print(f"\n{result.summary()}")

    return 0


def main():
    parser = build_tag_parser()
    args = parser.parse_args()
    sys.exit(run_tag(args))


if __name__ == "__main__":
    main()
