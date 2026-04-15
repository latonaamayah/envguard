"""Pin current env variable values as a locked reference snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import hashlib


@dataclass
class PinEntry:
    key: str
    value: str
    checksum: str

    @staticmethod
    def compute_checksum(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()[:16]


@dataclass
class PinResult:
    pinned: Dict[str, PinEntry] = field(default_factory=dict)
    changed: List[str] = field(default_factory=list)
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    def has_drift(self) -> bool:
        return bool(self.changed or self.new_keys or self.removed_keys)

    def summary(self) -> str:
        parts = []
        if self.new_keys:
            parts.append(f"{len(self.new_keys)} new")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed")
        if not parts:
            return "No drift detected."
        return "Drift detected: " + ", ".join(parts) + "."


def pin(env: Dict[str, str], existing: Optional[Dict[str, str]] = None) -> PinResult:
    """Pin env values and compare against an existing pin if provided."""
    result = PinResult()
    existing = existing or {}

    for key, value in env.items():
        checksum = PinEntry.compute_checksum(value)
        result.pinned[key] = PinEntry(key=key, value=value, checksum=checksum)
        if key not in existing:
            result.new_keys.append(key)
        elif existing[key] != checksum:
            result.changed.append(key)

    for key in existing:
        if key not in env:
            result.removed_keys.append(key)

    return result


def save_pin(result: PinResult, path: str) -> None:
    data = {k: v.checksum for k, v in result.pinned.items()}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_pin(path: str) -> Dict[str, str]:
    with open(path) as f:
        return json.load(f)
