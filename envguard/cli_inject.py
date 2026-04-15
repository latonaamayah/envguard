"""CLI sub-command: envguard inject — inject .env variables into a target file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envguard.loader import load_env_file, EnvFileNotFoundError, EnvParseError
from envguard.injector import inject


def build_inject_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Inject variables from a source .env into a target .env file."
    if subparsers is not None:
        parser = subparsers.add_parser("inject", description=description)
    else:
        parser = argparse.ArgumentParser(prog="envguard inject", description=description)

    parser.add_argument("source", help="Source .env file whose variables will be injected.")
    parser.add_argument("target", help="Target .env file to inject variables into.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing keys in the target file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the merged result without writing to disk.",
    )
    return parser


def run_inject(args: argparse.Namespace) -> int:
    try:
        source_env = load_env_file(args.source)
    except (EnvFileNotFoundError, EnvParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        target_env = load_env_file(args.target)
    except EnvFileNotFoundError:
        target_env = {}
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = inject(source_env, target_env, overwrite=args.overwrite)
    print(result.summary())

    if not args.dry_run:
        lines = [f"{k}={v}" for k, v in target_env.items()]
        Path(args.target).write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        for key, value in result.as_dict().items():
            print(f"{key}={value}")

    return 0


def main() -> None:
    parser = build_inject_parser()
    args = parser.parse_args()
    sys.exit(run_inject(args))


if __name__ == "__main__":
    main()
