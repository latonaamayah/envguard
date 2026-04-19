import pytest
from envguard.obscurer import obscure, _is_sensitive, ObscureResult


@pytest.fixture
def env():
    return {
        "DB_PASSWORD": "supersecret",
        "API_TOKEN": "tok_abc123",
        "APP_HOST": "localhost",
        "APP_PORT": "5432",
        "SECRET_KEY": "mysecretkey",
    }


def test_returns_obscure_result(env):
    result = obscure(env)
    assert isinstance(result, ObscureResult)


def test_sensitive_keys_obscured(env):
    result = obscure(env)
    assert "DB_PASSWORD" in result.obscured_keys()
    assert "API_TOKEN" in result.obscured_keys()
    assert "SECRET_KEY" in result.obscured_keys()


def test_non_sensitive_keys_unchanged(env):
    result = obscure(env)
    d = result.as_dict()
    assert d["APP_HOST"] == "localhost"
    assert d["APP_PORT"] == "5432"


def test_stars_style_replaces_with_stars(env):
    result = obscure(env, style="stars")
    d = result.as_dict()
    assert d["DB_PASSWORD"] == "*" * len("supersecret")


def test_partial_style_shows_edges():
    env = {"API_TOKEN": "abcdefgh"}
    result = obscure(env, style="partial")
    d = result.as_dict()
    assert d["API_TOKEN"].startswith("ab")
    assert d["API_TOKEN"].endswith("gh")
    assert "****" in d["API_TOKEN"]


def test_hash_style_returns_8_chars():
    env = {"DB_PASSWORD": "secret"}
    result = obscure(env, style="hash")
    d = result.as_dict()
    assert len(d["DB_PASSWORD"]) == 8


def test_explicit_keys_override_sensitivity(env):
    result = obscure(env, keys=["APP_HOST"])
    assert "APP_HOST" in result.obscured_keys()
    assert "DB_PASSWORD" not in result.obscured_keys()


def test_has_obscured_true(env):
    result = obscure(env)
    assert result.has_obscured()


def test_has_obscured_false():
    result = obscure({"HOST": "localhost", "PORT": "8080"})
    assert not result.has_obscured()


def test_summary_format(env):
    result = obscure(env)
    s = result.summary()
    assert "/" in s
    assert "obscured" in s


def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD")


def test_is_sensitive_token():
    assert _is_sensitive("API_TOKEN")


def test_is_not_sensitive_host():
    assert not _is_sensitive("APP_HOST")
