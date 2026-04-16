from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MigrateEntry:
    old_key: str
    new_key: str
    value: str
    renamed: bool = True

    @property
    def message(self) -> str:
        if self.renamed:
            return f"{self.old_key} -> {self.new_key}"
        return f"{self.old_key} (unchanged)"


@dataclass
class MigrateResult:
    entries: List[MigrateEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    output: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return any(e.renamed for e in self.entries)

    @property
    def renamed_keys(self) -> List[str]:
        return [e.old_key for e in self.entries if e.renamed]

    def summary(self) -> str:
        n = len(self.renamed_keys)
        s = len(self.skipped)
        return f"{n} key(s) migrated, {s} skipped"


def migrate(
    env: Dict[str, str],
    mapping: Dict[str, str],
    keep_old: bool = False,
) -> MigrateResult:
    """Rename keys in env according to mapping.

    Args:
        env: Source environment variables.
        mapping: Dict of {old_key: new_key}.
        keep_old: If True, retain original key alongside new key.
    """
    result = MigrateResult()
    output: Dict[str, str] = dict(env)

    for old_key, new_key in mapping.items():
        if old_key not in env:
            result.skipped.append(old_key)
            continue
        value = env[old_key]
        output[new_key] = value
        if not keep_old:
            output.pop(old_key, None)
        result.entries.append(MigrateEntry(old_key=old_key, new_key=new_key, value=value))

    # carry over keys not in mapping
    result.output = output
    return result
