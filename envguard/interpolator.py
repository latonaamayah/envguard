"""Variable interpolation for .env files.

Supports ${VAR} and $VAR syntax to expand references between variables.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationWarning:
    variable: str
    reference: str
    message: str


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    warnings: List[InterpolationWarning] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


def _resolve_value(
    key: str,
    value: str,
    env: Dict[str, str],
    seen: Optional[set] = None,
    warnings: Optional[List[InterpolationWarning]] = None,
) -> str:
    """Recursively resolve variable references in *value*."""
    if seen is None:
        seen = set()
    if warnings is None:
        warnings = []

    def replacer(match: re.Match) -> str:  # type: ignore[type-arg]
        ref = match.group(1) or match.group(2)
        if ref == key or ref in seen:
            warnings.append(
                InterpolationWarning(
                    variable=key,
                    reference=ref,
                    message=f"Circular reference detected: '{key}' -> '{ref}'",
                )
            )
            return match.group(0)
        if ref not in env:
            warnings.append(
                InterpolationWarning(
                    variable=key,
                    reference=ref,
                    message=f"Undefined reference '${ref}' in variable '{key}'",
                )
            )
            return ""
        return _resolve_value(ref, env[ref], env, seen | {key}, warnings)

    return _PATTERN.sub(replacer, value)


def interpolate(env: Dict[str, str]) -> InterpolationResult:
    """Expand all variable references in *env* and return an InterpolationResult."""
    result = InterpolationResult()
    for key, value in env.items():
        resolved = _resolve_value(key, value, env, warnings=result.warnings)
        result.resolved[key] = resolved
    return result
