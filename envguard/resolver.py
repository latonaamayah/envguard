"""Resolver module for envguard.

Resolves final environment variable values by merging multiple sources
(e.g., .env file, OS environment, defaults from schema) with a defined
precedence order: OS env > .env file > schema defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ResolveEntry:
    """Represents a single resolved environment variable."""

    key: str
    value: Optional[str]
    source: str  # 'os', 'file', 'default', or 'missing'

    def is_missing(self) -> bool:
        return self.source == "missing"


@dataclass
class ResolveResult:
    """Result of resolving environment variables from multiple sources."""

    entries: List[ResolveEntry] = field(default_factory=list)

    def has_missing(self) -> bool:
        """Return True if any variable could not be resolved."""
        return any(e.is_missing() for e in self.entries)

    def missing_keys(self) -> List[str]:
        """Return keys that could not be resolved from any source."""
        return [e.key for e in self.entries if e.is_missing()]

    def as_dict(self) -> Dict[str, Optional[str]]:
        """Return resolved values as a plain dictionary."""
        return {e.key: e.value for e in self.entries}

    def by_source(self, source: str) -> List[ResolveEntry]:
        """Return entries resolved from a specific source."""
        return [e for e in self.entries if e.source == source]

    def summary(self) -> str:
        total = len(self.entries)
        from_os = len(self.by_source("os"))
        from_file = len(self.by_source("file"))
        from_default = len(self.by_source("default"))
        missing = len(self.missing_keys())
        return (
            f"{total} variable(s) resolved: "
            f"{from_os} from OS, {from_file} from file, "
            f"{from_default} from defaults, {missing} missing."
        )


def resolve(
    keys: List[str],
    file_env: Dict[str, str],
    os_env: Optional[Dict[str, str]] = None,
    defaults: Optional[Dict[str, Optional[str]]] = None,
) -> ResolveResult:
    """Resolve environment variables from multiple sources.

    Precedence (highest to lowest):
      1. OS environment variables
      2. .env file values
      3. Schema defaults
      4. Missing (unresolved)

    Args:
        keys: The list of variable names to resolve.
        file_env: Variables loaded from a .env file.
        os_env: OS-level environment variables (defaults to empty dict).
        defaults: Default values from the schema (defaults to empty dict).

    Returns:
        A ResolveResult containing one entry per key.
    """
    if os_env is None:
        os_env = {}
    if defaults is None:
        defaults = {}

    result = ResolveResult()

    for key in keys:
        if key in os_env:
            entry = ResolveEntry(key=key, value=os_env[key], source="os")
        elif key in file_env:
            entry = ResolveEntry(key=key, value=file_env[key], source="file")
        elif key in defaults and defaults[key] is not None:
            entry = ResolveEntry(key=key, value=defaults[key], source="default")
        else:
            entry = ResolveEntry(key=key, value=None, source="missing")

        result.entries.append(entry)

    return result
