"""Rename keys in a .env variable mapping with optional dry-run support."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RenameEntry:
    old_key: str
    new_key: str
    value: str


@dataclass
class RenameResult:
    renamed: List[RenameEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)  # old keys not found
    output: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return len(self.renamed) > 0

    def summary(self) -> str:
        parts = [f"{len(self.renamed)} renamed"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} not found")
        return ", ".join(parts)


def rename(
    env: Dict[str, str],
    renames: List[Tuple[str, str]],
) -> RenameResult:
    """Apply a list of (old_key, new_key) renames to *env*.

    Keys that do not exist in *env* are recorded in ``skipped``.
    If *new_key* already exists it is overwritten.
    The original dict is never mutated.
    """
    result = RenameResult(output=dict(env))

    for old_key, new_key in renames:
        if old_key not in result.output:
            result.skipped.append(old_key)
            continue

        value = result.output.pop(old_key)
        result.output[new_key] = value
        result.renamed.append(RenameEntry(old_key=old_key, new_key=new_key, value=value))

    return result
