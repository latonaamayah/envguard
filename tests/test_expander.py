"""Tests for envguard.expander."""
import pytest
from envguard.expander import expand, ExpandResult, ExpandEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PWD": "secret",
        "APP_ENV": "production",
        "LOG_LVL": "info",
    }


def test_returns_expand_result(env):
    result = expand(env, {})
    assert isinstance(result, ExpandResult)


def test_entry_count_matches_env(env):
    result = expand(env, {})
    assert len(result.entries) == len(env)


def test_no_expansions_when_mapping_empty(env):
    result = expand(env, {})
    assert not result.has_expansions()


def test_single_key_expanded(env):
    result = expand(env, {"DB_PWD": "DB_PASSWORD"})
    assert "DB_PASSWORD" in result.as_dict()


def test_original_key_removed_after_expansion(env):
    result = expand(env, {"DB_PWD": "DB_PASSWORD"})
    assert "DB_PWD" not in result.as_dict()


def test_expanded_value_preserved(env):
    result = expand(env, {"DB_PWD": "DB_PASSWORD"})
    assert result.as_dict()["DB_PASSWORD"] == "secret"


def test_has_expansions_true(env):
    result = expand(env, {"LOG_LVL": "LOG_LEVEL"})
    assert result.has_expansions()


def test_expanded_keys_list(env):
    result = expand(env, {"LOG_LVL": "LOG_LEVEL", "DB_PWD": "DB_PASSWORD"})
    assert set(result.expanded_keys()) == {"LOG_LEVEL", "DB_PASSWORD"}


def test_unexpanded_keys_unchanged(env):
    result = expand(env, {"LOG_LVL": "LOG_LEVEL"})
    d = result.as_dict()
    assert "DB_HOST" in d
    assert d["DB_HOST"] == "localhost"


def test_summary_string(env):
    result = expand(env, {"LOG_LVL": "LOG_LEVEL"})
    s = result.summary()
    assert "1" in s
    assert "4" in s


def test_entry_message_expanded(env):
    result = expand(env, {"DB_PWD": "DB_PASSWORD"})
    entry = next(e for e in result.entries if e.was_expanded)
    assert "DB_PWD" in entry.message()
    assert "DB_PASSWORD" in entry.message()


def test_entry_message_unchanged(env):
    result = expand(env, {})
    entry = result.entries[0]
    assert "unchanged" in entry.message()


def test_mapping_key_not_in_env_is_ignored():
    env = {"FOO": "bar"}
    result = expand(env, {"BAZ": "BAZ_FULL"})
    assert result.as_dict() == {"FOO": "bar"}
    assert not result.has_expansions()


def test_identity_mapping_does_not_expand(env):
    result = expand(env, {"DB_HOST": "DB_HOST"})
    assert not result.has_expansions()
