import pytest
from envguard.strikethrough import strike, StrikeResult, StrikeEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "API_KEY": "abc123",
        "DEBUG": "",
        "APP_NAME": "myapp",
    }


def test_returns_strike_result(env):
    result = strike(env)
    assert isinstance(result, StrikeResult)


def test_no_strikes_by_default(env):
    result = strike(env)
    assert not result.has_struck()
    assert len(result.kept) == len(env)


def test_strike_by_explicit_key(env):
    result = strike(env, keys=["DB_PASSWORD"])
    assert "DB_PASSWORD" in result.struck_keys()
    assert "DB_PASSWORD" not in result.kept


def test_strike_by_pattern(env):
    result = strike(env, patterns=[r"^DB_"])
    assert "DB_HOST" in result.struck_keys()
    assert "DB_PASSWORD" in result.struck_keys()
    assert "API_KEY" not in result.struck_keys()


def test_strike_empty_only(env):
    result = strike(env, empty_only=True)
    assert "DEBUG" in result.struck_keys()
    assert "DB_HOST" not in result.struck_keys()


def test_kept_contains_non_struck(env):
    result = strike(env, keys=["API_KEY"])
    assert "DB_HOST" in result.kept
    assert "APP_NAME" in result.kept
    assert "API_KEY" not in result.kept


def test_struck_entry_has_reason(env):
    result = strike(env, keys=["API_KEY"])
    entry = next(e for e in result.struck if e.key == "API_KEY")
    assert entry.reason == "explicitly struck"


def test_pattern_entry_has_reason(env):
    result = strike(env, patterns=[r"API"])
    entry = next(e for e in result.struck if e.key == "API_KEY")
    assert entry.reason == "matched pattern"


def test_summary_string(env):
    result = strike(env, keys=["DEBUG"])
    assert "1 key(s) struck" in result.summary()


def test_as_dict_returns_kept(env):
    result = strike(env, keys=["DB_HOST"])
    d = result.as_dict()
    assert "DB_HOST" not in d
    assert "API_KEY" in d


def test_message_on_entry():
    entry = StrikeEntry(key="FOO", value="bar", reason="test reason")
    assert "FOO" in entry.message()
    assert "test reason" in entry.message()
