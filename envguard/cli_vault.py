from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file_safe
from envguard.vaulter import vault


def build_vault_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard vault",
        description="Vault (mask + checksum) environment variables from a .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Only vault these specific keys",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    return parser


def run_vault(args: argparse.Namespace) -> int:
    result = load_env_file_safe(args.env_file)
    if result is None:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2

    vr = vault(result, keys=args.keys)

    if args.json:
        print(vr.to_json())
    else:
        if not vr.has_entries():
            print("No entries vaulted.")
        else:
            for entry in vr.entries:
                print(str(entry))
        print(vr.summary())

    return 0


def main() -> None:
    parser = build_vault_parser()
    args = parser.parse_args()
    sys.exit(run_vault(args))


if __name__ == "__main__":
    main()
