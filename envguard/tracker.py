from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class TrackEntry:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def was_added(self) -> bool:
        return self.old_value is None and self.new_value is not None

    @property
    def was_removed(self) -> bool:
        return self.old_value is not None and self.new_value is None

    @property
    def was_modified(self) -> bool:
        return self.old_value is not None and self.new_value is not None and self.old_value != self.new_value

    def message(self) -> str:
        if self.was_added:
            return f"{self.key}: added with value '{self.new_value}'"
        if self.was_removed:
            return f"{self.key}: removed (was '{self.old_value}')"
        if self.was_modified:
            return f"{self.key}: changed from '{self.old_value}' to '{self.new_value}'"
        return f"{self.key}: unchanged"


@dataclass
class TrackResult:
    entries: List[TrackEntry] = field(default_factory=list)

    def has_changes(self) -> bool:
        return any(e.was_added or e.was_removed or e.was_modified for e in self.entries)

    def added_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_added]

    def removed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_removed]

    def modified_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_modified]

    def summary(self) -> str:
        a, r, m = len(self.added_keys()), len(self.removed_keys()), len(self.modified_keys())
        return f"added={a}, removed={r}, modified={m}"


def track(before: Dict[str, str], after: Dict[str, str]) -> TrackResult:
    result = TrackResult()
    all_keys = set(before) | set(after)
    for key in sorted(all_keys):
        old = before.get(key)
        new = after.get(key)
        if old != new:
            result.entries.append(TrackEntry(key=key, old_value=old, new_value=new))
    return result
