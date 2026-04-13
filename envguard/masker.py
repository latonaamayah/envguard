"""Masking sensitive environment variable values for safe output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

# Common patterns that suggest a value is sensitive
_SENSITIVE_KEYWORDS: Set[str] = {
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "auth", "credential", "private", "key", "cert", "pwd",
}

DEFAULT_MASK = "***"


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def has_masked(self) -> bool:
        return len(self.masked_keys) > 0

    def summary(self) -> str:
        if not self.has_masked:
            return "No values were masked."
        keys = ", ".join(self.masked_keys)
        return f"Masked {len(self.masked_keys)} sensitive key(s): {keys}"


def _is_sensitive(key: str) -> bool:
    """Return True if the key name suggests a sensitive value."""
    lower = key.lower()
    return any(kw in lower for kw in _SENSITIVE_KEYWORDS)


def mask(
    env: Dict[str, str],
    extra_sensitive: List[str] | None = None,
    mask_char: str = DEFAULT_MASK,
    reveal_prefix: int = 0,
) -> MaskResult:
    """Mask sensitive values in an env dict.

    Args:
        env: The environment variable mapping to process.
        extra_sensitive: Additional key names to treat as sensitive.
        mask_char: Replacement string for masked values.
        reveal_prefix: Number of leading characters to keep visible.

    Returns:
        A MaskResult with original and masked dicts.
    """
    sensitive_keys: Set[str] = set(extra_sensitive or [])
    result: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key) or key in sensitive_keys:
            if reveal_prefix > 0 and len(value) > reveal_prefix:
                masked_value = value[:reveal_prefix] + mask_char
            else:
                masked_value = mask_char
            result[key] = masked_value
            masked_keys.append(key)
        else:
            result[key] = value

    return MaskResult(original=dict(env), masked=result, masked_keys=sorted(masked_keys))
