import pytest
from envguard.censor import censor, _is_sensitive, CensorResult


@pytest.fixture
def env():
    return {
        "DB_PASSWORD": "s3cr3t",
        "API_TOKEN": "tok_abc123",
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "SECRET_KEY": "mysecret",
    }


def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("API_TOKEN") is True


def test_is_not_sensitive_host():
    assert _is_sensitive("APP_HOST") is False


def test_is_not_sensitive_port():
    assert _is_sensitive("APP_PORT") is False


def test_returns_censor_result(env):
    result = censor(env)
    assert isinstance(result, CensorResult)


def test_sensitive_keys_censored(env):
    result = censor(env)
    d = result.as_dict()
    assert d["DB_PASSWORD"] == "***"
    assert d["API_TOKEN"] == "***"
    assert d["SECRET_KEY"] == "***"


def test_non_sensitive_keys_unchanged(env):
    result = censor(env)
    d = result.as_dict()
    assert d["APP_HOST"] == "localhost"
    assert d["APP_PORT"] == "8080"


def test_has_censored_true(env):
    result = censor(env)
    assert result.has_censored() is True


def test_has_censored_false():
    result = censor({"APP_HOST": "localhost"})
    assert result.has_censored() is False


def test_censored_keys_list(env):
    result = censor(env)
    censored = result.censored_keys()
    assert "DB_PASSWORD" in censored
    assert "APP_HOST" not in censored


def test_explicit_keys_override(env):
    result = censor(env, keys=["APP_HOST"])
    d = result.as_dict()
    assert d["APP_HOST"] == "***"
    assert d["DB_PASSWORD"] == "s3cr3t"


def test_summary_string(env):
    result = censor(env)
    summary = result.summary()
    assert "censored" in summary
    assert "5" in summary
