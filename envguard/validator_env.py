"""Validates raw env dict values against simple runtime rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvViolation:
    key: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.key}: {self.message}"


@dataclass
class EnvValidationResult:
    violations: List[EnvViolation] = field(default_factory=list)

    def has_violations(self) -> bool:
        return bool(self.violations)

    def violation_keys(self) -> List[str]:
        return [v.key for v in self.violations]

    def errors(self) -> List[EnvViolation]:
        return [v for v in self.violations if v.rule != "warning"]

    def summary(self) -> str:
        if not self.violations:
            return "All variables passed env validation."
        lines = [str(v) for v in self.violations]
        return "\n".join(lines)


def _check_not_empty(key: str, value: str) -> Optional[EnvViolation]:
    if value.strip() == "":
        return EnvViolation(key=key, rule="not_empty", message="Value must not be empty or whitespace.")
    return None


def _check_no_newlines(key: str, value: str) -> Optional[EnvViolation]:
    if "\n" in value or "\r" in value:
        return EnvViolation(key=key, rule="no_newlines", message="Value must not contain newline characters.")
    return None


def _check_max_length(key: str, value: str, max_len: int = 512) -> Optional[EnvViolation]:
    if len(value) > max_len:
        return EnvViolation(key=key, rule="max_length", message=f"Value exceeds maximum length of {max_len}.")
    return None


def _check_no_null_bytes(key: str, value: str) -> Optional[EnvViolation]:
    if "\x00" in value:
        return EnvViolation(key=key, rule="no_null_bytes", message="Value must not contain null bytes.")
    return None


DEFAULT_RULES = [_check_not_empty, _check_no_newlines, _check_max_length, _check_no_null_bytes]


def validate_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    max_length: int = 512,
) -> EnvValidationResult:
    result = EnvValidationResult()
    target_keys = keys if keys is not None else list(env.keys())
    for key in target_keys:
        value = env.get(key, "")
        for rule_fn in [_check_not_empty, _check_no_newlines, _check_no_null_bytes]:
            violation = rule_fn(key, value)
            if violation:
                result.violations.append(violation)
        length_violation = _check_max_length(key, value, max_length)
        if length_violation:
            result.violations.append(length_violation)
    return result
