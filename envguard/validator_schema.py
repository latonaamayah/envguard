"""Schema-based validation of env vars with detailed rule checking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.schema import Schema


@dataclass
class SchemaViolation:
    key: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.key}: {self.message}"


@dataclass
class SchemaValidationResult:
    violations: List[SchemaViolation] = field(default_factory=list)
    passed: List[str] = field(default_factory=list)

    def has_violations(self) -> bool:
        return bool(self.violations)

    def violation_keys(self) -> List[str]:
        return [v.key for v in self.violations]

    def errors(self) -> List[SchemaViolation]:
        return [v for v in self.violations if v.rule in ("required", "type", "allowed")]

    def warnings(self) -> List[SchemaViolation]:
        return [v for v in self.violations if v.rule not in ("required", "type", "allowed")]

    def summary(self) -> str:
        total = len(self.passed) + len(self.violations)
        return (
            f"{len(self.passed)}/{total} keys passed schema validation, "
            f"{len(self.violations)} violation(s) found."
        )


def validate_schema(
    env: Dict[str, str],
    schema: Schema,
) -> SchemaValidationResult:
    result = SchemaValidationResult()

    for var in schema.variables:
        key = var.name
        value: Optional[str] = env.get(key)

        if value is None or value == "":
            if var.required:
                result.violations.append(
                    SchemaViolation(key, "required", "required variable is missing or empty")
                )
            else:
                result.passed.append(key)
            continue

        if var.type == "integer":
            try:
                int(value)
            except ValueError:
                result.violations.append(
                    SchemaViolation(key, "type", f"expected integer, got {value!r}")
                )
                continue

        elif var.type == "boolean":
            if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                result.violations.append(
                    SchemaViolation(key, "type", f"expected boolean, got {value!r}")
                )
                continue

        if var.allowed_values and value not in var.allowed_values:
            result.violations.append(
                SchemaViolation(
                    key,
                    "allowed",
                    f"{value!r} not in allowed values {var.allowed_values}",
                )
            )
            continue

        result.passed.append(key)

    return result
