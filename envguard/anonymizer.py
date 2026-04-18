from dataclasses import dataclass, field
from typing import Dict, List
import re

_SENSITIVE_PATTERNS = re.compile(
    r"(password|secret|token|api_key|apikey|private|credential|auth)",
    re.IGNORECASE,
)

_ANON_PLACEHOLDER = "***"


@dataclass
class AnonymizeEntry:
    key: str
    original: str
    anonymized: str

    @property
    def changed(self) -> bool:
        return self.original != self.anonymized


@dataclass
class AnonymizeResult:
    entries: List[AnonymizeEntry] = field(default_factory=list)

    @property
    def has_anonymized(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def anonymized_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.anonymized for e in self.entries}

    def summary(self) -> str:
        total = len(self.anonymized_keys)
        if total == 0:
            return "No values anonymized."
        return f"{total} value(s) anonymized."


def _is_sensitive(key: str) -> bool:
    return bool(_SENSITIVE_PATTERNS.search(key))


def anonymize(
    env: Dict[str, str],
    placeholder: str = _ANON_PLACEHOLDER,
    keys: List[str] = None,
) -> AnonymizeResult:
    entries: List[AnonymizeEntry] = []
    for key, value in env.items():
        if keys is not None:
            should_anon = key in keys
        else:
            should_anon = _is_sensitive(key)
        anonymized = placeholder if should_anon else value
        entries.append(AnonymizeEntry(key=key, original=value, anonymized=anonymized))
    return AnonymizeResult(entries=entries)
