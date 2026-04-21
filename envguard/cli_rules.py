"""CLI entry point for envguard rule validation."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List

from envguard.loader import EnvFileNotFoundError, load_env_file
from envguard.validator_rules import BUILT_IN_RULES, apply_rules


def build_rules_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Apply named validation rules to .env file keys."
    if parent is not None:
        parser = parent.add_parser("rules", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard-rules", description=description)

    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--rule",
        action="append",
        metavar="RULE:KEY",
        dest="rule_pairs",
        default=[],
        help="Apply RULE to KEY (repeatable, e.g. --rule not_empty:DB_HOST)",
    )
    parser.add_argument(
        "--severity",
        choices=["error", "warning"],
        default="error",
        help="Severity for violations (default: error)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when warnings are present",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="List available built-in rules and exit",
    )
    return parser


def _parse_rule_pairs(pairs: List[str]) -> Dict[str, List[str]]:
    rules: Dict[str, List[str]] = {}
    for pair in pairs:
        if ":" not in pair:
            continue
        rule, _, key = pair.partition(":")
        rules.setdefault(rule.strip(), []).append(key.strip())
    return rules


def run_rules(args: argparse.Namespace) -> int:
    if args.list_rules:
        for name in sorted(BUILT_IN_RULES):
            print(name)
        return 0

    try:
        env = load_env_file(args.env_file)
    except (EnvFileNotFoundError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rule_map = _parse_rule_pairs(args.rule_pairs)
    result = apply_rules(env, rule_map, severity=args.severity)

    for v in result.violations:
        print(str(v))

    if result.errors:
        return 1
    if args.strict and result.warnings:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_rules_parser()
    args = parser.parse_args()
    sys.exit(run_rules(args))


if __name__ == "__main__":  # pragma: no cover
    main()
