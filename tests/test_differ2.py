"""Tests for envguard.differ2 structural diff."""
import pytest
from envguard.differ2 import struct_diff, StructDiffResult, StructDiffEntry


@pytest.fixture
def left():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_SECRET": "old-secret",
        "APP_ENV": "staging",
    }


@pytest.fixture
def right():
    return {
        "DB_HOST": "prod.db.example.com",
        "DB_PORT": "5432",
        "API_SECRET": "new-secret",
        "LOG_LEVEL": "info",
    }


def test_returns_struct_diff_result(left, right):
    result = struct_diff(left, right)
    assert isinstance(result, StructDiffResult)


def test_entry_count_is_union_of_keys(left, right):
    result = struct_diff(left, right)
    expected = len(set(left) | set(right))
    assert len(result.entries) == expected


def test_has_changes_true_when_diffs(left, right):
    result = struct_diff(left, right)
    assert result.has_changes is True


def test_has_changes_false_when_identical():
    env = {"A": "1", "B": "2"}
    result = struct_diff(env, env.copy())
    assert result.has_changes is False


def test_added_key_detected(left, right):
    result = struct_diff(left, right)
    added_keys = [e.key for e in result.added]
    assert "LOG_LEVEL" in added_keys


def test_removed_key_detected(left, right):
    result = struct_diff(left, right)
    removed_keys = [e.key for e in result.removed]
    assert "APP_ENV" in removed_keys


def test_changed_value_detected(left, right):
    result = struct_diff(left, right)
    changed_keys = [e.key for e in result.changed]
    assert "DB_HOST" in changed_keys


def test_unchanged_value_not_in_changed(left, right):
    result = struct_diff(left, right)
    changed_keys = [e.key for e in result.changed]
    assert "DB_PORT" not in changed_keys


def test_sensitive_key_masked_in_message(left, right):
    result = struct_diff(left, right)
    entry = next(e for e in result.entries if e.key == "API_SECRET")
    assert entry.is_sensitive is True
    assert "***" in entry.message
    assert "old-secret" not in entry.message


def test_non_sensitive_key_shows_value(left, right):
    result = struct_diff(left, right)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.is_sensitive is False
    assert "localhost" in entry.message


def test_summary_format(left, right):
    result = struct_diff(left, right)
    s = result.summary()
    assert "+" in s
    assert "-" in s
    assert "~" in s


def test_empty_left_all_added():
    result = struct_diff({}, {"A": "1", "B": "2"})
    assert len(result.added) == 2
    assert len(result.removed) == 0


def test_empty_right_all_removed():
    result = struct_diff({"A": "1", "B": "2"}, {})
    assert len(result.removed) == 2
    assert len(result.added) == 0


def test_keys_sorted_in_entries():
    left = {"Z": "1", "A": "2", "M": "3"}
    right = {"Z": "1", "A": "2", "M": "3"}
    result = struct_diff(left, right)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
