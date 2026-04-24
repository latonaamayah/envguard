"""Structural diff between two env dicts with schema-aware context."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StructDiffEntry:
    key: str
    left_value: Optional[str]
    right_value: Optional[str]
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    is_sensitive: bool = False

    @property
    def message(self) -> str:
        if self.status == "added":
            return f"{self.key}: [absent] -> {self._safe(self.right_value)}"
        if self.status == "removed":
            return f"{self.key}: {self._safe(self.left_value)} -> [absent]"
        if self.status == "changed":
            return f"{self.key}: {self._safe(self.left_value)} -> {self._safe(self.right_value)}"
        return f"{self.key}: unchanged"

    def _safe(self, value: Optional[str]) -> str:
        if value is None:
            return "[none]"
        return "***" if self.is_sensitive else value


@dataclass
class StructDiffResult:
    entries: List[StructDiffEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.status != "unchanged" for e in self.entries)

    @property
    def added(self) -> List[StructDiffEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[StructDiffEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[StructDiffEntry]:
        return [e for e in self.entries if e.status == "changed"]

    def summary(self) -> str:
        return (
            f"+{len(self.added)} added, "
            f"-{len(self.removed)} removed, "
            f"~{len(self.changed)} changed"
        )


_SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "api", "auth")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in _SENSITIVE_PATTERNS)


def struct_diff(
    left: Dict[str, str],
    right: Dict[str, str],
) -> StructDiffResult:
    all_keys = sorted(set(left) | set(right))
    entries: List[StructDiffEntry] = []
    for key in all_keys:
        sensitive = _is_sensitive(key)
        if key not in left:
            entries.append(StructDiffEntry(key, None, right[key], "added", sensitive))
        elif key not in right:
            entries.append(StructDiffEntry(key, left[key], None, "removed", sensitive))
        elif left[key] != right[key]:
            entries.append(StructDiffEntry(key, left[key], right[key], "changed", sensitive))
        else:
            entries.append(StructDiffEntry(key, left[key], right[key], "unchanged", sensitive))
    return StructDiffResult(entries=entries)
