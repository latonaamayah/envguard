"""Tests for envguard.shielder."""
import pytest
from envguard.shielder import shield, ShieldResult, ShieldEntry, _is_sensitive


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "AUTH_TOKEN": "tok_xyz",
    }


def test_returns_shield_result(env):
    result = shield(env)
    assert isinstance(result, ShieldResult)


def test_entry_count_matches_env(env):
    result = shield(env)
    assert len(result.entries) == len(env)


def test_sensitive_keys_shielded(env):
    result = shield(env)
    assert "DB_PASSWORD" in result.shielded_keys
    assert "API_KEY" in result.shielded_keys
    assert "AUTH_TOKEN" in result.shielded_keys


def test_non_sensitive_keys_not_shielded(env):
    result = shield(env)
    assert "DB_HOST" not in result.shielded_keys
    assert "DB_PORT" not in result.shielded_keys
    assert "APP_NAME" not in result.shielded_keys


def test_shielded_value_uses_default_placeholder(env):
    result = shield(env)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert entry.shielded_value == "${DB_PASSWORD}"


def test_custom_prefix_suffix(env):
    result = shield(env, prefix="%{", suffix="}")
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert entry.shielded_value == "%{API_KEY}"


def test_explicit_keys_override_auto_detection(env):
    result = shield(env, keys=["DB_HOST"])
    assert "DB_HOST" in result.shielded_keys
    # Sensitive keys NOT shielded when explicit list provided
    assert "DB_PASSWORD" not in result.shielded_keys


def test_has_shielded_true_when_sensitive_present(env):
    result = shield(env)
    assert result.has_shielded is True


def test_has_shielded_false_when_no_sensitive():
    result = shield({"HOST": "localhost", "PORT": "80"})
    assert result.has_shielded is False


def test_as_dict_returns_shielded_values(env):
    result = shield(env)
    d = result.as_dict
    assert d["DB_PASSWORD"] == "${DB_PASSWORD}"
    assert d["DB_HOST"] == "localhost"


def test_summary_string(env):
    result = shield(env)
    s = result.summary()
    assert "/" in s
    assert "shielded" in s


def test_str_shielded_entry(env):
    result = shield(env)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert "shielded" in str(entry)


def test_str_unchanged_entry(env):
    result = shield(env)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert "unchanged" in str(entry)


def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("AUTH_TOKEN") is True


def test_is_not_sensitive_host():
    assert _is_sensitive("DB_HOST") is False
