from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ArchiveEntry:
    label: str
    timestamp: str
    variables: Dict[str, str]

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveEntry":
        return cls(
            label=data["label"],
            timestamp=data["timestamp"],
            variables=data["variables"],
        )


@dataclass
class ArchiveResult:
    entries: List[ArchiveEntry] = field(default_factory=list)

    def has_entries(self) -> bool:
        return len(self.entries) > 0

    def labels(self) -> List[str]:
        return [e.label for e in self.entries]

    def get(self, label: str) -> Optional[ArchiveEntry]:
        for e in self.entries:
            if e.label == label:
                return e
        return None

    def summary(self) -> str:
        return f"{len(self.entries)} archive(s) stored"


def archive(env: Dict[str, str], label: str) -> ArchiveEntry:
    return ArchiveEntry(
        label=label,
        timestamp=datetime.utcnow().isoformat(),
        variables=dict(env),
    )


def save_archive(result: ArchiveResult, path: Path) -> None:
    data = [e.to_dict() for e in result.entries]
    path.write_text(json.dumps(data, indent=2))


def load_archive(path: Path) -> ArchiveResult:
    if not path.exists():
        return ArchiveResult()
    data = json.loads(path.read_text())
    return ArchiveResult(entries=[ArchiveEntry.from_dict(d) for d in data])
