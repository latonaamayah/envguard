from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LabelEntry:
    key: str
    value: str
    labels: List[str] = field(default_factory=list)

    def has_label(self, label: str) -> bool:
        return label in self.labels


@dataclass
class LabelResult:
    entries: List[LabelEntry] = field(default_factory=list)
    _label_index: Dict[str, List[str]] = field(default_factory=dict, repr=False)

    def has_labels(self) -> bool:
        return any(e.labels for e in self.entries)

    def keys_for_label(self, label: str) -> List[str]:
        return [e.key for e in self.entries if label in e.labels]

    def all_labels(self) -> List[str]:
        seen = set()
        result = []
        for e in self.entries:
            for lbl in e.labels:
                if lbl not in seen:
                    seen.add(lbl)
                    result.append(lbl)
        return result

    def summary(self) -> str:
        total = sum(len(e.labels) for e in self.entries)
        unique = len(self.all_labels())
        return f"{total} label(s) applied across {unique} unique label(s)"


def label(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
) -> LabelResult:
    """
    Apply labels to env keys based on rules.

    rules: mapping of label -> list of key patterns (exact match or prefix with *)
    e.g. {"sensitive": ["PASSWORD", "SECRET_*"], "infra": ["DB_*"]}
    """
    import fnmatch

    key_labels: Dict[str, List[str]] = {k: [] for k in env}

    for lbl, patterns in rules.items():
        for pattern in patterns:
            for key in env:
                if fnmatch.fnmatch(key, pattern) and lbl not in key_labels[key]:
                    key_labels[key].append(lbl)

    entries = [
        LabelEntry(key=k, value=env[k], labels=key_labels[k])
        for k in env
    ]
    return LabelResult(entries=entries)
