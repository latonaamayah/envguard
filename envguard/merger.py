"""Merge multiple .env files with precedence rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from envguard.loader import load_env_file


@dataclass
class MergeConflict:
    key: str
    values: List[Tuple[str, str]]  # (source_path, value)

    @property
    def winning_value(self) -> str:
        """The value that wins (last source wins)."""
        return self.values[-1][1]


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: List[MergeConflict] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def summary(self) -> str:
        lines = [f"Merged {len(self.sources)} source(s), {len(self.merged)} variable(s)"]
        if self.conflicts:
            lines.append(f"  {len(self.conflicts)} conflict(s) resolved (last-wins)")
        return "\n".join(lines)


def merge(env_paths: List[str], override: bool = True) -> MergeResult:
    """Merge multiple env files. Later files take precedence when override=True."""
    result = MergeResult()
    key_sources: Dict[str, List[Tuple[str, str]]] = {}

    for path in env_paths:
        resolved = str(Path(path).resolve())
        result.sources.append(resolved)
        env_vars = load_env_file(path)

        for key, value in env_vars.items():
            if key not in key_sources:
                key_sources[key] = []
            key_sources[key].append((resolved, value))

    for key, entries in key_sources.items():
        if len(entries) > 1:
            conflict = MergeConflict(key=key, values=entries)
            result.conflicts.append(conflict)
            result.merged[key] = entries[-1][1] if override else entries[0][1]
        else:
            result.merged[key] = entries[0][1]

    return result
