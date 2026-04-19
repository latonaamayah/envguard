import pytest
from envguard.scrambler import scramble, ScramblerResult, _is_sensitive


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
    }


def test_returns_scrambler_result(env):
    result = scramble(env)
    assert isinstance(result, ScramblerResult)


def test_entry_count_matches_env(env):
    result = scramble(env)
    assert len(result.entries) == len(env)


def test_sensitive_keys_scrambled(env):
    result = scramble(env)
    assert "DB_PASSWORD" in result.scrambled_keys
    assert "API_KEY" in result.scrambled_keys


def test_non_sensitive_keys_unchanged(env):
    result = scramble(env)
    d = result.as_dict()
    assert d["DB_HOST"] == "localhost"
    assert d["APP_NAME"] == "myapp"


def test_has_scrambled_true(env):
    result = scramble(env)
    assert result.has_scrambled is True


def test_has_scrambled_false_when_no_sensitive():
    result = scramble({"HOST": "localhost", "PORT": "5432"})
    assert result.has_scrambled is False


def test_explicit_keys_scrambled(env):
    result = scramble(env, keys=["APP_NAME"], auto_detect=False)
    assert "APP_NAME" in result.scrambled_keys
    assert "DB_PASSWORD" not in result.scrambled_keys


def test_scrambled_value_differs_from_original(env):
    result = scramble(env)
    d = result.as_dict()
    assert d["DB_PASSWORD"] != "s3cr3t"


def test_scrambled_value_is_deterministic(env):
    r1 = scramble(env)
    r2 = scramble(env)
    assert r1.as_dict()["DB_PASSWORD"] == r2.as_dict()["DB_PASSWORD"]


def test_summary_reports_count(env):
    result = scramble(env)
    assert "2 key(s) scrambled" in result.summary()


def test_summary_no_scrambled():
    result = scramble({"HOST": "localhost"})
    assert result.summary() == "No keys scrambled."


def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("AUTH_TOKEN") is True


def test_is_not_sensitive_host():
    assert _is_sensitive("DB_HOST") is False
