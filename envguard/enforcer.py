"""enforcer.py — Enforce a set of rules on an env dict, blocking or warning on violations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class EnforceEntry:
    key: str
    value: str
    rule: str
    passed: bool
    message: Optional[str] = None

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        detail = f": {self.message}" if self.message else ""
        return f"[{status}] {self.key} ({self.rule}){detail}"


@dataclass
class EnforceResult:
    entries: List[EnforceEntry] = field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        return any(not e.passed for e in self.entries)

    @property
    def failed_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.passed]

    @property
    def passed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.passed]

    def summary(self) -> str:
        total = len(self.entries)
        failed = len(self.failed_keys)
        passed = total - failed
        return f"{passed}/{total} checks passed, {failed} failed"


# Built-in rule callables: (key, value) -> Optional[str]  (None = pass, str = failure message)
RuleFunc = Callable[[str, str], Optional[str]]

_BUILTIN_RULES: Dict[str, RuleFunc] = {
    "not_empty": lambda k, v: None if v.strip() else f"{k} must not be empty",
    "no_spaces": lambda k, v: None if " " not in v else f"{k} must not contain spaces",
    "uppercase_key": lambda k, v: None if k == k.upper() else f"{k} key must be uppercase",
    "min_length_8": lambda k, v: None if len(v) >= 8 else f"{k} value must be at least 8 characters",
    "no_quotes": lambda k, v: None if not (v.startswith('"') or v.startswith("'")) else f"{k} must not be quoted",
}


def enforce(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    custom_rules: Optional[Dict[str, RuleFunc]] = None,
) -> EnforceResult:
    """Apply named rules to specific keys in env.

    Args:
        env: mapping of key -> value
        rules: mapping of key -> list of rule names to apply
        custom_rules: optional extra rule functions keyed by name
    """
    all_rules = {**_BUILTIN_RULES, **(custom_rules or {})}
    result = EnforceResult()

    for key, rule_names in rules.items():
        value = env.get(key, "")
        for rule_name in rule_names:
            rule_fn = all_rules.get(rule_name)
            if rule_fn is None:
                result.entries.append(
                    EnforceEntry(key=key, value=value, rule=rule_name, passed=False,
                                 message=f"Unknown rule '{rule_name}'")
                )
                continue
            msg = rule_fn(key, value)
            result.entries.append(
                EnforceEntry(key=key, value=value, rule=rule_name, passed=(msg is None), message=msg)
            )

    return result
