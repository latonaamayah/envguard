"""Snapshot module: save and compare .env state over time."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class Snapshot:
    """A point-in-time record of an .env file's keys and values."""

    timestamp: str
    source: str
    variables: Dict[str, str]

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            timestamp=data["timestamp"],
            source=data["source"],
            variables=data["variables"],
        )


@dataclass
class SnapshotDiff:
    """Differences between two snapshots."""

    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts: List[str] = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        return ", ".join(parts) if parts else "no changes"


def take_snapshot(env: Dict[str, str], source: str) -> Snapshot:
    """Create a new snapshot from an env dict."""
    ts = datetime.now(timezone.utc).isoformat()
    return Snapshot(timestamp=ts, source=source, variables=dict(env))


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Snapshot file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Compare two snapshots and return a SnapshotDiff."""
    result = SnapshotDiff()
    old_vars = old.variables
    new_vars = new.variables

    for key, value in new_vars.items():
        if key not in old_vars:
            result.added[key] = value
        elif old_vars[key] != value:
            result.changed[key] = (old_vars[key], value)

    for key, value in old_vars.items():
        if key not in new_vars:
            result.removed[key] = value

    return result
