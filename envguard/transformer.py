"""Transform env variable values using built-in or custom rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformEntry:
    key: str
    original: str
    transformed: str
    rule: str

    @property
    def changed(self) -> bool:
        return self.original != self.transformed


@dataclass
class TransformResult:
    entries: List[TransformEntry] = field(default_factory=list)
    vars: Dict[str, str] = field(default_factory=dict)

    def has_changes(self) -> bool:
        return any(e.changed for e in self.entries)

    def summary(self) -> str:
        changed = [e for e in self.entries if e.changed]
        if not changed:
            return "No transformations applied."
        lines = [f"{e.key}: '{e.original}' -> '{e.transformed}' (rule: {e.rule})" for e in changed]
        return "\n".join(lines)


_BUILTIN_RULES: Dict[str, Callable[[str], str]] = {
    "uppercase": str.upper,
    "lowercase": str.lower,
    "strip": str.strip,
    "strip_quotes": lambda v: v.strip('"').strip("'"),
}


def transform(
    env: Dict[str, str],
    rules: Dict[str, str],
    custom_rules: Optional[Dict[str, Callable[[str], str]]] = None,
) -> TransformResult:
    """Apply named transformation rules to env keys.

    Args:
        env: The source env dict.
        rules: Mapping of key -> rule name.
        custom_rules: Optional additional rule callables keyed by name.

    Returns:
        TransformResult with per-key entries and the final transformed vars.
    """
    all_rules = {**_BUILTIN_RULES, **(custom_rules or {})}
    result_vars = dict(env)
    entries: List[TransformEntry] = []

    for key, rule_name in rules.items():
        original = env.get(key, "")
        if rule_name not in all_rules:
            raise ValueError(f"Unknown transform rule: '{rule_name}'")
        transformed = all_rules[rule_name](original)
        result_vars[key] = transformed
        entries.append(TransformEntry(key=key, original=original, transformed=transformed, rule=rule_name))

    return TransformResult(entries=entries, vars=result_vars)
