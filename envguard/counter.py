from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CountEntry:
    key: str
    value_length: int
    is_empty: bool
    is_numeric: bool
    is_boolean: bool


@dataclass
class CountResult:
    entries: List[CountEntry] = field(default_factory=list)
    _counts: Dict[str, int] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._counts = {
            "total": len(self.entries),
            "empty": sum(1 for e in self.entries if e.is_empty),
            "numeric": sum(1 for e in self.entries if e.is_numeric),
            "boolean": sum(1 for e in self.entries if e.is_boolean),
        }

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def empty_count(self) -> int:
        return sum(1 for e in self.entries if e.is_empty)

    @property
    def numeric_count(self) -> int:
        return sum(1 for e in self.entries if e.is_numeric)

    @property
    def boolean_count(self) -> int:
        return sum(1 for e in self.entries if e.is_boolean)

    def has_entries(self) -> bool:
        return len(self.entries) > 0

    def summary(self) -> str:
        return (
            f"{self.total} variables: {self.empty_count} empty, "
            f"{self.numeric_count} numeric, {self.boolean_count} boolean"
        )


_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0"}


def count(env: Dict[str, str]) -> CountResult:
    entries = []
    for key, value in env.items():
        is_empty = value.strip() == ""
        is_numeric = False
        is_boolean = value.strip().lower() in _BOOL_VALUES
        if not is_empty and not is_boolean:
            try:
                float(value.strip())
                is_numeric = True
            except ValueError:
                pass
        entries.append(CountEntry(
            key=key,
            value_length=len(value),
            is_empty=is_empty,
            is_numeric=is_numeric,
            is_boolean=is_boolean,
        ))
    return CountResult(entries=entries)
