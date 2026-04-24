from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CombineEntry:
    key: str
    value: str
    sources: List[str] = field(default_factory=list)
    overridden: bool = False

    def message(self) -> str:
        if self.overridden:
            return f"{self.key} combined from {len(self.sources)} source(s) (last-write wins)"
        return f"{self.key} present in {len(self.sources)} source(s)"


@dataclass
class CombineResult:
    entries: List[CombineEntry] = field(default_factory=list)
    source_labels: List[str] = field(default_factory=list)

    def has_overrides(self) -> bool:
        return any(e.overridden for e in self.entries)

    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.overridden]

    def merged(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        overrides = len(self.overridden_keys())
        sources = len(self.source_labels)
        return (
            f"{total} key(s) combined from {sources} source(s); "
            f"{overrides} override(s) applied"
        )


def combine(
    sources: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> CombineResult:
    """Merge multiple env dicts; later sources override earlier ones."""
    if labels is None:
        labels = [f"source_{i}" for i in range(len(sources))]

    # Track which keys appeared in which source indices
    key_sources: Dict[str, List[str]] = {}
    merged: Dict[str, str] = {}
    seen_keys: Dict[str, str] = {}  # key -> first value

    for idx, source in enumerate(sources):
        label = labels[idx] if idx < len(labels) else f"source_{idx}"
        for key, value in source.items():
            if key not in key_sources:
                key_sources[key] = []
                seen_keys[key] = value
            key_sources[key].append(label)
            merged[key] = value

    entries: List[CombineEntry] = []
    for key, value in merged.items():
        src_list = key_sources[key]
        overridden = len(src_list) > 1
        entries.append(
            CombineEntry(
                key=key,
                value=value,
                sources=src_list,
                overridden=overridden,
            )
        )

    entries.sort(key=lambda e: e.key)
    return CombineResult(entries=entries, source_labels=labels)
