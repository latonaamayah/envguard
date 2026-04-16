from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ExtractEntry:
    key: str
    value: str
    pattern: str


@dataclass
class ExtractResult:
    matches: List[ExtractEntry] = field(default_factory=list)
    unmatched_keys: List[str] = field(default_factory=list)

    def has_matches(self) -> bool:
        return len(self.matches) > 0

    def keys_for_pattern(self, pattern: str) -> List[str]:
        return [e.key for e in self.matches if e.pattern == pattern]

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.matches}

    def summary(self) -> str:
        if not self.has_matches():
            return "No keys matched the given patterns."
        return (
            f"{len(self.matches)} key(s) extracted, "
            f"{len(self.unmatched_keys)} key(s) unmatched."
        )


def extract(
    env: Dict[str, str],
    patterns: List[str],
    match_values: bool = False,
) -> ExtractResult:
    """Extract env vars whose keys (or optionally values) match any of the given regex patterns."""
    result = ExtractResult()
    matched_keys: set = set()

    for key, value in env.items():
        target = value if match_values else key
        for pattern in patterns:
            try:
                if re.search(pattern, target):
                    result.matches.append(ExtractEntry(key=key, value=value, pattern=pattern))
                    matched_keys.add(key)
                    break
            except re.error:
                continue

    for key in env:
        if key not in matched_keys:
            result.unmatched_keys.append(key)

    return result
