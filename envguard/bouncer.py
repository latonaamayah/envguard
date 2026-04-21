"""bouncer.py — Rejects env variables whose values match a blocklist of forbidden patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


_DEFAULT_PATTERNS: List[str] = [
    r"^password123$",
    r"^admin$",
    r"^secret$",
    r"^changeme$",
    r"^1234",
    r"^(true|false|yes|no)$",  # booleans used as secrets
    r"^\s*$",  # blank / whitespace-only
]


@dataclass
class BounceEntry:
    key: str
    value: str
    pattern: Optional[str]
    rejected: bool

    def message(self) -> str:
        if self.rejected:
            return f"{self.key!r} rejected: value matches forbidden pattern {self.pattern!r}"
        return f"{self.key!r} allowed"


@dataclass
class BounceResult:
    entries: List[BounceEntry] = field(default_factory=list)

    def has_rejected(self) -> bool:
        return any(e.rejected for e in self.entries)

    def rejected_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.rejected]

    def allowed_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.rejected]

    def summary(self) -> str:
        total = len(self.entries)
        rejected = len(self.rejected_keys())
        return f"{rejected}/{total} variable(s) rejected by blocklist"


def bounce(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
) -> BounceResult:
    """Check each env value against forbidden patterns.

    Args:
        env: Mapping of environment variable names to values.
        patterns: Optional list of regex patterns to block.
                  Defaults to ``_DEFAULT_PATTERNS``.

    Returns:
        A :class:`BounceResult` describing which keys were rejected.
    """
    compiled = [re.compile(p, re.IGNORECASE) for p in (patterns or _DEFAULT_PATTERNS)]
    result = BounceResult()

    for key, value in env.items():
        matched_pattern: Optional[str] = None
        for rx in compiled:
            if rx.search(value):
                matched_pattern = rx.pattern
                break
        result.entries.append(
            BounceEntry(
                key=key,
                value=value,
                pattern=matched_pattern,
                rejected=matched_pattern is not None,
            )
        )

    return result
