"""envguard CLI — graph subcommand."""
from __future__ import annotations

import argparse
import sys

from envguard.grapher import graph
from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError


def build_graph_parser(sub: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Display the variable reference dependency graph for a .env file."
    if sub is not None:
        parser = sub.add_parser("graph", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard graph", description=description)
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--cycles-only",
        action="store_true",
        default=False,
        help="Exit 1 if cycles are detected, otherwise exit 0",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a one-line summary instead of the full graph",
    )
    return parser


def run_graph(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = graph(env)

    if args.summary:
        print(result.summary())
        return 1 if (args.cycles_only and result.has_cycles()) else 0

    for key, node in sorted(result.nodes.items()):
        refs = ", ".join(node.references) if node.references else "-"
        rev = ", ".join(node.referenced_by) if node.referenced_by else "-"
        print(f"{key}  refs=[{refs}]  used_by=[{rev}]")

    if result.has_cycles():
        print("warning: cycle(s) detected in variable references", file=sys.stderr)
        if args.cycles_only:
            return 1

    return 0


def main() -> None:  # pragma: no cover
    parser = build_graph_parser()
    args = parser.parse_args()
    sys.exit(run_graph(args))


if __name__ == "__main__":  # pragma: no cover
    main()
