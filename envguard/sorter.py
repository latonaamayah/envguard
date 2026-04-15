"""Sort .env file variables by key, group, or declaration order."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_vars: Dict[str, str]
    order: List[str]
    strategy: str

    @property
    def has_changes(self) -> bool:
        return list(self.original.keys()) != self.order

    @property
    def summary(self) -> str:
        if not self.has_changes:
            return "Already sorted — no changes needed."
        return (
            f"Sorted {len(self.order)} variable(s) using '{self.strategy}' strategy."
        )


def _group_key(key: str) -> str:
    """Return a grouping prefix based on the key name (e.g. DB_, APP_)."""
    parts = key.split("_", 1)
    return parts[0].upper() if len(parts) > 1 else "MISC"


def sort(
    env: Dict[str, str],
    strategy: str = "alpha",
    reverse: bool = False,
    groups: Optional[List[str]] = None,
) -> SortResult:
    """Sort environment variables.

    Strategies:
      - 'alpha'  : alphabetical by key
      - 'group'  : grouped by prefix (DB_, APP_, etc.), then alphabetical
      - 'length' : ascending key length
    """
    keys = list(env.keys())

    if strategy == "alpha":
        ordered = sorted(keys, reverse=reverse)
    elif strategy == "group":
        priority = {g.upper(): i for i, g in enumerate(groups or [])}
        ordered = sorted(
            keys,
            key=lambda k: (priority.get(_group_key(k), 999), k),
            reverse=reverse,
        )
    elif strategy == "length":
        ordered = sorted(keys, key=len, reverse=reverse)
    else:
        raise ValueError(f"Unknown sort strategy: '{strategy}'")

    sorted_vars = {k: env[k] for k in ordered}
    return SortResult(
        original=dict(env),
        sorted_vars=sorted_vars,
        order=ordered,
        strategy=strategy,
    )
