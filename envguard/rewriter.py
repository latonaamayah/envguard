"""Rewriter: apply key-value updates to a .env file while preserving formatting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RewriteEntry:
    key: str
    old_value: Optional[str]
    new_value: str
    line_number: int

    @property
    def changed(self) -> bool:
        return self.old_value != self.new_value


@dataclass
class RewriteResult:
    entries: List[RewriteEntry] = field(default_factory=list)
    lines: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def changed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    def summary(self) -> str:
        n = len(self.changed_keys)
        if n == 0:
            return "No keys rewritten."
        keys = ", ".join(self.changed_keys)
        return f"{n} key(s) rewritten: {keys}"

    def as_dotenv(self) -> str:
        return "\n".join(self.lines)


def rewrite(raw_lines: List[str], updates: Dict[str, str]) -> RewriteResult:
    """Rewrite *updates* into *raw_lines*, preserving comments and blank lines."""
    result = RewriteResult()
    applied: Dict[str, bool] = {k: False for k in updates}
    out_lines: List[str] = []

    for lineno, raw in enumerate(raw_lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(raw.rstrip("\n"))
            continue

        if "=" not in stripped:
            out_lines.append(raw.rstrip("\n"))
            continue

        key, _, old_val = stripped.partition("=")
        key = key.strip()
        old_val = old_val.strip()

        if key in updates:
            new_val = updates[key]
            out_lines.append(f"{key}={new_val}")
            result.entries.append(RewriteEntry(key, old_val, new_val, lineno))
            applied[key] = True
        else:
            out_lines.append(raw.rstrip("\n"))

    # Append keys that were not found in the original file
    for key, was_applied in applied.items():
        if not was_applied:
            new_val = updates[key]
            out_lines.append(f"{key}={new_val}")
            result.entries.append(RewriteEntry(key, None, new_val, len(out_lines)))

    result.lines = out_lines
    return result
