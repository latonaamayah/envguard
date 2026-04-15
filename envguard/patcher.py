"""Patch a .env file by applying a dict of key-value updates."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchEntry:
    key: str
    old_value: Optional[str]
    new_value: str
    action: str  # 'added' | 'updated' | 'unchanged'


@dataclass
class PatchResult:
    patched: Dict[str, str]
    entries: List[PatchEntry] = field(default_factory=list)

    def has_changes(self) -> bool:
        return any(e.action != "unchanged" for e in self.entries)

    def summary(self) -> str:
        added = sum(1 for e in self.entries if e.action == "added")
        updated = sum(1 for e in self.entries if e.action == "updated")
        return f"{added} added, {updated} updated, {len(self.entries) - added - updated} unchanged"


def patch(env: Dict[str, str], updates: Dict[str, str]) -> PatchResult:
    """Apply *updates* on top of *env*, returning a new merged mapping.

    Keys present in *updates* are added or overwritten; all other keys in
    *env* are preserved without modification.
    """
    result: Dict[str, str] = dict(env)
    entries: List[PatchEntry] = []

    for key, new_value in updates.items():
        old_value = env.get(key)
        if old_value is None:
            action = "added"
        elif old_value == new_value:
            action = "unchanged"
        else:
            action = "updated"
        result[key] = new_value
        entries.append(PatchEntry(key=key, old_value=old_value, new_value=new_value, action=action))

    return PatchResult(patched=result, entries=entries)
