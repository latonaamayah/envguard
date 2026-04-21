"""Reusable validation rule functions for envguard."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class RuleViolation:
    key: str
    rule: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key} ({self.rule}): {self.message}"


@dataclass
class RuleResult:
    violations: List[RuleViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return bool(self.violations)

    @property
    def errors(self) -> List[RuleViolation]:
        return [v for v in self.violations if v.severity == "error"]

    @property
    def warnings(self) -> List[RuleViolation]:
        return [v for v in self.violations if v.severity == "warning"]

    def summary(self) -> str:
        e, w = len(self.errors), len(self.warnings)
        return f"{e} error(s), {w} warning(s)"


RuleFunc = Callable[[str, str], Optional[str]]


def rule_not_empty(key: str, value: str) -> Optional[str]:
    """Value must not be empty."""
    if not value.strip():
        return "Value must not be empty"
    return None


def rule_no_whitespace(key: str, value: str) -> Optional[str]:
    """Value must not contain surrounding whitespace."""
    if value != value.strip():
        return "Value has leading or trailing whitespace"
    return None


def rule_alphanumeric(key: str, value: str) -> Optional[str]:
    """Value must be alphanumeric (underscores allowed)."""
    if not re.fullmatch(r"[\w]+", value):
        return "Value must be alphanumeric (underscores allowed)"
    return None


def rule_numeric(key: str, value: str) -> Optional[str]:
    """Value must be a valid number."""
    try:
        float(value)
        return None
    except ValueError:
        return "Value must be numeric"


def rule_url(key: str, value: str) -> Optional[str]:
    """Value must look like a URL."""
    pattern = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
    if not pattern.match(value):
        return "Value must be a valid URL (http/https)"
    return None


BUILT_IN_RULES: Dict[str, RuleFunc] = {
    "not_empty": rule_not_empty,
    "no_whitespace": rule_no_whitespace,
    "alphanumeric": rule_alphanumeric,
    "numeric": rule_numeric,
    "url": rule_url,
}


def apply_rules(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    severity: str = "error",
) -> RuleResult:
    """Apply named rules to specific keys.

    Args:
        env: mapping of key -> value
        rules: mapping of rule_name -> list of keys to apply it to
        severity: default severity for violations
    """
    result = RuleResult()
    for rule_name, keys in rules.items():
        fn = BUILT_IN_RULES.get(rule_name)
        if fn is None:
            continue
        for key in keys:
            value = env.get(key, "")
            msg = fn(key, value)
            if msg:
                result.violations.append(
                    RuleViolation(key=key, rule=rule_name, message=msg, severity=severity)
                )
    return result
