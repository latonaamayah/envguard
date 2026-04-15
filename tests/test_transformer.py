"""Tests for envguard.transformer."""
import pytest
from envguard.transformer import transform, TransformResult


@pytest.fixture
def env():
    return {
        "APP_ENV": "production",
        "DB_HOST": "  localhost  ",
        "API_KEY": '"secret123"',
        "LOG_LEVEL": "debug",
    }


def test_uppercase_rule(env):
    result = transform(env, {"LOG_LEVEL": "uppercase"})
    assert result.vars["LOG_LEVEL"] == "DEBUG"


def test_lowercase_rule(env):
    result = transform(env, {"APP_ENV": "lowercase"})
    assert result.vars["APP_ENV"] == "production"


def test_strip_rule(env):
    result = transform(env, {"DB_HOST": "strip"})
    assert result.vars["DB_HOST"] == "localhost"


def test_strip_quotes_rule(env):
    result = transform(env, {"API_KEY": "strip_quotes"})
    assert result.vars["API_KEY"] == "secret123"


def test_no_rules_returns_original(env):
    result = transform(env, {})
    assert result.vars == env
    assert not result.has_changes()


def test_entry_records_original_and_transformed(env):
    result = transform(env, {"LOG_LEVEL": "uppercase"})
    entry = next(e for e in result.entries if e.key == "LOG_LEVEL")
    assert entry.original == "debug"
    assert entry.transformed == "DEBUG"
    assert entry.rule == "uppercase"
    assert entry.changed is True


def test_unchanged_entry_changed_is_false(env):
    result = transform(env, {"APP_ENV": "lowercase"})
    entry = next(e for e in result.entries if e.key == "APP_ENV")
    assert entry.changed is False


def test_has_changes_true_when_value_differs(env):
    result = transform(env, {"DB_HOST": "strip"})
    assert result.has_changes()


def test_has_changes_false_when_no_diff(env):
    result = transform(env, {"APP_ENV": "lowercase"})
    assert not result.has_changes()


def test_unknown_rule_raises(env):
    with pytest.raises(ValueError, match="Unknown transform rule"):
        transform(env, {"APP_ENV": "nonexistent_rule"})


def test_custom_rule_applied(env):
    result = transform(env, {"APP_ENV": "exclaim"}, custom_rules={"exclaim": lambda v: v + "!"})
    assert result.vars["APP_ENV"] == "production!"


def test_multiple_rules_applied(env):
    result = transform(env, {"LOG_LEVEL": "uppercase", "DB_HOST": "strip"})
    assert result.vars["LOG_LEVEL"] == "DEBUG"
    assert result.vars["DB_HOST"] == "localhost"


def test_summary_lists_changed_keys(env):
    result = transform(env, {"LOG_LEVEL": "uppercase", "DB_HOST": "strip"})
    summary = result.summary()
    assert "LOG_LEVEL" in summary
    assert "DB_HOST" in summary


def test_summary_no_changes_message(env):
    result = transform(env, {})
    assert result.summary() == "No transformations applied."


def test_untouched_keys_preserved(env):
    result = transform(env, {"LOG_LEVEL": "uppercase"})
    assert result.vars["APP_ENV"] == env["APP_ENV"]
    assert result.vars["DB_HOST"] == env["DB_HOST"]
