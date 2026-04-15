"""Normalizer: strips, trims, and standardizes .env variable values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeChange:
    key: str
    original: str
    normalized: str
    reason: str


@dataclass
class NormalizeResult:
    variables: Dict[str, str] = field(default_factory=dict)
    changes: List[NormalizeChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        if not self.has_changes:
            return "No normalization changes applied."
        lines = [f"{len(self.changes)} change(s) applied:"]
        for c in self.changes:
            lines.append(f"  [{c.key}] {c.reason}: {c.original!r} -> {c.normalized!r}")
        return "\n".join(lines)


def _normalize_value(key: str, value: str) -> Tuple[str, List[str]]:
    """Return (normalized_value, list_of_reasons)."""
    reasons: List[str] = []
    result = value

    # Strip surrounding whitespace
    stripped = result.strip()
    if stripped != result:
        reasons.append("stripped surrounding whitespace")
        result = stripped

    # Remove matching surrounding quotes (single or double)
    if len(result) >= 2 and result[0] == result[-1] and result[0] in ('"', "'"):
        unquoted = result[1:-1]
        reasons.append(f"removed surrounding {result[0]} quotes")
        result = unquoted

    # Normalize boolean-like values to lowercase
    if result.lower() in ("true", "false", "yes", "no"):
        lower = result.lower()
        if lower != result:
            reasons.append("lowercased boolean-like value")
            result = lower

    return result, reasons


def normalize(env: Dict[str, str]) -> NormalizeResult:
    """Normalize all values in an env dict and report what changed."""
    result = NormalizeResult()
    for key, value in env.items():
        normalized, reasons = _normalize_value(key, value)
        result.variables[key] = normalized
        for reason in reasons:
            result.changes.append(
                NormalizeChange(
                    key=key,
                    original=value,
                    normalized=normalized,
                    reason=reason,
                )
            )
    return result
