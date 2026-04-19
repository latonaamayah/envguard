from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import hashlib
import re

_SENSITIVE_PATTERNS = re.compile(
    r"(password|secret|token|api_?key|private|credential)",
    re.IGNORECASE,
)


@dataclass
class ScramblerEntry:
    key: str
    original: str
    scrambled: str

    @property
    def changed(self) -> bool:
        return self.original != self.scrambled


@dataclass
class ScramblerResult:
    entries: List[ScramblerEntry] = field(default_factory=list)

    @property
    def has_scrambled(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def scrambled_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.scrambled for e in self.entries}

    def summary(self) -> str:
        total = len(self.scrambled_keys)
        if total == 0:
            return "No keys scrambled."
        return f"{total} key(s) scrambled: {', '.join(self.scrambled_keys)}"


def _is_sensitive(key: str) -> bool:
    return bool(_SENSITIVE_PATTERNS.search(key))


def _scramble_value(value: str, key: str) -> str:
    digest = hashlib.sha256(f"{key}:{value}".encode()).hexdigest()
    return digest[:len(value)] if len(value) <= 64 else digest


def scramble(
    env: Dict[str, str],
    keys: List[str] | None = None,
    auto_detect: bool = True,
) -> ScramblerResult:
    result = ScramblerResult()
    targets = set(keys or [])
    if auto_detect:
        targets |= {k for k in env if _is_sensitive(k)}
    for key, value in env.items():
        if key in targets:
            scrambled = _scramble_value(value, key)
        else:
            scrambled = value
        result.entries.append(ScramblerEntry(key=key, original=value, scrambled=scrambled))
    return result
