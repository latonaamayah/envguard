from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasEntry:
    original_key: str
    alias_key: str
    value: str

    @property
    def message(self) -> str:
        return f"{self.alias_key} -> {self.original_key} = {self.value!r}"


@dataclass
class AliasResult:
    entries: List[AliasEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def has_aliases(self) -> bool:
        return len(self.entries) > 0

    @property
    def aliased_keys(self) -> List[str]:
        return [e.alias_key for e in self.entries]

    @property
    def original_keys(self) -> List[str]:
        return [e.original_key for e in self.entries]

    def as_dict(self) -> Dict[str, str]:
        return {e.alias_key: e.value for e in self.entries}

    def summary(self) -> str:
        if not self.has_aliases:
            return "No aliases created."
        lines = [f"Aliases created: {len(self.entries)}"]
        for e in self.entries:
            lines.append(f"  {e.message}")
        if self.skipped:
            lines.append(f"Skipped (missing source): {', '.join(self.skipped)}")
        return "\n".join(lines)


def alias(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> AliasResult:
    """Create alias keys in env from mapping {alias_key: original_key}."""
    result = AliasResult()
    for alias_key, original_key in mapping.items():
        if original_key not in env:
            result.skipped.append(original_key)
            continue
        if alias_key in env and not overwrite:
            result.skipped.append(alias_key)
            continue
        value = env[original_key]
        result.entries.append(AliasEntry(
            original_key=original_key,
            alias_key=alias_key,
            value=value,
        ))
    return result
