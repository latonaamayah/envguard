"""Weight and prioritize environment variables based on configurable rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WeightEntry:
    key: str
    value: str
    weight: int
    reason: str

    def __str__(self) -> str:
        return f"{self.key} (weight={self.weight}): {self.reason}"


@dataclass
class WeightResult:
    entries: List[WeightEntry] = field(default_factory=list)

    def has_entries(self) -> bool:
        return len(self.entries) > 0

    def top(self, n: int = 5) -> List[WeightEntry]:
        """Return the top N highest-weighted entries."""
        return sorted(self.entries, key=lambda e: e.weight, reverse=True)[:n]

    def bottom(self, n: int = 5) -> List[WeightEntry]:
        """Return the N lowest-weighted entries."""
        return sorted(self.entries, key=lambda e: e.weight)[:n]

    def as_dict(self) -> Dict[str, int]:
        return {e.key: e.weight for e in self.entries}

    def summary(self) -> str:
        if not self.entries:
            return "No entries to weight."
        top = self.top(3)
        names = ", ".join(e.key for e in top)
        return f"{len(self.entries)} entries weighted. Top keys: {names}"


_SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "api", "auth")
_LONG_VALUE_THRESHOLD = 64


def _compute_weight(key: str, value: str, rules: Optional[Dict[str, int]]) -> tuple[int, str]:
    """Compute a weight score and reason for a key/value pair."""
    if rules and key in rules:
        return rules[key], "explicit rule"

    weight = 0
    reasons = []

    lower = key.lower()
    if any(p in lower for p in _SENSITIVE_PATTERNS):
        weight += 30
        reasons.append("sensitive key")

    if not value or value.strip() == "":
        weight -= 20
        reasons.append("empty value")
    elif len(value) > _LONG_VALUE_THRESHOLD:
        weight += 10
        reasons.append("long value")

    if key == key.upper():
        weight += 5
        reasons.append("uppercase key")

    return weight, ", ".join(reasons) if reasons else "default"


def weight(
    env: Dict[str, str],
    rules: Optional[Dict[str, int]] = None,
) -> WeightResult:
    """Assign weights to all environment variables."""
    entries: List[WeightEntry] = []
    for key, value in env.items():
        w, reason = _compute_weight(key, value, rules)
        entries.append(WeightEntry(key=key, value=value, weight=w, reason=reason))
    return WeightResult(entries=entries)
