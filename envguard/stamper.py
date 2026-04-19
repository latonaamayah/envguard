from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional
import hashlib
import json


@dataclass
class StampEntry:
    key: str
    value: str
    stamped_at: str
    fingerprint: str

    def __str__(self) -> str:
        return f"{self.key} [{self.fingerprint}] @ {self.stamped_at}"


@dataclass
class StampResult:
    entries: Dict[str, StampEntry] = field(default_factory=dict)
    label: str = ""

    def has_entries(self) -> bool:
        return bool(self.entries)

    def get(self, key: str) -> Optional[StampEntry]:
        return self.entries.get(key)

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "entries": {
                k: {
                    "value": e.value,
                    "stamped_at": e.stamped_at,
                    "fingerprint": e.fingerprint,
                }
                for k, e in self.entries.items()
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2)

    def summary(self) -> str:
        count = len(self.entries)
        label_part = f" [{self.label}]" if self.label else ""
        return f"{count} key(s) stamped{label_part}."


def _fingerprint(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()[:16]


def stamp(
    env: Dict[str, str],
    keys: Optional[list] = None,
    label: str = "",
) -> StampResult:
    result = StampResult(label=label)
    now = datetime.now(timezone.utc).isoformat()
    targets = keys if keys is not None else list(env.keys())
    for key in targets:
        if key not in env:
            continue
        value = env[key]
        result.entries[key] = StampEntry(
            key=key,
            value=value,
            stamped_at=now,
            fingerprint=_fingerprint(value),
        )
    return result
