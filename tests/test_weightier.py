"""Tests for envguard.weightier module."""
import pytest
from envguard.weightier import WeightEntry, WeightResult, weight


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "EMPTY_VAR": "",
        "LONG_VALUE": "x" * 80,
    }


def test_returns_weight_result(env):
    result = weight(env)
    assert isinstance(result, WeightResult)


def test_entry_count_matches_env(env):
    result = weight(env)
    assert len(result.entries) == len(env)


def test_has_entries_true(env):
    result = weight(env)
    assert result.has_entries() is True


def test_has_entries_false_empty():
    result = weight({})
    assert result.has_entries() is False


def test_sensitive_key_has_higher_weight(env):
    result = weight(env)
    by_key = {e.key: e.weight for e in result.entries}
    assert by_key["DB_PASSWORD"] > by_key["APP_NAME"]


def test_empty_value_reduces_weight(env):
    result = weight(env)
    by_key = {e.key: e.weight for e in result.entries}
    assert by_key["EMPTY_VAR"] < by_key["APP_NAME"]


def test_long_value_increases_weight(env):
    result = weight(env)
    by_key = {e.key: e.weight for e in result.entries}
    assert by_key["LONG_VALUE"] > by_key["APP_NAME"]


def test_explicit_rule_overrides_computed(env):
    result = weight(env, rules={"APP_NAME": 999})
    by_key = {e.key: e.weight for e in result.entries}
    assert by_key["APP_NAME"] == 999


def test_explicit_rule_reason_is_explicit(env):
    result = weight(env, rules={"APP_NAME": 999})
    entry = next(e for e in result.entries if e.key == "APP_NAME")
    assert entry.reason == "explicit rule"


def test_top_returns_highest_weighted(env):
    result = weight(env)
    top = result.top(2)
    assert len(top) == 2
    assert top[0].weight >= top[1].weight


def test_bottom_returns_lowest_weighted(env):
    result = weight(env)
    bottom = result.bottom(2)
    assert len(bottom) == 2
    assert bottom[0].weight <= bottom[1].weight


def test_as_dict_returns_key_weight_map(env):
    result = weight(env)
    d = result.as_dict()
    assert isinstance(d, dict)
    assert set(d.keys()) == set(env.keys())
    for v in d.values():
        assert isinstance(v, int)


def test_summary_contains_entry_count(env):
    result = weight(env)
    s = result.summary()
    assert str(len(env)) in s


def test_summary_empty_env():
    result = weight({})
    assert "No entries" in result.summary()


def test_str_representation(env):
    result = weight(env)
    entry = result.entries[0]
    s = str(entry)
    assert entry.key in s
    assert "weight=" in s
