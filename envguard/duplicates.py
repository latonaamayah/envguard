"""Detect duplicate keys within one or more .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DuplicateEntry:
    key: str
    occurrences: List[Tuple[str, int]]  # (source_label, line_number)

    @property
    def count(self) -> int:
        return len(self.occurrences)


@dataclass
class DuplicateResult:
    duplicates: List[DuplicateEntry] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicates) > 0

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        lines = [f"{len(self.duplicates)} duplicate key(s) detected:"]
        for entry in self.duplicates:
            locs = ", ".join(f"{src}:{ln}" for src, ln in entry.occurrences)
            lines.append(f"  {entry.key} ({entry.count}x) — {locs}")
        return "\n".join(lines)


def _scan_file(path: str) -> Dict[str, List[int]]:
    """Return a mapping of key -> list of line numbers where it appears."""
    seen: Dict[str, List[int]] = {}
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            if not key:
                continue
            seen.setdefault(key, []).append(lineno)
    return seen


def find_duplicates(*env_paths: str) -> DuplicateResult:
    """Scan one or more env files and report keys that appear more than once.

    When multiple files are provided the key namespace is shared, so the same
    key defined in two different files is also considered a duplicate.
    """
    combined: Dict[str, List[Tuple[str, int]]] = {}

    for path in env_paths:
        label = path
        occurrences = _scan_file(path)
        for key, lines in occurrences.items():
            for ln in lines:
                combined.setdefault(key, []).append((label, ln))

    entries = [
        DuplicateEntry(key=k, occurrences=v)
        for k, v in combined.items()
        if len(v) > 1
    ]
    entries.sort(key=lambda e: e.key)
    return DuplicateResult(duplicates=entries)
