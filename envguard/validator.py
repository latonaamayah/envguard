"""Validation logic for envguard."""

import re
from dataclasses import dataclass, field
from typing import Optional

from envguard.schema import EnvVarSchema, Schema


URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")


@dataclass
class ValidationError:
    variable: str
    message: str
    severity: str = "error"  # "error" or "warning"


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, variable: str, message: str):
        self.errors.append(ValidationError(variable, message, "error"))

    def add_warning(self, variable: str, message: str):
        self.warnings.append(ValidationError(variable, message, "warning"))


def _validate_type(name: str, value: str, expected_type: str) -> Optional[str]:
    if expected_type == "integer":
        try:
            int(value)
        except ValueError:
            return f"Expected integer, got '{value}'"
    elif expected_type == "boolean":
        if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
            return f"Expected boolean, got '{value}'"
    elif expected_type == "url":
        if not URL_PATTERN.match(value):
            return f"Expected valid URL, got '{value}'"
    elif expected_type == "email":
        if not EMAIL_PATTERN.match(value):
            return f"Expected valid email, got '{value}'"
    return None


def validate(env: dict[str, str], schema: Schema) -> ValidationResult:
    result = ValidationResult()

    for var in schema.variables:
        value = env.get(var.name)

        if value is None or value == "":
            if var.required and var.default is None:
                result.add_error(var.name, "Required variable is missing or empty")
            elif not var.required:
                result.add_warning(var.name, "Optional variable is not set")
            continue

        type_error = _validate_type(var.name, value, var.type)
        if type_error:
            result.add_error(var.name, type_error)

        if var.allowed_values and value not in var.allowed_values:
            result.add_error(
                var.name,
                f"Value '{value}' not in allowed values: {var.allowed_values}",
            )

    return result
