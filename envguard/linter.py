"""Linter for .env files: checks style and best-practice issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.schema import Schema


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str  # "warning" | "error"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        if not self.has_issues:
            return "No lint issues found."
        return (
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s) found."
        )


_SENSITIVE_HINTS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASS")


def _is_sensitive_key(key: str) -> bool:
    """Return True if *key* looks like it holds a sensitive value."""
    return any(hint in key.upper() for hint in _SENSITIVE_HINTS)


def lint(env: Dict[str, str], schema: Schema) -> LintResult:
    """Run lint checks on *env* values against *schema* definitions.

    Checks performed:
    - Required variables that are present but empty are reported as errors.
    - Sensitive-looking variables (e.g. containing TOKEN, SECRET) without a
      schema description are reported as warnings.
    - Values longer than 512 characters are flagged as a possible
      misconfiguration.
    - Values with leading or trailing whitespace are flagged as warnings.
    """
    result = LintResult()

    for key, var in schema.variables.items():
        value = env.get(key)

        # Check for keys present in env but with empty values when required
        if var.required and key in env and value == "":
            result.issues.append(
                LintIssue(key, "Required variable is set but empty.", "error")
            )

        # Warn about sensitive-looking keys that have no description
        if _is_sensitive_key(key) and not var.description:
            result.issues.append(
                LintIssue(
                    key,
                    "Sensitive variable has no description in schema.",
                    "warning",
                )
            )

        # Warn about very long values that may indicate a misconfiguration
        if value and len(value) > 512:
            result.issues.append(
                LintIssue(key, "Value exceeds 512 characters; verify it is correct.", "warning")
            )

    # Warn about keys in env that look like they contain whitespace in value
    for key, value in env.items():
        if value != value.strip():
            result.issues.append(
                LintIssue(key, "Value has leading or trailing whitespace.", "warning")
            )

    return result
