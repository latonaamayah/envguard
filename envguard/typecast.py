"""Typecast module: attempts to cast .env string values to their declared schema types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from envguard.schema import Schema


@dataclass
class CastEntry:
    key: str
    raw: str
    casted: Any
    target_type: str


@dataclass
class CastResult:
    entries: List[CastEntry] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return bool(self.errors)

    def as_dict(self) -> Dict[str, Any]:
        return {e.key: e.casted for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        errs = len(self.errors)
        return f"{total} variable(s) processed, {errs} cast error(s)."


def _cast_value(raw: str, target_type: str) -> Any:
    """Cast a raw string to the given type name. Raises ValueError on failure."""
    t = target_type.lower()
    if t == "integer":
        return int(raw)
    if t == "float":
        return float(raw)
    if t == "boolean":
        if raw.lower() in ("true", "1", "yes"):
            return True
        if raw.lower() in ("false", "0", "no"):
            return False
        raise ValueError(f"Cannot cast {raw!r} to boolean")
    # default: string
    return raw


def typecast(env: Dict[str, str], schema: Schema) -> CastResult:
    """Cast each env variable to its declared schema type."""
    result = CastResult()
    for key, var_schema in schema.variables.items():
        if key not in env:
            continue
        raw = env[key]
        target = var_schema.type or "string"
        try:
            casted = _cast_value(raw, target)
            result.entries.append(CastEntry(key=key, raw=raw, casted=casted, target_type=target))
        except (ValueError, TypeError) as exc:
            result.errors.append(f"{key}: cannot cast {raw!r} to {target} — {exc}")
    return result
