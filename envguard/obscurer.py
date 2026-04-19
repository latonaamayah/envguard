from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_PATTERNS = ("password", "secret", "token", "api_key", "apikey", "private", "auth")


@dataclass
class ObscureEntry:
    key: str
    original: str
    obscured: str
    was_obscured: bool

    def changed(self) -> bool:
        return self.was_obscured


@dataclass
class ObscureResult:
    entries: List[ObscureEntry] = field(default_factory=list)

    def has_obscured(self) -> bool:
        return any(e.was_obscured for e in self.entries)

    def obscured_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_obscured]

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.obscured for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        obscured = len(self.obscured_keys())
        return f"{obscured}/{total} keys obscured"


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in _SENSITIVE_PATTERNS)


def _obscure_value(value: str, style: str = "stars") -> str:
    if not value:
        return value
    if style == "stars":
        return "*" * len(value)
    if style == "partial":
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    if style == "hash":
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()[:8]
    return "*" * len(value)


def obscure(env: Dict[str, str], style: str = "stars", keys: List[str] = None) -> ObscureResult:
    result = ObscureResult()
    for key, value in env.items():
        sensitive = (keys and key in keys) or (not keys and _is_sensitive(key))
        if sensitive:
            obscured = _obscure_value(value, style)
            result.entries.append(ObscureEntry(key=key, original=value, obscured=obscured, was_obscured=True))
        else:
            result.entries.append(ObscureEntry(key=key, original=value, obscured=value, was_obscured=False))
    return result
