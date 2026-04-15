"""Trimmer: removes unused or undeclared variables from a .env file based on a schema."""

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.schema import Schema


@dataclass
class TrimResult:
    original: Dict[str, str]
    trimmed: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)

    def has_removed(self) -> bool:
        return len(self.removed_keys) > 0

    def summary(self) -> str:
        if not self.has_removed():
            return "No variables removed — env is already clean."
        keys = ", ".join(self.removed_keys)
        return f"Removed {len(self.removed_keys)} undeclared variable(s): {keys}"


def trim(env: Dict[str, str], schema: Schema) -> TrimResult:
    """Remove variables from env that are not declared in the schema.

    Args:
        env: Parsed environment variables as a dict.
        schema: Schema instance defining declared variables.

    Returns:
        TrimResult with the cleaned env and list of removed keys.
    """
    declared_keys = {var.name for var in schema.variables}
    removed: List[str] = []
    trimmed: Dict[str, str] = {}

    for key, value in env.items():
        if key in declared_keys:
            trimmed[key] = value
        else:
            removed.append(key)

    removed.sort()
    return TrimResult(original=dict(env), trimmed=trimmed, removed_keys=removed)
