"""Inject environment variables into a process environment or output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InjectEntry:
    key: str
    value: str
    overwritten: bool = False


@dataclass
class InjectResult:
    injected: List[InjectEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def has_injected(self) -> bool:
        return len(self.injected) > 0

    def has_skipped(self) -> bool:
        return len(self.skipped) > 0

    def summary(self) -> str:
        parts = [f"{len(self.injected)} injected"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        return ", ".join(parts)

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.injected}


def inject(
    env: Dict[str, str],
    target: Optional[Dict[str, str]] = None,
    *,
    overwrite: bool = False,
) -> InjectResult:
    """Inject *env* variables into *target* (defaults to a new dict).

    Args:
        env: Variables to inject.
        target: Destination mapping.  When *None* a fresh dict is used.
        overwrite: If *False* existing keys in *target* are skipped.

    Returns:
        InjectResult describing what was injected and what was skipped.
    """
    if target is None:
        target = {}

    result = InjectResult()

    for key, value in env.items():
        if key in target and not overwrite:
            result.skipped.append(key)
            continue
        overwritten = key in target
        target[key] = value
        result.injected.append(InjectEntry(key=key, value=value, overwritten=overwritten))

    return result
