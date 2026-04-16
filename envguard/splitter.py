"""Split a .env file into multiple files based on prefix or group."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    def has_groups(self) -> bool:
        return bool(self.groups)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def total_keys(self) -> int:
        total = sum(len(v) for v in self.groups.values())
        return total + len(self.ungrouped)

    def summary(self) -> str:
        parts = [f"{name}: {len(vars_)} key(s)" for name, vars_ in sorted(self.groups.items())]
        if self.ungrouped:
            parts.append(f"ungrouped: {len(self.ungrouped)} key(s)")
        return ", ".join(parts) if parts else "no keys"


def _extract_prefix(key: str, separator: str = "_") -> Optional[str]:
    """Return the first segment before the separator, or None if no separator."""
    if separator in key:
        return key.split(separator, 1)[0].upper()
    return None


def split(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
) -> SplitResult:
    """Split env vars into groups by prefix.

    If *prefixes* is provided, only those prefixes are used as group keys.
    Any key that does not match a prefix goes to ``ungrouped``.
    If *prefixes* is None, all detected prefixes form groups.
    """
    result = SplitResult()
    allowed = {p.upper() for p in prefixes} if prefixes is not None else None

    for key, value in env.items():
        prefix = _extract_prefix(key, separator)
        if prefix is None:
            result.ungrouped[key] = value
            continue
        if allowed is not None and prefix not in allowed:
            result.ungrouped[key] = value
            continue
        result.groups.setdefault(prefix, {})[key] = value

    return result
