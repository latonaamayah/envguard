"""comparer.py — Compare two env dicts and produce a structured diff report."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CompareChange:
    key: str
    left_value: Optional[str]
    right_value: Optional[str]
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'

    def message(self) -> str:
        if self.status == "added":
            return f"{self.key}: added with value '{self.right_value}'"
        if self.status == "removed":
            return f"{self.key}: removed (was '{self.left_value}')"
        if self.status == "changed":
            return f"{self.key}: '{self.left_value}' -> '{self.right_value}'"
        return f"{self.key}: unchanged"


@dataclass
class CompareReport:
    changes: List[CompareChange] = field(default_factory=list)

    def has_diff(self) -> bool:
        return any(c.status != "unchanged" for c in self.changes)

    def added(self) -> List[CompareChange]:
        return [c for c in self.changes if c.status == "added"]

    def removed(self) -> List[CompareChange]:
        return [c for c in self.changes if c.status == "removed"]

    def changed(self) -> List[CompareChange]:
        return [c for c in self.changes if c.status == "changed"]

    def unchanged(self) -> List[CompareChange]:
        return [c for c in self.changes if c.status == "unchanged"]

    def summary(self) -> str:
        a = len(self.added())
        r = len(self.removed())
        c = len(self.changed())
        u = len(self.unchanged())
        return f"added={a}, removed={r}, changed={c}, unchanged={u}"


def compare(
    left: Dict[str, str],
    right: Dict[str, str],
    include_unchanged: bool = True,
) -> CompareReport:
    """Compare two env dicts key-by-key and return a CompareReport."""
    all_keys = sorted(set(left) | set(right))
    changes: List[CompareChange] = []

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        if in_left and in_right:
            if left[key] == right[key]:
                if include_unchanged:
                    changes.append(CompareChange(key, left[key], right[key], "unchanged"))
            else:
                changes.append(CompareChange(key, left[key], right[key], "changed"))
        elif in_right:
            changes.append(CompareChange(key, None, right[key], "added"))
        else:
            changes.append(CompareChange(key, left[key], None, "removed"))

    return CompareReport(changes=changes)
