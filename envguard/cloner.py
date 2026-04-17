from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CloneEntry:
    key: str
    original_value: str
    cloned_value: str
    new_key: str

    @property
    def changed_key(self) -> bool:
        return self.key != self.new_key


@dataclass
class CloneResult:
    entries: List[CloneEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def has_clones(self) -> bool:
        return len(self.entries) > 0

    @property
    def cloned_keys(self) -> List[str]:
        return [e.new_key for e in self.entries]

    def as_dict(self) -> Dict[str, str]:
        result = {}
        for entry in self.entries:
            result[entry.new_key] = entry.cloned_value
        return result

    def summary(self) -> str:
        if not self.has_clones:
            return "No keys cloned."
        lines = [f"Cloned {len(self.entries)} key(s):"]
        for e in self.entries:
            lines.append(f"  {e.key} -> {e.new_key}")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} missing key(s): {', '.join(self.skipped)}")
        return "\n".join(lines)


def clone(
    env: Dict[str, str],
    mapping: Dict[str, str],
    transform: Optional[str] = None,
) -> CloneResult:
    """Clone keys from env into new keys, optionally transforming values.

    Args:
        env: Source environment variables.
        mapping: Dict of {source_key: new_key}.
        transform: Optional value transform: 'upper', 'lower', or None.
    """
    result = CloneResult()
    for src_key, new_key in mapping.items():
        if src_key not in env:
            result.skipped.append(src_key)
            continue
        value = env[src_key]
        if transform == "upper":
            value = value.upper()
        elif transform == "lower":
            value = value.lower()
        result.entries.append(CloneEntry(
            key=src_key,
            original_value=env[src_key],
            cloned_value=value,
            new_key=new_key,
        ))
    return result
