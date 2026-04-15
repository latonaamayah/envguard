"""Groups environment variables by prefix or custom category."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class GroupResult:
    groups: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    ungrouped: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def has_groups(self) -> bool:
        return bool(self.groups)

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def summary(self) -> str:
        parts = [f"{len(self.groups)} group(s) found"]
        for name in self.group_names:
            parts.append(f"  [{name}]: {len(self.groups[name])} variable(s)")
        if self.ungrouped:
            parts.append(f"  [ungrouped]: {len(self.ungrouped)} variable(s)")
        return "\n".join(parts)


def _extract_prefix(key: str, separator: str = "_") -> str:
    """Return the first segment of a key split by separator."""
    parts = key.split(separator, 1)
    return parts[0].upper() if len(parts) > 1 else ""


def group(
    env: Dict[str, str],
    *,
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Group env vars by key prefix.

    Args:
        env: Mapping of variable names to values.
        separator: Character used to split key into prefix + rest.
        min_group_size: Minimum number of keys required to form a group.

    Returns:
        GroupResult with populated groups and ungrouped entries.
    """
    from collections import defaultdict

    buckets: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    no_prefix: List[Tuple[str, str]] = []

    for key, value in env.items():
        prefix = _extract_prefix(key, separator)
        if prefix:
            buckets[prefix].append((key, value))
        else:
            no_prefix.append((key, value))

    result = GroupResult()
    for prefix, entries in buckets.items():
        if len(entries) >= min_group_size:
            result.groups[prefix] = entries
        else:
            no_prefix.extend(entries)

    result.ungrouped = no_prefix
    return result
