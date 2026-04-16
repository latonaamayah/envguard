from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ScoreEntry:
    key: str
    points: int
    reason: str


@dataclass
class ScoreResult:
    entries: List[ScoreEntry] = field(default_factory=list)
    total: int = 0
    max_total: int = 0

    @property
    def has_entries(self) -> bool:
        return len(self.entries) > 0

    @property
    def percent(self) -> float:
        if self.max_total == 0:
            return 0.0
        return round(self.total / self.max_total * 100, 2)

    @property
    def grade(self) -> str:
        p = self.percent
        if p >= 90:
            return "A"
        if p >= 75:
            return "B"
        if p >= 60:
            return "C"
        if p >= 40:
            return "D"
        return "F"

    def summary(self) -> str:
        return (
            f"Score: {self.total}/{self.max_total} ({self.percent}%) "
            f"Grade: {self.grade}"
        )


def score(env: Dict[str, str]) -> ScoreResult:
    entries: List[ScoreEntry] = []
    total = 0
    max_total = 0
    points_per_key = 10

    for key, value in env.items():
        max_total += points_per_key
        pts = 0
        reason_parts = []

        if value and value.strip():
            pts += 5
            reason_parts.append("non-empty")
        else:
            reason_parts.append("empty value")

        if len(key) >= 3:
            pts += 2
            reason_parts.append("key length ok")

        if key == key.upper():
            pts += 3
            reason_parts.append("uppercase key")
        else:
            reason_parts.append("key not uppercase")

        total += pts
        entries.append(ScoreEntry(key=key, points=pts, reason=", ".join(reason_parts)))

    return ScoreResult(entries=entries, total=total, max_total=max_total)
