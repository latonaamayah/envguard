"""Tests for envguard.validator_env."""
import pytest
from envguard.validator_env import (
    EnvViolation,
    EnvValidationResult,
    validate_env,
)


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "abc123secret",
        "EMPTY_VAR": "",
    }


def test_returns_env_validation_result(env):
    result = validate_env(env, keys=["DB_HOST"])
    assert isinstance(result, EnvValidationResult)


def test_no_violations_for_clean_env(env):
    result = validate_env(env, keys=["DB_HOST", "DB_PORT", "API_KEY"])
    assert not result.has_violations()


def test_empty_value_raises_violation(env):
    result = validate_env(env, keys=["EMPTY_VAR"])
    assert result.has_violations()
    assert "EMPTY_VAR" in result.violation_keys()


def test_whitespace_only_value_raises_violation():
    result = validate_env({"FOO": "   "})
    assert result.has_violations()
    assert "FOO" in result.violation_keys()


def test_newline_in_value_raises_violation():
    result = validate_env({"SECRET": "line1\nline2"})
    assert result.has_violations()
    assert any(v.rule == "no_newlines" for v in result.violations)


def test_carriage_return_in_value_raises_violation():
    result = validate_env({"SECRET": "value\r"})
    assert result.has_violations()
    assert any(v.rule == "no_newlines" for v in result.violations)


def test_null_byte_in_value_raises_violation():
    result = validate_env({"BAD": "val\x00ue"})
    assert result.has_violations()
    assert any(v.rule == "no_null_bytes" for v in result.violations)


def test_value_exceeding_max_length_raises_violation():
    result = validate_env({"LONG": "x" * 600})
    assert result.has_violations()
    assert any(v.rule == "max_length" for v in result.violations)


def test_custom_max_length_respected():
    result = validate_env({"SHORT": "hello"}, max_length=3)
    assert result.has_violations()
    assert any(v.rule == "max_length" for v in result.violations)


def test_value_within_custom_max_length_passes():
    result = validate_env({"OK": "hi"}, max_length=10)
    assert not result.has_violations()


def test_keys_filter_limits_checked_keys():
    env = {"GOOD": "ok", "BAD": ""}
    result = validate_env(env, keys=["GOOD"])
    assert not result.has_violations()


def test_all_keys_checked_when_keys_none():
    env = {"GOOD": "ok", "BAD": ""}
    result = validate_env(env)
    assert result.has_violations()
    assert "BAD" in result.violation_keys()


def test_violation_str_representation():
    v = EnvViolation(key="FOO", rule="not_empty", message="must not be empty")
    assert "FOO" in str(v)
    assert "not_empty" in str(v)


def test_summary_no_violations():
    result = EnvValidationResult()
    assert "passed" in result.summary()


def test_summary_with_violations():
    result = EnvValidationResult(violations=[
        EnvViolation(key="X", rule="not_empty", message="empty")
    ])
    assert "X" in result.summary()
