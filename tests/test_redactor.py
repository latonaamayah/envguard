"""Tests for envguard.redactor."""

import pytest
from envguard.redactor import redact, _is_sensitive, DEFAULT_PLACEHOLDER


# ---------------------------------------------------------------------------
# _is_sensitive helpers
# ---------------------------------------------------------------------------

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_secret():
    assert _is_sensitive("APP_SECRET") is True


def test_is_not_sensitive_host():
    assert _is_sensitive("DB_HOST") is False


def test_is_not_sensitive_port():
    assert _is_sensitive("PORT") is False


def test_is_sensitive_case_insensitive():
    """Key matching should be case-insensitive so lowercase keys are caught."""
    assert _is_sensitive("db_password") is True
    assert _is_sensitive("github_token") is True
    assert _is_sensitive("stripe_api_key") is True


# ---------------------------------------------------------------------------
# redact()
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env():
    return {
        "APP_ENV": "production",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "GITHUB_TOKEN": "ghp_abc123",
        "PORT": "8080",
    }


def test_sensitive_values_replaced(sample_env):
    result = redact(sample_env)
    assert result.redacted["DB_PASSWORD"] == DEFAULT_PLACEHOLDER
    assert result.redacted["GITHUB_TOKEN"] == DEFAULT_PLACEHOLDER


def test_non_sensitive_values_unchanged(sample_env):
    result = redact(sample_env)
    assert result.redacted["APP_ENV"] == "production"
    assert result.redacted["DB_HOST"] == "localhost"
    assert result.redacted["PORT"] == "8080"


def test_redacted_keys_list(sample_env):
    result = redact(sample_env)
    assert set(result.redacted_keys) == {"DB_PASSWORD", "GITHUB_TOKEN"}


def test_has_redacted_true(sample_env):
    result = redact(sample_env)
    assert result.has_redacted() is True


def test_has_redacted_false():
    result = redact({"HOST": "localhost", "PORT": "5432"})
    assert result.has_redacted() is False


def test_custom_placeholder(sample_env):
    result = redact(sample_env, placeholder="***")
    assert result.redacted["DB_PASSWORD"] == "***"


def test_extra_keys_redacted(sample_env):
    result = redact(sample_env, extra_keys=["APP_ENV"])
    assert result.redacted["APP_ENV"] == DEFAULT_PLACEHOLDER
    assert "APP_ENV" in result.redacted_keys


def test_extra_keys_unknown_key(sample_env):
    """extra_keys entries that are absent from the env should be silently ignored."""
    result = redact(sample_env, extra_keys=["NONEXISTENT_KEY"])
    assert "NONEXISTENT_KEY" not in result.redacted
    assert "NONEXISTENT_KEY" not in result.redacted_keys


def test_original_env_unchanged(sample_env):
    original_copy = dict(sample_env)
    redact(sample_env)
    assert sample_env == original_copy


def test_summary_message(sample_env):
    result = redact(sample_env)
    assert "2/5" in result.summary()


def test_empty_env():
    result = redact({})
    assert result.has_redacted() is False
    assert result.redacted == {}
