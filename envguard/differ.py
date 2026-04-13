"""Diff two .env files against a schema to highlight changes and regressions."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.schema import Schema


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'type_changed'
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    declared_in_schema: bool = False


@dataclass
class DiffResult:
    entries: List[DiffEntry] = field(default_factory=list)
    schema_regressions: List[str] = field(default_factory=list)  # required vars removed

    @property
    def has_changes(self) -> bool:
        return bool(self.entries)

    @property
    def has_regressions(self) -> bool:
        return bool(self.schema_regressions)

    def summary(self) -> str:
        added = sum(1 for e in self.entries if e.status == "added")
        removed = sum(1 for e in self.entries if e.status == "removed")
        changed = sum(1 for e in self.entries if e.status == "changed")
        regressions = len(self.schema_regressions)
        parts = []
        if added:
            parts.append(f"{added} added")
        if removed:
            parts.append(f"{removed} removed")
        if changed:
            parts.append(f"{changed} changed")
        if regressions:
            parts.append(f"{regressions} regression(s)")
        return ", ".join(parts) if parts else "no changes"


def diff_envs(
    old_env: Dict[str, str],
    new_env: Dict[str, str],
    schema: Optional[Schema] = None,
) -> DiffResult:
    """Compare two env dicts and return a DiffResult."""
    result = DiffResult()
    schema_keys: Dict[str, bool] = {}
    required_keys = set()

    if schema:
        for var in schema.variables:
            schema_keys[var.name] = True
            if var.required:
                required_keys.add(var.name)

    all_keys = set(old_env) | set(new_env)

    for key in sorted(all_keys):
        in_old = key in old_env
        in_new = key in new_env
        declared = key in schema_keys

        if in_old and not in_new:
            result.entries.append(
                DiffEntry(key=key, status="removed", old_value=old_env[key], declared_in_schema=declared)
            )
            if key in required_keys:
                result.schema_regressions.append(key)
        elif in_new and not in_old:
            result.entries.append(
                DiffEntry(key=key, status="added", new_value=new_env[key], declared_in_schema=declared)
            )
        elif old_env[key] != new_env[key]:
            result.entries.append(
                DiffEntry(
                    key=key,
                    status="changed",
                    old_value=old_env[key],
                    new_value=new_env[key],
                    declared_in_schema=declared,
                )
            )

    return result
