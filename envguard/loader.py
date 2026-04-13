"""Loader module for parsing .env files into key-value dictionaries."""

from pathlib import Path
from typing import Dict, Optional


class EnvFileNotFoundError(FileNotFoundError):
    """Raised when the .env file does not exist."""
    pass


class EnvParseError(ValueError):
    """Raised when a line in the .env file cannot be parsed."""
    pass


def load_env_file(path: str) -> Dict[str, str]:
    """
    Parse a .env file and return a dictionary of key-value pairs.

    Supports:
      - KEY=VALUE
      - KEY="VALUE" or KEY='VALUE' (strips surrounding quotes)
      - Inline comments after values (e.g. KEY=value  # comment)
      - Blank lines and full-line comments are ignored

    Args:
        path: Path to the .env file.

    Returns:
        A dict mapping variable names to their string values.

    Raises:
        EnvFileNotFoundError: If the file does not exist.
        EnvParseError: If a non-comment, non-blank line is malformed.
    """
    env_path = Path(path)
    if not env_path.exists():
        raise EnvFileNotFoundError(f".env file not found: {path}")

    env_vars: Dict[str, str] = {}

    with env_path.open("r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise EnvParseError(
                    f"Line {line_number}: invalid syntax (missing '='): {raw_line.rstrip()}"
                )

            key, _, raw_value = line.partition("=")
            key = key.strip()

            if not key:
                raise EnvParseError(
                    f"Line {line_number}: empty key found: {raw_line.rstrip()}"
                )

            # Strip inline comments
            value = raw_value.split(" #")[0].strip()

            # Strip surrounding quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[0] == value[-1]:
                value = value[1:-1]

            env_vars[key] = value

    return env_vars


def load_env_file_safe(path: str) -> Optional[Dict[str, str]]:
    """Like load_env_file but returns None on error instead of raising."""
    try:
        return load_env_file(path)
    except (EnvFileNotFoundError, EnvParseError):
        return None
