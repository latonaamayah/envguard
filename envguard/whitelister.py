"""Whitelister: filters an env dict to only keys present in an allowed list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class WhitelistEntry:
    key: str
    value: str
    allowed: bool

    def __repr__(self) -> str:  # pragma: no cover
        status = "allowed" if self.allowed else "rejected"
        return f"WhitelistEntry({self.key!r}, {status})"


@dataclass
class WhitelistResult:
    entries: List[WhitelistEntry] = field(default_factory=list)

    @property
    def has_rejected(self) -> bool:
        return any(not e.allowed for e in self.entries)

    @property
    def allowed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.allowed]

    @property
    def rejected_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.allowed]

    @property
    def allowed_vars(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries if e.allowed}

    def summary(self) -> str:
        total = len(self.entries)
        allowed = len(self.allowed_keys)
        rejected = len(self.rejected_keys)
        return (
            f"{total} key(s) processed: {allowed} allowed, {rejected} rejected."
        )


def whitelist(
    env: Dict[str, str],
    allowed: List[str],
    *,
    case_sensitive: bool = True,
) -> WhitelistResult:
    """Return a WhitelistResult keeping only keys present in *allowed*.

    Parameters
    ----------
    env:
        The environment dictionary to filter.
    allowed:
        The list of permitted key names.
    case_sensitive:
        When *False* comparisons are done in lower-case.
    """
    allowed_set: Set[str] = (
        {k for k in allowed}
        if case_sensitive
        else {k.lower() for k in allowed}
    )

    entries: List[WhitelistEntry] = []
    for key, value in env.items():
        lookup = key if case_sensitive else key.lower()
        is_allowed = lookup in allowed_set
        entries.append(WhitelistEntry(key=key, value=value, allowed=is_allowed))

    return WhitelistResult(entries=entries)
