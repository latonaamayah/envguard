from __future__ import annotations
import argparse
import sys
from envguard.loader import load_env_file, EnvFileNotFoundError
from envguard.rotator import rotate


def build_rotate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard rotate",
        description="Rotate secret values in a .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Keys to rotate (default: all keys)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=32,
        help="Length of generated secret (default: 32)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write rotated env to file instead of stdout",
    )
    return parser


def run_rotate(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except EnvFileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = rotate(env, keys=args.keys, length=args.length)
    lines = [f"{k}={v}" for k, v in result.as_dict().items()]
    output = "\n".join(lines) + "\n"

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
        print(f"Rotated {len(result.rotated_keys)} key(s) → {args.output}")
    else:
        print(output, end="")

    return 0


def main() -> None:
    parser = build_rotate_parser()
    args = parser.parse_args()
    sys.exit(run_rotate(args))


if __name__ == "__main__":
    main()
