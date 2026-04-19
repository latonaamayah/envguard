from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import hashlib
import json


@dataclass
class SealEntry:
    key: str
    value: str
    checksum: str

    def __str__(self) -> str:
        return f"{self.key}={self.checksum}"


@dataclass
class SealResult:
    entries: List[SealEntry] = field(default_factory=list)
    tampered: List[str] = field(default_factory=list)

    def has_entries(self) -> bool:
        return bool(self.entries)

    def has_tampering(self) -> bool:
        return bool(self.tampered)

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.checksum for e in self.entries}

    def summary(self) -> str:
        if self.has_tampering():
            return f"{len(self.tampered)} tampered key(s): {', '.join(self.tampered)}"
        return f"{len(self.entries)} key(s) sealed, no tampering detected."


def _checksum(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def seal(env: Dict[str, str]) -> SealResult:
    entries = [SealEntry(key=k, value=v, checksum=_checksum(v)) for k, v in env.items()]
    return SealResult(entries=entries)


def verify(env: Dict[str, str], seal_data: Dict[str, str]) -> SealResult:
    entries = []
    tampered = []
    for key, value in env.items():
        current = _checksum(value)
        expected = seal_data.get(key)
        entry = SealEntry(key=key, value=value, checksum=current)
        entries.append(entry)
        if expected is not None and current != expected:
            tampered.append(key)
    return SealResult(entries=entries, tampered=tampered)


def save_seal(result: SealResult, path: str) -> None:
    with open(path, "w") as f:
        json.dump(result.as_dict(), f, indent=2)


def load_seal(path: str) -> Dict[str, str]:
    with open(path) as f:
        return json.load(f)
