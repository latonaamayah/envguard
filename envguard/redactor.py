"""Redactor: replace sensitive env values with placeholder tokens for safe logging/output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

DEFAULT_PLACEHOLDER = "[REDACTED]"

SENSITIVE_PATTERNS: List[str] = [
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "auth", "credential", "private", "access_key", "signing",
]


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    def has_redacted(self) -> bool:
        return len(self.redacted_keys) > 0

    def summary(self) -> str:
        total = len(self.original)
        count = len(self.redacted_keys)
        return f"{count}/{total} variable(s) redacted."


def _is_sensitive(key: str) -> bool:
    """Return True if the key name suggests a sensitive value."""
    lower = key.lower()
    return any(pattern in lower for pattern in SENSITIVE_PATTERNS)


def redact(
    env: Dict[str, str],
    placeholder: str = DEFAULT_PLACEHOLDER,
    extra_keys: List[str] | None = None,
) -> RedactResult:
    """Return a RedactResult where sensitive values are replaced by *placeholder*.

    Args:
        env: Mapping of environment variable names to values.
        placeholder: String used to replace sensitive values.
        extra_keys: Additional key names (case-insensitive) to treat as sensitive.
    """
    extra = {k.lower() for k in (extra_keys or [])}
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key) or key.lower() in extra:
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=redacted_keys,
    )
