"""Shield sensitive .env values by replacing them with environment variable references."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS = ("password", "secret", "token", "api_key", "apikey", "private", "auth")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


@dataclass
class ShieldEntry:
    key: str
    original_value: str
    shielded_value: str
    was_shielded: bool

    def __str__(self) -> str:
        if self.was_shielded:
            return f"{self.key}: shielded -> {self.shielded_value}"
        return f"{self.key}: unchanged"


@dataclass
class ShieldResult:
    entries: List[ShieldEntry] = field(default_factory=list)

    @property
    def has_shielded(self) -> bool:
        return any(e.was_shielded for e in self.entries)

    @property
    def shielded_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_shielded]

    @property
    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.shielded_value for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        shielded = len(self.shielded_keys)
        return f"{shielded}/{total} keys shielded"


def shield(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    prefix: str = "${{",
    suffix: str = "}}",
) -> ShieldResult:
    """Replace sensitive (or explicitly listed) values with variable reference placeholders.

    Args:
        env: mapping of environment variable key -> value.
        keys: explicit list of keys to shield; if None, auto-detect sensitive keys.
        prefix: prefix for the shielded placeholder.
        suffix: suffix for the shielded placeholder.

    Returns:
        ShieldResult with per-key entries.
    """
    result = ShieldResult()
    for key, value in env.items():
        should_shield = (keys is not None and key in keys) or (
            keys is None and _is_sensitive(key)
        )
        if should_shield:
            shielded_value = f"{prefix}{key}{suffix}"
            result.entries.append(
                ShieldEntry(
                    key=key,
                    original_value=value,
                    shielded_value=shielded_value,
                    was_shielded=True,
                )
            )
        else:
            result.entries.append(
                ShieldEntry(
                    key=key,
                    original_value=value,
                    shielded_value=value,
                    was_shielded=False,
                )
            )
    return result
