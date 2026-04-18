from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CastEntry:
    key: str
    raw: str
    cast: object
    target_type: str
    error: Optional[str] = None

    @property
    def changed(self) -> bool:
        return self.error is None and str(self.cast) != self.raw


@dataclass
class CastResult:
    entries: List[CastEntry] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(e.error for e in self.entries)

    @property
    def failed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.error]

    @property
    def as_dict(self) -> Dict[str, object]:
        return {e.key: e.cast for e in self.entries if not e.error}

    def summary(self) -> str:
        total = len(self.entries)
        failed = len(self.failed_keys)
        return f"{total} keys processed, {failed} cast error(s)."


_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def _cast_value(raw: str, target_type: str):
    if target_type == "int":
        return int(raw)
    if target_type == "float":
        return float(raw)
    if target_type == "bool":
        low = raw.lower()
        if low in _BOOL_TRUE:
            return True
        if low in _BOOL_FALSE:
            return False
        raise ValueError(f"Cannot cast {raw!r} to bool")
    if target_type == "str":
        return raw
    raise ValueError(f"Unknown type: {target_type}")


def cast(env: Dict[str, str], type_map: Dict[str, str]) -> CastResult:
    result = CastResult()
    for key, raw in env.items():
        target = type_map.get(key, "str")
        try:
            value = _cast_value(raw, target)
            result.entries.append(CastEntry(key=key, raw=raw, cast=value, target_type=target))
        except (ValueError, TypeError) as exc:
            result.entries.append(CastEntry(key=key, raw=raw, cast=raw, target_type=target, error=str(exc)))
    return result
