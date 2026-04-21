"""Tests for envguard.bouncer."""

import pytest
from envguard.bouncer import bounce, BounceResult, BounceEntry


@pytest.fixture
def env():
    return {
        "DB_PASSWORD": "password123",
        "APP_SECRET": "secret",
        "DB_HOST": "db.example.com",
        "PORT": "5432",
        "ADMIN_USER": "admin",
        "API_KEY": "xK9#mP2$vL8nQ",
    }


def test_returns_bounce_result(env):
    result = bounce(env)
    assert isinstance(result, BounceResult)


def test_entry_count_matches_env(env):
    result = bounce(env)
    assert len(result.entries) == len(env)


def test_has_rejected_true_when_forbidden_values(env):
    result = bounce(env)
    assert result.has_rejected() is True


def test_has_rejected_false_for_clean_env():
    clean = {"DB_HOST": "db.example.com", "PORT": "5432", "API_KEY": "xK9#mP2$vL8nQ"}
    result = bounce(clean)
    assert result.has_rejected() is False


def test_password123_rejected(env):
    result = bounce(env)
    assert "DB_PASSWORD" in result.rejected_keys()


def test_secret_value_rejected(env):
    result = bounce(env)
    assert "APP_SECRET" in result.rejected_keys()


def test_admin_value_rejected(env):
    result = bounce(env)
    assert "ADMIN_USER" in result.rejected_keys()


def test_clean_host_allowed(env):
    result = bounce(env)
    assert "DB_HOST" in result.allowed_keys()


def test_strong_api_key_allowed(env):
    result = bounce(env)
    assert "API_KEY" in result.allowed_keys()


def test_blank_value_rejected():
    result = bounce({"EMPTY": "", "SPACES": "   "})
    assert "EMPTY" in result.rejected_keys()
    assert "SPACES" in result.rejected_keys()


def test_custom_patterns_override_defaults():
    result = bounce({"DB_HOST": "forbidden_host"}, patterns=[r"^forbidden_host$"])
    assert "DB_HOST" in result.rejected_keys()


def test_custom_patterns_allow_defaults():
    # With custom patterns, 'password123' should NOT be rejected
    result = bounce({"DB_PASSWORD": "password123"}, patterns=[r"^totally_different$"])
    assert "DB_PASSWORD" in result.allowed_keys()


def test_entry_message_rejected(env):
    result = bounce(env)
    rejected_entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert "rejected" in rejected_entry.message()


def test_entry_message_allowed(env):
    result = bounce(env)
    allowed_entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert "allowed" in allowed_entry.message()


def test_summary_string(env):
    result = bounce(env)
    summary = result.summary()
    assert "rejected" in summary
    assert "/" in summary


def test_entry_is_bounce_entry(env):
    result = bounce(env)
    for entry in result.entries:
        assert isinstance(entry, BounceEntry)
