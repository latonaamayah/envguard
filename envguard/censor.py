from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_PATTERNS = ("password", "secret", "token", "api_key", "apikey", "private", "auth", "credential")
_CENSOR_MASK = "***"


@dataclass
class CensorEntry:
    key: str
    original: str
    censored: str
    was_censored: bool


@dataclass
class CensorResult:
    entries: List[CensorEntry] = field(default_factory=list)

    def has_censored(self) -> bool:
        return any(e.was_censored for e in self.entries)

    def censored_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_censored]

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.censored for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        censored = len(self.censored_keys())
        return f"{censored}/{total} keys censored."


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in _SENSITIVE_PATTERNS)


def censor(env: Dict[str, str], keys: List[str] | None = None) -> CensorResult:
    result = CensorResult()
    for key, value in env.items():
        should_censor = (keys is not None and key in keys) or (keys is None and _is_sensitive(key))
        censored_value = _CENSOR_MASK if should_censor else value
        result.entries.append(CensorEntry(
            key=key,
            original=value,
            censored=censored_value,
            was_censored=should_censor,
        ))
    return result
