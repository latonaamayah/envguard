from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TraceEntry:
    key: str
    value: str
    source: str
    overridden_by: Optional[str] = None
    final_value: Optional[str] = None

    @property
    def was_overridden(self) -> bool:
        return self.overridden_by is not None

    def message(self) -> str:
        if self.was_overridden:
            return f"{self.key}: '{self.value}' (from {self.source}) overridden by '{self.final_value}' (from {self.overridden_by})"
        return f"{self.key}: '{self.value}' (from {self.source})"


@dataclass
class TraceResult:
    entries: List[TraceEntry] = field(default_factory=list)

    @property
    def has_overrides(self) -> bool:
        return any(e.was_overridden for e in self.entries)

    @property
    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_overridden]

    def summary(self) -> str:
        total = len(self.entries)
        overridden = len(self.overridden_keys)
        return f"{total} key(s) traced, {overridden} overridden"

    def as_dict(self) -> Dict[str, str]:
        result = {}
        for e in self.entries:
            result[e.key] = e.final_value if e.final_value is not None else e.value
        return result


def trace(layers: List[Dict[str, str]], labels: Optional[List[str]] = None) -> TraceResult:
    """Trace how keys are resolved across multiple env layers (first to last wins)."""
    if labels is None:
        labels = [f"layer_{i}" for i in range(len(layers))]

    seen: Dict[str, TraceEntry] = {}
    result = TraceResult()

    for label, layer in zip(labels, layers):
        for key, value in layer.items():
            if key in seen:
                existing = seen[key]
                existing.overridden_by = label
                existing.final_value = value
            else:
                entry = TraceEntry(key=key, value=value, source=label)
                seen[key] = entry

    result.entries = list(seen.values())
    return result
