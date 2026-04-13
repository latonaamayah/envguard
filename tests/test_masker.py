"""Tests for envguard.masker."""
import pytest
from envguard.masker import mask, _is_sensitive, DEFAULT_MASK


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_is_not_sensitive_host():
    assert _is_sensitive("DB_HOST") is False


def test_is_not_sensitive_port():
    assert _is_sensitive("APP_PORT") is False


# ---------------------------------------------------------------------------
# mask()
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_env():
    return {
        "APP_ENV": "production",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "GITHUB_TOKEN": "ghp_abc123",
        "APP_PORT": "8080",
    }


def test_non_sensitive_values_unchanged(sample_env):
    result = mask(sample_env)
    assert result.masked["APP_ENV"] == "production"
    assert result.masked["DB_HOST"] == "localhost"
    assert result.masked["APP_PORT"] == "8080"


def test_sensitive_values_replaced(sample_env):
    result = mask(sample_env)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["GITHUB_TOKEN"] == DEFAULT_MASK


def test_masked_keys_recorded(sample_env):
    result = mask(sample_env)
    assert "DB_PASSWORD" in result.masked_keys
    assert "GITHUB_TOKEN" in result.masked_keys


def test_has_masked_true(sample_env):
    result = mask(sample_env)
    assert result.has_masked is True


def test_has_masked_false():
    result = mask({"APP_ENV": "dev", "PORT": "3000"})
    assert result.has_masked is False


def test_extra_sensitive_key(sample_env):
    result = mask(sample_env, extra_sensitive=["DB_HOST"])
    assert result.masked["DB_HOST"] == DEFAULT_MASK
    assert "DB_HOST" in result.masked_keys


def test_reveal_prefix(sample_env):
    result = mask(sample_env, reveal_prefix=3)
    assert result.masked["DB_PASSWORD"].startswith("s3c")
    assert result.masked["DB_PASSWORD"].endswith(DEFAULT_MASK)


def test_reveal_prefix_shorter_than_value():
    result = mask({"SECRET_KEY": "ab"}, reveal_prefix=5)
    # value shorter than prefix → fully masked
    assert result.masked["SECRET_KEY"] == DEFAULT_MASK


def test_original_is_unchanged(sample_env):
    result = mask(sample_env)
    assert result.original["DB_PASSWORD"] == "s3cr3t"


def test_summary_with_masked(sample_env):
    result = mask(sample_env)
    assert "Masked" in result.summary()
    assert "DB_PASSWORD" in result.summary()


def test_summary_no_masked():
    result = mask({"PORT": "8080"})
    assert result.summary() == "No values were masked."
