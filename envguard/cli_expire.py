import argparse
import sys
from datetime import datetime

from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.expirer import expire


def build_expire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-expire",
        description="Check expiry dates for environment variables.",
    )
    parser.add_argument("env_file", help="Path to .env file")
    parser.add_argument(
        "--expiry",
        metavar="KEY=DATE",
        nargs="+",
        default=[],
        help="Expiry dates in KEY=YYYY-MM-DD format",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Exit 0 even if keys are expired",
    )
    return parser


def _parse_expiry(pairs):
    expiry_map = {}
    for pair in pairs:
        if "=" not in pair:
            continue
        key, _, date = pair.partition("=")
        expiry_map[key.strip()] = date.strip()
    return expiry_map


def run_expire(args, out=None):
    import sys
    out = out or sys.stdout

    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    expiry_map = _parse_expiry(args.expiry)
    result = expire(env, expiry_map)

    for entry in result.entries:
        print(entry.message, file=out)

    print(result.summary(), file=out)

    if result.has_expired and not args.warn_only:
        return 1
    return 0


def main():
    parser = build_expire_parser()
    args = parser.parse_args()
    sys.exit(run_expire(args))


if __name__ == "__main__":
    main()
