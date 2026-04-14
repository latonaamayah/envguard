"""Compare two .env files and report structural and value differences."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CompareEntry:
    key: str
    left_value: str | None
    right_value: str | None
    status: str  # 'equal' | 'changed' | 'left_only' | 'right_only'


@dataclass
class CompareResult:
    left_file: str
    right_file: str
    entries: List[CompareEntry] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return any(e.status != "equal" for e in self.entries)

    @property
    def changed(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "changed"]

    @property
    def left_only(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "left_only"]

    @property
    def right_only(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "right_only"]

    def summary(self) -> str:
        return (
            f"{len(self.changed)} changed, "
            f"{len(self.left_only)} left-only, "
            f"{len(self.right_only)} right-only"
        )


def compare(
    left: Dict[str, str],
    right: Dict[str, str],
    left_file: str = "left",
    right_file: str = "right",
) -> CompareResult:
    """Compare two env variable dictionaries and return a CompareResult."""
    result = CompareResult(left_file=left_file, right_file=right_file)
    all_keys = sorted(set(left) | set(right))

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        if in_left and in_right:
            status = "equal" if left[key] == right[key] else "changed"
            result.entries.append(
                CompareEntry(
                    key=key,
                    left_value=left[key],
                    right_value=right[key],
                    status=status,
                )
            )
        elif in_left:
            result.entries.append(
                CompareEntry(key=key, left_value=left[key], right_value=None, status="left_only")
            )
        else:
            result.entries.append(
                CompareEntry(key=key, left_value=None, right_value=right[key], status="right_only")
            )

    return result
