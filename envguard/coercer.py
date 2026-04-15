"""Coercer: force-convert env var values to target types with a result report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CoerceEntry:
    key: str
    original: str
    coerced: Any
    target_type: str
    success: bool
    error: str = ""

    @property
    def changed(self) -> bool:
        return self.success and str(self.coerced) != self.original


@dataclass
class CoerceResult:
    entries: List[CoerceEntry] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(not e.success for e in self.entries)

    @property
    def failed_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.success]

    def as_dict(self) -> Dict[str, Any]:
        return {e.key: e.coerced for e in self.entries if e.success}

    def summary(self) -> str:
        ok = sum(1 for e in self.entries if e.success)
        fail = len(self.entries) - ok
        return f"{ok} coerced successfully, {fail} failed"


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _coerce(value: str, target: str):
    if target == "int":
        return int(value)
    if target == "float":
        return float(value)
    if target == "bool":
        low = value.strip().lower()
        if low in _TRUE_VALUES:
            return True
        if low in _FALSE_VALUES:
            return False
        raise ValueError(f"Cannot coerce {value!r} to bool")
    if target == "str":
        return value
    raise ValueError(f"Unknown target type: {target!r}")


def coerce(env: Dict[str, str], rules: Dict[str, str]) -> CoerceResult:
    """Coerce env values according to rules mapping key -> target_type."""
    result = CoerceResult()
    for key, target in rules.items():
        raw = env.get(key, "")
        try:
            coerced = _coerce(raw, target)
            result.entries.append(CoerceEntry(key, raw, coerced, target, True))
        except (ValueError, KeyError) as exc:
            result.entries.append(CoerceEntry(key, raw, None, target, False, str(exc)))
    return result
