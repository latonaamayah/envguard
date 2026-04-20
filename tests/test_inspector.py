"""Tests for envguard.inspector."""
import pytest
from envguard.inspector import inspect, InspectResult, InspectEntry


@pytest.fixture()
def env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "DB_PORT": "5432",
        "ENABLE_FEATURE": "true",
        "EMPTY_VAR": "",
        "SPACED_VALUE": "  hello  ",
        "QUOTED_VALUE": '"production"',
    }


def test_returns_inspect_result(env):
    result = inspect(env)
    assert isinstance(result, InspectResult)


def test_entry_count_matches_env(env):
    result = inspect(env)
    assert len(result.entries) == len(env)


def test_has_entries_true(env):
    result = inspect(env)
    assert result.has_entries() is True


def test_has_entries_false_empty():
    result = inspect({})
    assert result.has_entries() is False


def test_sensitive_key_detected(env):
    result = inspect(env)
    assert "DB_PASSWORD" in result.sensitive_keys()


def test_non_sensitive_key_not_flagged(env):
    result = inspect(env)
    assert "DB_HOST" not in result.sensitive_keys()


def test_empty_key_detected(env):
    result = inspect(env)
    assert "EMPTY_VAR" in result.empty_keys()


def test_non_empty_key_not_in_empty(env):
    result = inspect(env)
    assert "DB_HOST" not in result.empty_keys()


def test_numeric_value_detected(env):
    result = inspect(env)
    entry = next(e for e in result.entries if e.key == "DB_PORT")
    assert entry.is_numeric is True


def test_non_numeric_value(env):
    result = inspect(env)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.is_numeric is False


def test_boolean_value_detected(env):
    result = inspect(env)
    entry = next(e for e in result.entries if e.key == "ENABLE_FEATURE")
    assert entry.is_boolean is True


def test_has_whitespace_detected(env):
    result = inspect(env)
    entry = next(e for e in result.entries if e.key == "SPACED_VALUE")
    assert entry.has_whitespace is True


def test_no_whitespace_for_clean_value(env):
    result = inspect(env)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.has_whitespace is False


def test_has_quotes_detected(env):
    result = inspect(env)
    entry = next(e for e in result.entries if e.key == "QUOTED_VALUE")
    assert entry.has_quotes is True


def test_length_correct(env):
    result = inspect(env)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.length == len("localhost")


def test_as_dict_keys_match_env(env):
    result = inspect(env)
    d = result.as_dict()
    assert set(d.keys()) == set(env.keys())


def test_as_dict_entry_has_expected_fields(env):
    result = inspect(env)
    d = result.as_dict()
    entry = d["DB_PORT"]
    assert "length" in entry
    assert "is_empty" in entry
    assert "is_sensitive" in entry
    assert "is_numeric" in entry


def test_summary_contains_key():
    env = {"SECRET_KEY": "abc"}
    result = inspect(env)
    assert "SECRET_KEY" in result.entries[0].summary()
