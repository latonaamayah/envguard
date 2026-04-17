from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StackEntry:
    key: str
    values: List[str]
    final_value: str
    source_count: int

    @property
    def has_conflict(self) -> bool:
        return len(set(self.values)) > 1


@dataclass
class StackResult:
    entries: List[StackEntry] = field(default_factory=list)
    merged: Dict[str, str] = field(default_factory=dict)

    def has_conflicts(self) -> bool:
        return any(e.has_conflict for e in self.entries)

    def conflict_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.has_conflict]

    def summary(self) -> str:
        total = len(self.entries)
        conflicts = len(self.conflict_keys())
        if conflicts == 0:
            return f"{total} key(s) stacked with no conflicts."
        return f"{total} key(s) stacked, {conflicts} conflict(s) detected."


def stack(layers: List[Dict[str, str]], strategy: str = "last") -> StackResult:
    """Merge multiple env dicts (layers) into one, tracking conflicts.

    strategy:
        'last'  – last layer wins (default)
        'first' – first layer wins
    """
    all_keys: List[str] = []
    for layer in layers:
        for k in layer:
            if k not in all_keys:
                all_keys.append(k)

    entries: List[StackEntry] = []
    merged: Dict[str, str] = {}

    for key in all_keys:
        values = [layer[key] for layer in layers if key in layer]
        if strategy == "first":
            final = values[0]
        else:
            final = values[-1]
        entries.append(StackEntry(
            key=key,
            values=values,
            final_value=final,
            source_count=len(values),
        ))
        merged[key] = final

    return StackResult(entries=entries, merged=merged)
