"""Tests for envguard.comparer."""
import pytest
from envguard.comparer import compare, CompareReport, CompareChange


@pytest.fixture
def left():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_ENV": "development",
        "SECRET_KEY": "old-secret",
    }


@pytest.fixture
def right():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5433",
        "APP_ENV": "production",
        "NEW_KEY": "hello",
    }


def test_returns_compare_report(left, right):
    result = compare(left, right)
    assert isinstance(result, CompareReport)


def test_has_diff_true_when_changes(left, right):
    result = compare(left, right)
    assert result.has_diff() is True


def test_has_diff_false_when_identical():
    env = {"A": "1", "B": "2"}
    result = compare(env, env.copy())
    assert result.has_diff() is False


def test_added_key_detected(left, right):
    result = compare(left, right)
    added_keys = [c.key for c in result.added()]
    assert "NEW_KEY" in added_keys


def test_removed_key_detected(left, right):
    result = compare(left, right)
    removed_keys = [c.key for c in result.removed()]
    assert "SECRET_KEY" in removed_keys


def test_changed_value_detected(left, right):
    result = compare(left, right)
    changed_keys = [c.key for c in result.changed()]
    assert "DB_PORT" in changed_keys
    assert "APP_ENV" in changed_keys


def test_unchanged_value_detected(left, right):
    result = compare(left, right)
    unchanged_keys = [c.key for c in result.unchanged()]
    assert "DB_HOST" in unchanged_keys


def test_exclude_unchanged(left, right):
    result = compare(left, right, include_unchanged=False)
    assert all(c.status != "unchanged" for c in result.changes)


def test_summary_string(left, right):
    result = compare(left, right)
    s = result.summary()
    assert "added=" in s
    assert "removed=" in s
    assert "changed=" in s


def test_change_message_added():
    c = CompareChange("NEW_KEY", None, "hello", "added")
    assert "added" in c.message()
    assert "NEW_KEY" in c.message()


def test_change_message_removed():
    c = CompareChange("OLD_KEY", "bye", None, "removed")
    assert "removed" in c.message()
    assert "bye" in c.message()


def test_change_message_changed():
    c = CompareChange("DB_PORT", "5432", "5433", "changed")
    assert "5432" in c.message()
    assert "5433" in c.message()


def test_all_keys_covered(left, right):
    result = compare(left, right)
    all_keys = set(left) | set(right)
    result_keys = {c.key for c in result.changes}
    assert result_keys == all_keys


def test_empty_envs_produce_no_changes():
    result = compare({}, {})
    assert result.changes == []
    assert result.has_diff() is False
