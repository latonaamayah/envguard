from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LinkEntry:
    key: str
    value: str
    references: List[str] = field(default_factory=list)
    broken: List[str] = field(default_factory=list)

    @property
    def has_broken(self) -> bool:
        return len(self.broken) > 0


@dataclass
class LinkResult:
    entries: List[LinkEntry] = field(default_factory=list)

    @property
    def has_broken(self) -> bool:
        return any(e.has_broken for e in self.entries)

    @property
    def broken_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.has_broken]

    def summary(self) -> str:
        total = len(self.entries)
        broken = len(self.broken_keys)
        return f"{total} entries checked, {broken} with broken references."


_REF_PATTERN = __import__("re").compile(r"\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)")


def link(env: Dict[str, str]) -> LinkResult:
    """Detect inter-variable references and report broken ones."""
    entries: List[LinkEntry] = []
    for key, value in env.items():
        refs: List[str] = []
        broken: List[str] = []
        for m in _REF_PATTERN.finditer(value):
            ref = m.group(1) or m.group(2)
            refs.append(ref)
            if ref not in env:
                broken.append(ref)
        entries.append(LinkEntry(key=key, value=value, references=refs, broken=broken))
    return LinkResult(entries=entries)
