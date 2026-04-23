"""Expander: expand shorthand or abbreviated env var keys to their full canonical names."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExpandEntry:
    key: str
    original_key: str
    value: str
    was_expanded: bool

    def message(self) -> str:
        if self.was_expanded:
            return f"{self.original_key!r} expanded to {self.key!r}"
        return f"{self.key!r} unchanged"


@dataclass
class ExpandResult:
    entries: List[ExpandEntry] = field(default_factory=list)

    def has_expansions(self) -> bool:
        return any(e.was_expanded for e in self.entries)

    def expanded_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_expanded]

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def summary(self) -> str:
        n = sum(1 for e in self.entries if e.was_expanded)
        return f"{n} key(s) expanded out of {len(self.entries)} total."


def expand(
    env: Dict[str, str],
    mapping: Dict[str, str],
) -> ExpandResult:
    """Expand abbreviated keys in *env* using *mapping* (abbrev -> canonical).

    Keys not present in *mapping* are passed through unchanged.
    If the canonical name is already present in *env*, the abbreviated key
    is still renamed (last-write wins for the canonical slot).
    """
    result = ExpandResult()
    for key, value in env.items():
        canonical: Optional[str] = mapping.get(key)
        if canonical and canonical != key:
            result.entries.append(
                ExpandEntry(
                    key=canonical,
                    original_key=key,
                    value=value,
                    was_expanded=True,
                )
            )
        else:
            result.entries.append(
                ExpandEntry(
                    key=key,
                    original_key=key,
                    value=value,
                    was_expanded=False,
                )
            )
    return result
