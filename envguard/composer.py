"""envguard.composer — Compose multiple .env files into a single merged output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ComposeEntry:
    key: str
    value: str
    source: str  # filename that contributed this key
    overridden_by: Optional[str] = None  # later file that overwrote it

    @property
    def was_overridden(self) -> bool:
        return self.overridden_by is not None


@dataclass
class ComposeResult:
    entries: List[ComposeEntry] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    @property
    def has_overrides(self) -> bool:
        return any(e.was_overridden for e in self.entries)

    @property
    def merged(self) -> Dict[str, str]:
        """Return the final merged key→value mapping."""
        result: Dict[str, str] = {}
        for entry in self.entries:
            if not entry.was_overridden:
                result[entry.key] = entry.value
        return result

    @property
    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_overridden]

    def summary(self) -> str:
        total = len(self.merged)
        overrides = len(self.overridden_keys)
        src_count = len(self.sources)
        return (
            f"{total} key(s) composed from {src_count} source(s); "
            f"{overrides} override(s) applied."
        )


def compose(envs: List[Dict[str, str]], sources: Optional[List[str]] = None) -> ComposeResult:
    """Compose a list of env dicts in order; later dicts override earlier ones."""
    if sources is None:
        sources = [f"source_{i}" for i in range(len(envs))]

    # Track all entries including overridden ones for full audit trail
    all_entries: List[ComposeEntry] = []
    # key -> index of the winning entry in all_entries
    winner: Dict[str, int] = {}

    for src, env in zip(sources, envs):
        for key, value in env.items():
            entry = ComposeEntry(key=key, value=value, source=src)
            if key in winner:
                # Mark the previous winner as overridden
                all_entries[winner[key]].overridden_by = src
            winner[key] = len(all_entries)
            all_entries.append(entry)

    return ComposeResult(entries=all_entries, sources=list(sources))
