"""Tag environment variables with custom labels for categorization."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class TagEntry:
    key: str
    value: str
    tags: List[str]


@dataclass
class TagResult:
    tagged: List[TagEntry] = field(default_factory=list)
    untagged_keys: List[str] = field(default_factory=list)

    def has_tagged(self) -> bool:
        return len(self.tagged) > 0

    def keys_for_tag(self, tag: str) -> List[str]:
        return [e.key for e in self.tagged if tag in e.tags]

    def all_tags(self) -> Set[str]:
        result: Set[str] = set()
        for entry in self.tagged:
            result.update(entry.tags)
        return result

    def summary(self) -> str:
        total = len(self.tagged) + len(self.untagged_keys)
        return (
            f"{len(self.tagged)} tagged, {len(self.untagged_keys)} untagged "
            f"out of {total} variables"
        )


def tag(
    env: Dict[str, str],
    tag_rules: Dict[str, List[str]],
) -> TagResult:
    """Apply tag_rules to env variables.

    tag_rules maps a tag label to a list of key prefixes/substrings.
    A variable is tagged with every label whose patterns match its key.
    """
    result = TagResult()

    for key, value in env.items():
        matched_tags: List[str] = []
        for label, patterns in tag_rules.items():
            if any(pattern.upper() in key.upper() for pattern in patterns):
                matched_tags.append(label)

        if matched_tags:
            result.tagged.append(TagEntry(key=key, value=value, tags=matched_tags))
        else:
            result.untagged_keys.append(key)

    return result
