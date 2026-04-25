"""Tests for envguard.enforcer."""
import pytest
from envguard.enforcer import enforce, EnforceResult, EnforceEntry


@pytest.fixture()
def env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "supersecretkey",
        "PORT": "8080",
        "EMPTY_VAR": "",
        "spaced key": "value",
        "QUOTED": '"hello"',
    }


def test_returns_enforce_result(env):
    result = enforce(env, {})
    assert isinstance(result, EnforceResult)


def test_no_rules_no_entries(env):
    result = enforce(env, {})
    assert result.entries == []


def test_has_failures_false_when_all_pass(env):
    result = enforce(env, {"DATABASE_URL": ["not_empty"]})
    assert not result.has_failures


def test_has_failures_true_when_some_fail(env):
    result = enforce(env, {"EMPTY_VAR": ["not_empty"]})
    assert result.has_failures


def test_failed_keys_populated(env):
    result = enforce(env, {"EMPTY_VAR": ["not_empty"], "DATABASE_URL": ["not_empty"]})
    assert "EMPTY_VAR" in result.failed_keys
    assert "DATABASE_URL" not in result.failed_keys


def test_passed_keys_populated(env):
    result = enforce(env, {"SECRET_KEY": ["not_empty", "min_length_8"]})
    assert "SECRET_KEY" in result.passed_keys


def test_no_spaces_rule_pass(env):
    result = enforce(env, {"PORT": ["no_spaces"]})
    assert not result.has_failures


def test_no_spaces_rule_fail(env):
    result = enforce(env, {"spaced key": ["no_spaces"]})
    assert result.has_failures


def test_uppercase_key_rule_pass(env):
    result = enforce(env, {"DATABASE_URL": ["uppercase_key"]})
    assert not result.has_failures


def test_uppercase_key_rule_fail(env):
    result = enforce(env, {"spaced key": ["uppercase_key"]})
    assert result.has_failures


def test_min_length_8_pass(env):
    result = enforce(env, {"SECRET_KEY": ["min_length_8"]})
    assert not result.has_failures


def test_min_length_8_fail(env):
    result = enforce(env, {"PORT": ["min_length_8"]})
    assert result.has_failures


def test_no_quotes_fail(env):
    result = enforce(env, {"QUOTED": ["no_quotes"]})
    assert result.has_failures


def test_no_quotes_pass(env):
    result = enforce(env, {"PORT": ["no_quotes"]})
    assert not result.has_failures


def test_unknown_rule_is_failure(env):
    result = enforce(env, {"PORT": ["nonexistent_rule"]})
    assert result.has_failures
    assert "Unknown rule" in result.entries[0].message


def test_custom_rule_applied(env):
    def must_be_numeric(k, v):
        return None if v.isdigit() else f"{k} must be numeric"

    result = enforce(env, {"PORT": ["numeric"]}, custom_rules={"numeric": must_be_numeric})
    assert not result.has_failures


def test_custom_rule_fails(env):
    def must_be_numeric(k, v):
        return None if v.isdigit() else f"{k} must be numeric"

    result = enforce(env, {"DATABASE_URL": ["numeric"]}, custom_rules={"numeric": must_be_numeric})
    assert result.has_failures


def test_summary_format(env):
    result = enforce(env, {"PORT": ["not_empty"], "EMPTY_VAR": ["not_empty"]})
    s = result.summary()
    assert "1/2" in s or "passed" in s


def test_entry_str_pass(env):
    result = enforce(env, {"PORT": ["not_empty"]})
    entry = result.entries[0]
    assert "PASS" in str(entry)


def test_entry_str_fail(env):
    result = enforce(env, {"EMPTY_VAR": ["not_empty"]})
    entry = result.entries[0]
    assert "FAIL" in str(entry)


def test_missing_key_treated_as_empty(env):
    result = enforce(env, {"NONEXISTENT": ["not_empty"]})
    assert result.has_failures
