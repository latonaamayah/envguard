"""Detect and report deprecated environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationEntry:
    key: str
    reason: str
    replacement: Optional[str] = None

    def message(self) -> str:
        msg = f"{self.key} is deprecated: {self.reason}"
        if self.replacement:
            msg += f" — use '{self.replacement}' instead"
        return msg


@dataclass
class DeprecationResult:
    entries: List[DeprecationEntry] = field(default_factory=list)
    clean: List[str] = field(default_factory=list)

    def has_deprecations(self) -> bool:
        return len(self.entries) > 0

    def deprecated_keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def summary(self) -> str:
        total = len(self.entries) + len(self.clean)
        if not self.has_deprecations():
            return f"No deprecated keys found ({total} checked)."
        keys = ", ".join(self.deprecated_keys())
        return (
            f"{len(self.entries)} deprecated key(s) found out of {total} checked: {keys}"
        )


def deprecate(
    env: Dict[str, str],
    deprecated_map: Dict[str, Dict[str, str]],
) -> DeprecationResult:
    """Check env keys against a map of deprecated variable definitions.

    Args:
        env: Mapping of environment variable names to their values.
        deprecated_map: Mapping of deprecated key names to metadata dicts.
            Each metadata dict may contain:
              - 'reason' (str, required): why the key is deprecated.
              - 'replacement' (str, optional): the preferred key to use instead.

    Returns:
        A DeprecationResult with entries for each deprecated key found.
    """
    result = DeprecationResult()
    for key in env:
        if key in deprecated_map:
            meta = deprecated_map[key]
            entry = DeprecationEntry(
                key=key,
                reason=meta.get("reason", "deprecated"),
                replacement=meta.get("replacement"),
            )
            result.entries.append(entry)
        else:
            result.clean.append(key)
    return result
