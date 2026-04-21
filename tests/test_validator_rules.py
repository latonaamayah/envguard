"""Tests for envguard.validator_rules."""
import pytest

from envguard.validator_rules import (
    RuleResult,
    RuleViolation,
    apply_rules,
    rule_alphanumeric,
    rule_no_whitespace,
    rule_not_empty,
    rule_numeric,
    rule_url,
)


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_URL": "https://api.example.com",
        "SECRET": "  padded  ",
        "EMPTY": "",
    }


# --- unit rule tests ---

def test_rule_not_empty_passes():
    assert rule_not_empty("K", "value") is None


def test_rule_not_empty_fails_blank():
    assert rule_not_empty("K", "") is not None


def test_rule_not_empty_fails_whitespace_only():
    assert rule_not_empty("K", "   ") is not None


def test_rule_no_whitespace_passes():
    assert rule_no_whitespace("K", "clean") is None


def test_rule_no_whitespace_fails_leading():
    assert rule_no_whitespace("K", " bad") is not None


def test_rule_no_whitespace_fails_trailing():
    assert rule_no_whitespace("K", "bad ") is not None


def test_rule_alphanumeric_passes():
    assert rule_alphanumeric("K", "hello_world") is None


def test_rule_alphanumeric_fails_space():
    assert rule_alphanumeric("K", "hello world") is not None


def test_rule_numeric_passes_integer():
    assert rule_numeric("K", "42") is None


def test_rule_numeric_passes_float():
    assert rule_numeric("K", "3.14") is None


def test_rule_numeric_fails_text():
    assert rule_numeric("K", "abc") is not None


def test_rule_url_passes_https():
    assert rule_url("K", "https://example.com") is None


def test_rule_url_passes_http():
    assert rule_url("K", "http://example.com/path") is None


def test_rule_url_fails_plain_text():
    assert rule_url("K", "example.com") is not None


# --- apply_rules integration ---

def test_apply_rules_returns_rule_result(env):
    result = apply_rules(env, {})
    assert isinstance(result, RuleResult)


def test_apply_rules_no_violations_clean_env(env):
    result = apply_rules(env, {"not_empty": ["DB_HOST", "DB_PORT"]})
    assert not result.has_violations


def test_apply_rules_detects_empty_value(env):
    result = apply_rules(env, {"not_empty": ["EMPTY"]})
    assert result.has_violations
    assert result.errors[0].key == "EMPTY"


def test_apply_rules_detects_whitespace(env):
    result = apply_rules(env, {"no_whitespace": ["SECRET"]})
    assert result.has_violations


def test_apply_rules_unknown_rule_skipped(env):
    result = apply_rules(env, {"nonexistent_rule": ["DB_HOST"]})
    assert not result.has_violations


def test_apply_rules_severity_warning(env):
    result = apply_rules(env, {"not_empty": ["EMPTY"]}, severity="warning")
    assert result.warnings[0].severity == "warning"
    assert not result.errors


def test_violation_str_format():
    v = RuleViolation(key="MY_KEY", rule="not_empty", message="bad", severity="error")
    assert "MY_KEY" in str(v)
    assert "not_empty" in str(v)
    assert "ERROR" in str(v)


def test_rule_result_summary():
    r = RuleResult()
    r.violations.append(RuleViolation("K", "r", "m", "error"))
    r.violations.append(RuleViolation("K2", "r", "m", "warning"))
    assert "1 error" in r.summary()
    assert "1 warning" in r.summary()
