"""Auditor module: checks .env files for unused or undeclared variables."""
from dataclasses import dataclass, field
from typing import Dict, List, Set

from envguard.schema import Schema


@dataclass
class AuditResult:
    """Result of auditing an .env file against a schema."""
    undeclared: List[str] = field(default_factory=list)
    unused_optional: List[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.undeclared or self.unused_optional)

    def summary(self) -> str:
        lines = []
        if self.undeclared:
            lines.append(
                f"{len(self.undeclared)} undeclared variable(s): "
                + ", ".join(self.undeclared)
            )
        if self.unused_optional:
            lines.append(
                f"{len(self.unused_optional)} unused optional variable(s): "
                + ", ".join(self.unused_optional)
            )
        return "\n".join(lines) if lines else "No audit issues found."


def audit(env_vars: Dict[str, str], schema: Schema) -> AuditResult:
    """Compare loaded env vars against schema and return an AuditResult.

    Args:
        env_vars: Mapping of variable names to their string values.
        schema: Parsed Schema containing EnvVarSchema definitions.

    Returns:
        AuditResult with undeclared and unused_optional lists populated.
    """
    result = AuditResult()
    declared_keys: Set[str] = set(schema.variables.keys())
    env_keys: Set[str] = set(env_vars.keys())

    # Variables present in .env but not in schema
    result.undeclared = sorted(env_keys - declared_keys)

    # Optional schema variables not present in .env
    for key, var_schema in schema.variables.items():
        if not var_schema.required and key not in env_keys:
            result.unused_optional.append(key)
    result.unused_optional.sort()

    return result
