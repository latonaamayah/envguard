from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class PruneEntry:
    key: str
    value: str
    reason: str


@dataclass
class PruneResult:
    pruned: List[PruneEntry] = field(default_factory=list)
    kept: Dict[str, str] = field(default_factory=dict)

    def has_pruned(self) -> bool:
        return len(self.pruned) > 0

    def pruned_keys(self) -> List[str]:
        return [e.key for e in self.pruned]

    def summary(self) -> str:
        if not self.has_pruned():
            return "No variables pruned."
        keys = ", ".join(self.pruned_keys())
        return f"Pruned {len(self.pruned)} variable(s): {keys}"


def prune(
    env: Dict[str, str],
    empty: bool = True,
    placeholders: bool = True,
    keys: Set[str] | None = None,
) -> PruneResult:
    """Remove variables from env based on pruning rules."""
    _PLACEHOLDER_VALUES = {"changeme", "todo", "fixme", "placeholder", "xxx", "<value>", "your_value_here"}
    result = PruneResult()

    for k, v in env.items():
        reason = None

        if keys and k in keys:
            reason = "explicitly selected"
        elif empty and v.strip() == "":
            reason = "empty value"
        elif placeholders and v.strip().lower() in _PLACEHOLDER_VALUES:
            reason = "placeholder value"

        if reason:
            result.pruned.append(PruneEntry(key=k, value=v, reason=reason))
        else:
            result.kept[k] = v

    return result
