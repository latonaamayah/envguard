import argparse
import sys

from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.anonymizer import anonymize


def build_anonymize_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard anonymize",
        description="Anonymize sensitive values in a .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--placeholder",
        default="***",
        help="Replacement string for sensitive values (default: ***)",
    )
    parser.add_argument(
        "--keys",
        nargs="*",
        help="Explicit list of keys to anonymize (overrides auto-detection)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line after output",
    )
    return parser


def run_anonymize(args, out=sys.stdout, err=sys.stderr) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"Error: {exc}", file=err)
        return 2

    result = anonymize(env, placeholder=args.placeholder, keys=args.keys)

    for key, value in result.as_dict().items():
        print(f"{key}={value}", file=out)

    if args.summary:
        print(result.summary(), file=out)

    return 0


def main():
    parser = build_anonymize_parser()
    args = parser.parse_args()
    sys.exit(run_anonymize(args))


if __name__ == "__main__":
    main()
