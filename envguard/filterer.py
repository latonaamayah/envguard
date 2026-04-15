"""Filter environment variables by prefix, suffix, or pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: Dict[str, str] = field(default_factory=dict)

    def has_matches(self) -> bool:
        return bool(self.matched)

    def summary(self) -> str:
        return (
            f"{len(self.matched)} matched, {len(self.excluded)} excluded"
        )


def filter_env(
    env: Dict[str, str],
    *,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    pattern: Optional[str] = None,
    keys: Optional[List[str]] = None,
    invert: bool = False,
) -> FilterResult:
    """Return a FilterResult partitioning *env* into matched/excluded.

    At least one of prefix, suffix, pattern, or keys must be provided.
    When *invert* is True the match logic is flipped.
    """
    if not any([prefix, suffix, pattern, keys]):
        raise ValueError(
            "Provide at least one of: prefix, suffix, pattern, keys"
        )

    compiled = re.compile(pattern) if pattern else None
    key_set = set(keys) if keys else None

    result = FilterResult()
    for k, v in env.items():
        matches = False
        if prefix and k.startswith(prefix):
            matches = True
        if suffix and k.endswith(suffix):
            matches = True
        if compiled and compiled.search(k):
            matches = True
        if key_set and k in key_set:
            matches = True

        if invert:
            matches = not matches

        if matches:
            result.matched[k] = v
        else:
            result.excluded[k] = v

    return result
