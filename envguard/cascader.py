from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CascadeEntry:
    key: str
    value: str
    source: str
    layer_index: int
    was_overridden: bool = False
    previous_value: Optional[str] = None

    @property
    def message(self) -> str:
        if self.was_overridden:
            return (
                f"{self.key}: overridden in layer '{self.source}' "
                f"(was '{self.previous_value}', now '{self.value}')"
            )
        return f"{self.key}: resolved from layer '{self.source}' = '{self.value}'"


@dataclass
class CascadeResult:
    entries: List[CascadeEntry] = field(default_factory=list)
    merged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_overrides(self) -> bool:
        return any(e.was_overridden for e in self.entries)

    @property
    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_overridden]

    @property
    def layer_count(self) -> int:
        return len({e.layer_index for e in self.entries})

    def summary(self) -> str:
        total = len(self.merged)
        overrides = len(self.overridden_keys)
        return (
            f"{total} key(s) resolved across {self.layer_count} layer(s); "
            f"{overrides} override(s) applied."
        )


def cascade(
    layers: List[Dict[str, str]],
    layer_names: Optional[List[str]] = None,
) -> CascadeResult:
    """Merge multiple env dicts in order; later layers override earlier ones."""
    if layer_names is None:
        layer_names = [f"layer_{i}" for i in range(len(layers))]

    result = CascadeResult()
    resolved: Dict[str, str] = {}
    source_map: Dict[str, str] = {}
    index_map: Dict[str, int] = {}

    for idx, (layer, name) in enumerate(zip(layers, layer_names)):
        for key, value in layer.items():
            was_overridden = key in resolved
            previous = resolved.get(key)
            entry = CascadeEntry(
                key=key,
                value=value,
                source=name,
                layer_index=idx,
                was_overridden=was_overridden,
                previous_value=previous,
            )
            result.entries.append(entry)
            resolved[key] = value
            source_map[key] = name
            index_map[key] = idx

    result.merged = dict(resolved)
    return result
