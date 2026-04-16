from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DeduplicateEntry:
    key: str
    kept_value: str
    removed_values: List[str]

    @property
    def count(self) -> int:
        return len(self.removed_values)


@dataclass
class DeduplicateResult:
    entries: List[DeduplicateEntry] = field(default_factory=list)
    cleaned: Dict[str, str] = field(default_factory=dict)

    @property
    def has_duplicates(self) -> bool:
        return len(self.entries) > 0

    @property
    def duplicate_keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        lines = [f"{len(self.entries)} duplicate key(s) resolved:"]
        for e in self.entries:
            lines.append(f"  {e.key}: kept '{e.kept_value}', removed {e.count} value(s)")
        return "\n".join(lines)


def deduplicate(pairs: List[tuple]) -> DeduplicateResult:
    """Accept a list of (key, value) pairs (preserving order/duplicates) and deduplicate.

    The last occurrence of each key wins.
    """
    seen: Dict[str, List[str]] = {}
    order: List[str] = []

    for key, value in pairs:
        if key not in seen:
            seen[key] = []
            order.append(key)
        seen[key].append(value)

    result = DeduplicateResult()
    for key in order:
        values = seen[key]
        kept = values[-1]
        result.cleaned[key] = kept
        if len(values) > 1:
            result.entries.append(
                DeduplicateEntry(key=key, kept_value=kept, removed_values=values[:-1])
            )
    return result
