"""Sanitizer: removes or replaces characters from env values based on rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class SanitizeEntry:
    key: str
    original: str
    sanitized: str

    @property
    def changed(self) -> bool:
        return self.original != self.sanitized


@dataclass
class SanitizeResult:
    entries: List[SanitizeEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def changed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    @property
    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.sanitized for e in self.entries}

    def summary(self) -> str:
        n = len(self.changed_keys)
        if n == 0:
            return "No sanitization changes."
        return f"{n} value(s) sanitized: {', '.join(self.changed_keys)}"


def _apply_rules(value: str, rules: List[str]) -> str:
    result = value
    for rule in rules:
        if rule == "strip":
            result = result.strip()
        elif rule == "strip_quotes":
            for q in ('"', "'"):
                if result.startswith(q) and result.endswith(q) and len(result) >= 2:
                    result = result[1:-1]
                    break
        elif rule == "remove_newlines":
            result = result.replace("\n", "").replace("\r", "")
        elif rule == "remove_nulls":
            result = result.replace("\x00", "")
        elif rule == "alphanumeric_only":
            result = re.sub(r"[^a-zA-Z0-9]", "", result)
        elif rule == "lowercase":
            result = result.lower()
        elif rule == "uppercase":
            result = result.upper()
    return result


def sanitize(
    env: Dict[str, str],
    rules: Optional[List[str]] = None,
    key_rules: Optional[Dict[str, List[str]]] = None,
) -> SanitizeResult:
    """Sanitize env values using global rules and optional per-key rules."""
    global_rules = rules or ["strip"]
    key_rules = key_rules or {}
    result = SanitizeResult()
    for key, value in env.items():
        effective_rules = key_rules.get(key, global_rules)
        sanitized = _apply_rules(value, effective_rules)
        result.entries.append(SanitizeEntry(key=key, original=value, sanitized=sanitized))
    return result
