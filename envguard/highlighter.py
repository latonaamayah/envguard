from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class HighlightEntry:
    key: str
    value: str
    patterns: List[str]

    def matched_patterns(self) -> List[str]:
        return self.patterns

    def is_highlighted(self) -> bool:
        return len(self.patterns) > 0


@dataclass
class HighlightResult:
    entries: List[HighlightEntry] = field(default_factory=list)

    def has_highlights(self) -> bool:
        return any(e.is_highlighted() for e in self.entries)

    def highlighted_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_highlighted()]

    def keys_for_pattern(self, pattern: str) -> List[str]:
        return [e.key for e in self.entries if pattern in e.patterns]

    def summary(self) -> str:
        total = len(self.entries)
        highlighted = len(self.highlighted_keys())
        return f"{highlighted}/{total} keys matched highlight patterns."


def highlight(
    env: Dict[str, str],
    patterns: List[str],
) -> HighlightResult:
    """Match env keys or values against a list of substring/glob patterns."""
    import fnmatch

    result = HighlightResult()
    for key, value in env.items():
        matched: List[str] = []
        for pattern in patterns:
            if fnmatch.fnmatch(key, pattern) or fnmatch.fnmatch(value, pattern):
                matched.append(pattern)
            elif pattern.lower() in key.lower() or pattern.lower() in value.lower():
                matched.append(pattern)
        entry = HighlightEntry(key=key, value=value, patterns=list(dict.fromkeys(matched)))
        result.entries.append(entry)
    return result
