"""Formats and outputs validation results for the CLI."""

from dataclasses import dataclass
from enum import Enum
from typing import List

from envguard.validator import ValidationResult


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_text(result: ValidationResult, use_color: bool = True) -> str:
    lines: List[str] = []

    if result.is_valid:
        lines.append(_colorize("✔ All environment variables are valid.", ANSI_GREEN, use_color))
    else:
        lines.append(_colorize("✘ Validation failed.", ANSI_RED, use_color))

    if result.errors:
        lines.append(_colorize(f"\nErrors ({len(result.errors)}):", ANSI_BOLD, use_color))
        for error in result.errors:
            lines.append(_colorize(f"  [ERROR] {error}", ANSI_RED, use_color))

    if result.warnings:
        lines.append(_colorize(f"\nWarnings ({len(result.warnings)}):", ANSI_BOLD, use_color))
        for warning in result.warnings:
            lines.append(_colorize(f"  [WARN]  {warning}", ANSI_YELLOW, use_color))

    return "\n".join(lines)


def format_json(result: ValidationResult) -> str:
    import json

    payload = {
        "valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
    }
    return json.dumps(payload, indent=2)


def render(result: ValidationResult, fmt: OutputFormat = OutputFormat.TEXT, use_color: bool = True) -> str:
    """Return a formatted string representation of the validation result."""
    if fmt == OutputFormat.JSON:
        return format_json(result)
    return format_text(result, use_color=use_color)
