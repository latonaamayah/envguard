from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib
import json


@dataclass
class VaultEntry:
    key: str
    value: str
    masked: str
    checksum: str

    def __str__(self) -> str:
        return f"{self.key}={self.masked} [{self.checksum[:8]}]"


@dataclass
class VaultResult:
    entries: List[VaultEntry] = field(default_factory=list)
    _index: Dict[str, VaultEntry] = field(default_factory=dict, repr=False)

    def has_entries(self) -> bool:
        return bool(self.entries)

    def get(self, key: str) -> Optional[VaultEntry]:
        return self._index.get(key)

    def keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def to_json(self) -> str:
        return json.dumps(
            {e.key: {"masked": e.masked, "checksum": e.checksum} for e in self.entries},
            indent=2,
        )

    def summary(self) -> str:
        return f"{len(self.entries)} vaulted variable(s)"


def _mask(value: str, visible: int = 4) -> str:
    if len(value) <= visible:
        return "*" * len(value)
    return value[:visible] + "*" * (len(value) - visible)


def _checksum(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def vault(env: Dict[str, str], keys: Optional[List[str]] = None) -> VaultResult:
    result = VaultResult()
    targets = keys if keys is not None else list(env.keys())
    for key in targets:
        if key not in env:
            continue
        value = env[key]
        entry = VaultEntry(
            key=key,
            value=value,
            masked=_mask(value),
            checksum=_checksum(value),
        )
        result.entries.append(entry)
        result._index[key] = entry
    return result
