"""Tests for envguard.whitelister."""
import pytest

from envguard.whitelister import WhitelistEntry, WhitelistResult, whitelist


@pytest.fixture()
def env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "s3cr3t",
        "APP_ENV": "production",
        "DEBUG": "false",
    }


def test_returns_whitelist_result(env):
    result = whitelist(env, allowed=["DB_HOST"])
    assert isinstance(result, WhitelistResult)


def test_entry_count_matches_env(env):
    result = whitelist(env, allowed=["DB_HOST"])
    assert len(result.entries) == len(env)


def test_has_rejected_true_when_some_rejected(env):
    result = whitelist(env, allowed=["DB_HOST"])
    assert result.has_rejected is True


def test_has_rejected_false_when_all_allowed(env):
    result = whitelist(env, allowed=list(env.keys()))
    assert result.has_rejected is False


def test_allowed_keys_contains_only_whitelisted(env):
    result = whitelist(env, allowed=["DB_HOST", "DB_PORT"])
    assert set(result.allowed_keys) == {"DB_HOST", "DB_PORT"}


def test_rejected_keys_contains_non_whitelisted(env):
    result = whitelist(env, allowed=["DB_HOST", "DB_PORT"])
    assert "SECRET_KEY" in result.rejected_keys
    assert "APP_ENV" in result.rejected_keys
    assert "DEBUG" in result.rejected_keys


def test_allowed_vars_returns_filtered_dict(env):
    result = whitelist(env, allowed=["DB_HOST", "DB_PORT"])
    assert result.allowed_vars == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_empty_allowed_list_rejects_all(env):
    result = whitelist(env, allowed=[])
    assert result.allowed_keys == []
    assert len(result.rejected_keys) == len(env)


def test_all_keys_allowed(env):
    result = whitelist(env, allowed=list(env.keys()))
    assert result.allowed_keys == list(env.keys())
    assert result.rejected_keys == []


def test_case_insensitive_matching(env):
    result = whitelist(env, allowed=["db_host", "app_env"], case_sensitive=False)
    assert "DB_HOST" in result.allowed_keys
    assert "APP_ENV" in result.allowed_keys


def test_case_sensitive_does_not_match_lowercase(env):
    result = whitelist(env, allowed=["db_host"], case_sensitive=True)
    assert "DB_HOST" not in result.allowed_keys
    assert "DB_HOST" in result.rejected_keys


def test_summary_contains_counts(env):
    result = whitelist(env, allowed=["DB_HOST", "DB_PORT"])
    summary = result.summary()
    assert "5" in summary
    assert "2" in summary
    assert "3" in summary


def test_entry_is_whitelist_entry_type(env):
    result = whitelist(env, allowed=["DB_HOST"])
    for entry in result.entries:
        assert isinstance(entry, WhitelistEntry)


def test_allowed_entry_flag(env):
    result = whitelist(env, allowed=["DB_HOST"])
    db_host_entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert db_host_entry.allowed is True


def test_rejected_entry_flag(env):
    result = whitelist(env, allowed=["DB_HOST"])
    secret_entry = next(e for e in result.entries if e.key == "SECRET_KEY")
    assert secret_entry.allowed is False
