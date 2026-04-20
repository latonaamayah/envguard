"""Inspector: reports a detailed breakdown of each env variable's properties."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "api_key", "apikey", "private")


@dataclass
class InspectEntry:
    key: str
    value: str
    length: int
    is_empty: bool
    is_sensitive: bool
    has_whitespace: bool
    has_quotes: bool
    is_numeric: bool
    is_boolean: bool

    def summary(self) -> str:
        flags: List[str] = []
        if self.is_empty:
            flags.append("empty")
        if self.is_sensitive:
            flags.append("sensitive")
        if self.has_whitespace:
            flags.append("has-whitespace")
        if self.has_quotes:
            flags.append("has-quotes")
        if self.is_numeric:
            flags.append("numeric")
        if self.is_boolean:
            flags.append("boolean")
        flag_str = ", ".join(flags) if flags else "clean"
        return f"{self.key} [len={self.length}] ({flag_str})"


@dataclass
class InspectResult:
    entries: List[InspectEntry] = field(default_factory=list)

    def has_entries(self) -> bool:
        return bool(self.entries)

    def sensitive_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_sensitive]

    def empty_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_empty]

    def as_dict(self) -> Dict[str, dict]:
        return {
            e.key: {
                "length": e.length,
                "is_empty": e.is_empty,
                "is_sensitive": e.is_sensitive,
                "has_whitespace": e.has_whitespace,
                "has_quotes": e.has_quotes,
                "is_numeric": e.is_numeric,
                "is_boolean": e.is_boolean,
            }
            for e in self.entries
        }


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _is_boolean(value: str) -> bool:
    return value.lower() in {"true", "false", "yes", "no", "1", "0"}


def inspect(env: Dict[str, str]) -> InspectResult:
    """Inspect each variable in *env* and return a detailed InspectResult."""
    entries: List[InspectEntry] = []
    for key, value in env.items():
        entries.append(
            InspectEntry(
                key=key,
                value=value,
                length=len(value),
                is_empty=value.strip() == "",
                is_sensitive=_is_sensitive(key),
                has_whitespace=value != value.strip(),
                has_quotes=value.startswith(("'", '"')) or value.endswith(("'", '"')),
                is_numeric=_is_numeric(value) if value else False,
                is_boolean=_is_boolean(value) if value else False,
            )
        )
    return InspectResult(entries=entries)
