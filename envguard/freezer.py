from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FreezeEntry:
    key: str
    checksum: str
    frozen: bool = True


@dataclass
class FreezeResult:
    entries: List[FreezeEntry] = field(default_factory=list)
    loaded_from: Optional[str] = None

    def has_frozen(self) -> bool:
        return bool(self.entries)

    def drifted(self, env: Dict[str, str]) -> List[str]:
        """Return keys whose current value differs from frozen checksum."""
        drifted_keys: List[str] = []
        for entry in self.entries:
            current = env.get(entry.key)
            if current is None:
                drifted_keys.append(entry.key)
                continue
            current_checksum = _checksum(current)
            if current_checksum != entry.checksum:
                drifted_keys.append(entry.key)
        return drifted_keys

    def summary(self) -> str:
        return f"{len(self.entries)} key(s) frozen."

    def to_dict(self) -> Dict:
        return {
            "frozen": [
                {"key": e.key, "checksum": e.checksum}
                for e in self.entries
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "FreezeResult":
        entries = [
            FreezeEntry(key=item["key"], checksum=item["checksum"])
            for item in data.get("frozen", [])
        ]
        return cls(entries=entries)


def _checksum(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def freeze(env: Dict[str, str], keys: Optional[List[str]] = None) -> FreezeResult:
    """Freeze selected (or all) keys from env by storing their checksums."""
    target_keys = keys if keys is not None else list(env.keys())
    entries = [
        FreezeEntry(key=k, checksum=_checksum(env[k]))
        for k in target_keys
        if k in env
    ]
    return FreezeResult(entries=entries)


def save_freeze(result: FreezeResult, path: str) -> None:
    Path(path).write_text(json.dumps(result.to_dict(), indent=2))


def load_freeze(path: str) -> FreezeResult:
    data = json.loads(Path(path).read_text())
    result = FreezeResult.from_dict(data)
    result.loaded_from = path
    return result
