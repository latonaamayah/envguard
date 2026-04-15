"""Summarizer: produce a high-level statistical summary of a .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

SENSITIVE_KEYWORDS = {"password", "secret", "token", "key", "auth", "credential", "private"}


@dataclass
class SummaryResult:
    total: int
    empty_count: int
    sensitive_count: int
    longest_key: str
    longest_value_key: str
    prefix_distribution: Dict[str, int] = field(default_factory=dict)
    categories: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    def has_empty(self) -> bool:
        return self.empty_count > 0

    def has_sensitive(self) -> bool:
        return self.sensitive_count > 0

    def summary(self) -> str:
        lines = [
            f"Total variables : {self.total}",
            f"Empty values    : {self.empty_count}",
            f"Sensitive keys  : {self.sensitive_count}",
            f"Longest key     : {self.longest_key or '—'}",
            f"Longest value   : {self.longest_value_key or '—'}",
        ]
        if self.prefix_distribution:
            dist = ", ".join(f"{p}({c})" for p, c in sorted(self.prefix_distribution.items()))
            lines.append(f"Prefixes        : {dist}")
        return "\n".join(lines)


# ------------------------------------------------------------------ #

def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(kw in lower for kw in SENSITIVE_KEYWORDS)


def _extract_prefix(key: str) -> str:
    """Return the first segment before '_', or '' if no underscore."""
    parts = key.split("_", 1)
    return parts[0] if len(parts) > 1 else ""


def summarize(env: Dict[str, str]) -> SummaryResult:
    """Compute a SummaryResult from a parsed env mapping."""
    if not env:
        return SummaryResult(
            total=0,
            empty_count=0,
            sensitive_count=0,
            longest_key="",
            longest_value_key="",
        )

    empty_count = sum(1 for v in env.values() if v == "")
    sensitive_count = sum(1 for k in env if _is_sensitive(k))

    longest_key = max(env.keys(), key=len)
    longest_value_key = max(env.keys(), key=lambda k: len(env[k]))

    prefix_dist: Dict[str, int] = {}
    for k in env:
        prefix = _extract_prefix(k)
        if prefix:
            prefix_dist[prefix] = prefix_dist.get(prefix, 0) + 1

    return SummaryResult(
        total=len(env),
        empty_count=empty_count,
        sensitive_count=sensitive_count,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        prefix_distribution=prefix_dist,
    )
