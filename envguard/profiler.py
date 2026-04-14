"""Profile .env files to produce statistics and insights."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.masker import _is_sensitive


@dataclass
class ProfileResult:
    total: int = 0
    empty_count: int = 0
    sensitive_count: int = 0
    long_value_count: int = 0  # values > 64 chars
    numeric_count: int = 0
    boolean_count: int = 0
    key_lengths: List[int] = field(default_factory=list)
    value_lengths: List[int] = field(default_factory=list)

    # -----------------------------------------------------------------
    @property
    def avg_key_length(self) -> float:
        return sum(self.key_lengths) / len(self.key_lengths) if self.key_lengths else 0.0

    @property
    def avg_value_length(self) -> float:
        return sum(self.value_lengths) / len(self.value_lengths) if self.value_lengths else 0.0

    def summary(self) -> str:
        return (
            f"Total variables : {self.total}\n"
            f"Empty values    : {self.empty_count}\n"
            f"Sensitive keys  : {self.sensitive_count}\n"
            f"Long values     : {self.long_value_count}\n"
            f"Numeric values  : {self.numeric_count}\n"
            f"Boolean values  : {self.boolean_count}\n"
            f"Avg key length  : {self.avg_key_length:.1f}\n"
            f"Avg value length: {self.avg_value_length:.1f}"
        )


_BOOL_VALUES = {"true", "false", "1", "0", "yes", "no", "on", "off"}


def profile(env: Dict[str, str]) -> ProfileResult:
    """Analyse *env* dict and return a :class:`ProfileResult`."""
    result = ProfileResult(total=len(env))

    for key, value in env.items():
        result.key_lengths.append(len(key))
        result.value_lengths.append(len(value))

        if value == "":
            result.empty_count += 1

        if _is_sensitive(key):
            result.sensitive_count += 1

        if len(value) > 64:
            result.long_value_count += 1

        if value.lstrip("-").replace(".", "", 1).isdigit():
            result.numeric_count += 1

        if value.lower() in _BOOL_VALUES:
            result.boolean_count += 1

    return result
