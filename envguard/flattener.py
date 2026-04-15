"""Flattens nested environment variable structures into dot-notation keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FlattenEntry:
    original_key: str
    flat_key: str
    value: str

    @property
    def changed(self) -> bool:
        return self.original_key != self.flat_key


@dataclass
class FlattenResult:
    entries: List[FlattenEntry] = field(default_factory=list)
    flattened: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return any(e.changed for e in self.entries)

    def summary(self) -> str:
        changed = sum(1 for e in self.entries if e.changed)
        total = len(self.entries)
        return f"{changed} of {total} keys normalised to flat dot-notation."


def _flatten_key(key: str, separator: str = "__") -> str:
    """Convert double-underscore-separated segments to dot-notation.

    Example: ``DB__HOST`` -> ``db.host``
    """
    if separator not in key:
        return key
    return key.replace(separator, ".").lower()


def flatten(
    env: Dict[str, str],
    separator: str = "__",
    preserve_case: bool = False,
) -> FlattenResult:
    """Flatten *env* keys that contain *separator* into dot-notation.

    Parameters
    ----------
    env:
        Mapping of raw environment variable names to their values.
    separator:
        The token used to denote hierarchy (default ``__``).
    preserve_case:
        When *True* the resulting dot-key retains the original casing;
        otherwise it is lowercased.
    """
    result = FlattenResult()
    for key, value in env.items():
        flat = _flatten_key(key, separator)
        if preserve_case and separator in key:
            flat = key.replace(separator, ".")
        entry = FlattenEntry(original_key=key, flat_key=flat, value=value)
        result.entries.append(entry)
        result.flattened[flat] = value
    return result
