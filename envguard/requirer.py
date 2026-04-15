"""Checks that all required env vars from a schema are present in an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.schema import Schema


@dataclass
class RequireEntry:
    key: str
    reason: str  # 'missing' | 'empty'

    @property
    def message(self) -> str:
        if self.reason == "empty":
            return f"{self.key} is required but has an empty value"
        return f"{self.key} is required but not present"


@dataclass
class RequireResult:
    missing: List[RequireEntry] = field(default_factory=list)
    satisfied: List[str] = field(default_factory=list)

    @property
    def has_missing(self) -> bool:
        return bool(self.missing)

    @property
    def missing_keys(self) -> List[str]:
        return [e.key for e in self.missing]

    def summary(self) -> str:
        total = len(self.missing) + len(self.satisfied)
        if not self.has_missing:
            return f"All {total} required variable(s) are present."
        keys = ", ".join(self.missing_keys)
        return (
            f"{len(self.missing)} required variable(s) missing or empty: {keys}"
        )


def require(schema: Schema, env: Dict[str, str]) -> RequireResult:
    """Validate that every required variable in *schema* exists in *env*."""
    result = RequireResult()

    for var in schema.variables:
        if not var.required:
            continue

        if var.name not in env:
            result.missing.append(RequireEntry(key=var.name, reason="missing"))
        elif env[var.name].strip() == "":
            result.missing.append(RequireEntry(key=var.name, reason="empty"))
        else:
            result.satisfied.append(var.name)

    return result
