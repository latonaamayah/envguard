"""Map environment variable keys to new names using a translation table."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MapEntry:
    original_key: str
    mapped_key: str
    value: str
    was_mapped: bool

    def message(self) -> str:
        if self.was_mapped:
            return f"{self.original_key} -> {self.mapped_key}"
        return f"{self.original_key} (unchanged)"


@dataclass
class MapResult:
    entries: List[MapEntry] = field(default_factory=list)
    unmapped_keys: List[str] = field(default_factory=list)

    def has_mapped(self) -> bool:
        return any(e.was_mapped for e in self.entries)

    def mapped_keys(self) -> List[str]:
        return [e.original_key for e in self.entries if e.was_mapped]

    def as_dict(self) -> Dict[str, str]:
        """Return the final env dict using mapped keys."""
        return {e.mapped_key: e.value for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        mapped = sum(1 for e in self.entries if e.was_mapped)
        return f"{mapped}/{total} keys mapped, {len(self.unmapped_keys)} unmapped translations"


def map_env(
    env: Dict[str, str],
    mapping: Dict[str, str],
    drop_unmapped: bool = False,
) -> MapResult:
    """Apply a key translation mapping to an env dict.

    Args:
        env: The source environment variables.
        mapping: A dict of {original_key: new_key} translations.
        drop_unmapped: If True, keys not in *mapping* are excluded from output.

    Returns:
        A MapResult containing all entries and metadata.

    Raises:
        ValueError: If *mapping* contains duplicate target keys, which would
            cause silent data loss when multiple source keys map to the same
            destination key.
    """
    target_keys = list(mapping.values())
    duplicate_targets = {k for k in target_keys if target_keys.count(k) > 1}
    if duplicate_targets:
        raise ValueError(
            f"Mapping contains duplicate target keys: {sorted(duplicate_targets)}"
        )

    result = MapResult()
    used_mappings = set()

    for key, value in env.items():
        if key in mapping:
            new_key = mapping[key]
            used_mappings.add(key)
            result.entries.append(
                MapEntry(original_key=key, mapped_key=new_key, value=value, was_mapped=True)
            )
        elif not drop_unmapped:
            result.entries.append(
                MapEntry(original_key=key, mapped_key=key, value=value, was_mapped=False)
            )

    # Track mapping keys that had no corresponding env key
    for original in mapping:
        if original not in used_mappings:
            result.unmapped_keys.append(original)

    return result
