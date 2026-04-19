from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StrikeEntry:
    key: str
    value: str
    reason: str

    def message(self) -> str:
        return f"{self.key}: {self.reason}"


@dataclass
class StrikeResult:
    struck: List[StrikeEntry] = field(default_factory=list)
    kept: Dict[str, str] = field(default_factory=dict)

    def has_struck(self) -> bool:
        return len(self.struck) > 0

    def struck_keys(self) -> List[str]:
        return [e.key for e in self.struck]

    def summary(self) -> str:
        return f"{len(self.struck)} key(s) struck, {len(self.kept)} kept"

    def as_dict(self) -> Dict[str, str]:
        return dict(self.kept)


def strike(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    keys: Optional[List[str]] = None,
    empty_only: bool = False,
) -> StrikeResult:
    """Remove keys from env matching patterns, explicit keys, or empty values."""
    import re

    result = StrikeResult()
    patterns = patterns or []
    keys_set = set(keys or [])

    for k, v in env.items():
        reason: Optional[str] = None

        if k in keys_set:
            reason = "explicitly struck"
        elif any(re.search(p, k) for p in patterns):
            reason = "matched pattern"
        elif empty_only and v.strip() == "":
            reason = "empty value"

        if reason:
            result.struck.append(StrikeEntry(key=k, value=v, reason=reason))
        else:
            result.kept[k] = v

    return result
