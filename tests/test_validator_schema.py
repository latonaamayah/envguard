"""Tests for envguard.validator_schema."""
import pytest

from envguard.schema import Schema
from envguard.validator_schema import (
    SchemaValidationResult,
    SchemaViolation,
    validate_schema,
)


@pytest.fixture
def schema() -> Schema:
    return Schema.from_dict(
        [
            {"name": "APP_ENV", "required": True, "type": "string", "allowed_values": ["dev", "prod", "staging"]},
            {"name": "PORT", "required": True, "type": "integer"},
            {"name": "DEBUG", "required": False, "type": "boolean"},
            {"name": "TIMEOUT", "required": False, "type": "integer"},
        ]
    )


def test_returns_schema_validation_result(schema):
    result = validate_schema({"APP_ENV": "dev", "PORT": "8080"}, schema)
    assert isinstance(result, SchemaValidationResult)


def test_all_valid_no_violations(schema):
    result = validate_schema({"APP_ENV": "prod", "PORT": "443", "DEBUG": "true"}, schema)
    assert not result.has_violations()


def test_missing_required_key_is_violation(schema):
    result = validate_schema({"PORT": "8080"}, schema)
    assert result.has_violations()
    assert "APP_ENV" in result.violation_keys()


def test_empty_required_value_is_violation(schema):
    result = validate_schema({"APP_ENV": "", "PORT": "8080"}, schema)
    assert "APP_ENV" in result.violation_keys()


def test_invalid_integer_type_is_violation(schema):
    result = validate_schema({"APP_ENV": "dev", "PORT": "not-a-number"}, schema)
    assert "PORT" in result.violation_keys()
    violations = {v.key: v for v in result.violations}
    assert violations["PORT"].rule == "type"


def test_invalid_boolean_type_is_violation(schema):
    result = validate_schema({"APP_ENV": "dev", "PORT": "8080", "DEBUG": "maybe"}, schema)
    assert "DEBUG" in result.violation_keys()


def test_disallowed_value_is_violation(schema):
    result = validate_schema({"APP_ENV": "local", "PORT": "8080"}, schema)
    assert "APP_ENV" in result.violation_keys()
    violations = {v.key: v for v in result.violations}
    assert violations["APP_ENV"].rule == "allowed"


def test_optional_missing_key_passes(schema):
    result = validate_schema({"APP_ENV": "dev", "PORT": "8080"}, schema)
    assert "DEBUG" not in result.violation_keys()


def test_passed_keys_recorded(schema):
    result = validate_schema({"APP_ENV": "staging", "PORT": "3000"}, schema)
    assert "APP_ENV" in result.passed
    assert "PORT" in result.passed


def test_errors_returns_only_error_rules(schema):
    result = validate_schema({"PORT": "bad", "APP_ENV": ""}, schema)
    for v in result.errors():
        assert v.rule in ("required", "type", "allowed")


def test_summary_includes_counts(schema):
    result = validate_schema({"APP_ENV": "dev", "PORT": "8080"}, schema)
    summary = result.summary()
    assert "passed" in summary
    assert "violation" in summary


def test_violation_str_includes_rule_and_key():
    v = SchemaViolation("MY_KEY", "required", "missing")
    s = str(v)
    assert "MY_KEY" in s
    assert "required" in s


def test_boolean_true_variants_pass(schema):
    for val in ("true", "false", "1", "0", "yes", "no"):
        result = validate_schema({"APP_ENV": "dev", "PORT": "80", "DEBUG": val}, schema)
        assert "DEBUG" not in result.violation_keys(), f"Expected {val!r} to pass"
