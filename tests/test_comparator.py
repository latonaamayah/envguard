"""Tests for envguard.comparator."""
import pytest
from envguard.comparator import compare, CompareResult, CompareEntry


LEFT = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
RIGHT = {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "info"}


def test_no_differences_when_identical():
    result = compare({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    assert not result.has_differences


def test_changed_value_detected():
    result = compare(LEFT, RIGHT)
    changed_keys = [e.key for e in result.changed]
    assert "HOST" in changed_keys


def test_equal_value_not_in_changed():
    result = compare(LEFT, RIGHT)
    changed_keys = [e.key for e in result.changed]
    assert "PORT" not in changed_keys


def test_left_only_detected():
    result = compare(LEFT, RIGHT)
    left_only_keys = [e.key for e in result.left_only]
    assert "DEBUG" in left_only_keys


def test_right_only_detected():
    result = compare(LEFT, RIGHT)
    right_only_keys = [e.key for e in result.right_only]
    assert "LOG_LEVEL" in right_only_keys


def test_left_only_has_none_right_value():
    result = compare(LEFT, RIGHT)
    entry = next(e for e in result.left_only if e.key == "DEBUG")
    assert entry.right_value is None
    assert entry.left_value == "true"


def test_right_only_has_none_left_value():
    result = compare(LEFT, RIGHT)
    entry = next(e for e in result.right_only if e.key == "LOG_LEVEL")
    assert entry.left_value is None
    assert entry.right_value == "info"


def test_has_differences_true_when_changes_exist():
    result = compare(LEFT, RIGHT)
    assert result.has_differences


def test_summary_format():
    result = compare(LEFT, RIGHT)
    summary = result.summary()
    assert "changed" in summary
    assert "left-only" in summary
    assert "right-only" in summary


def test_file_labels_stored():
    result = compare({}, {}, left_file=".env.dev", right_file=".env.prod")
    assert result.left_file == ".env.dev"
    assert result.right_file == ".env.prod"


def test_empty_envs_produce_no_entries():
    result = compare({}, {})
    assert result.entries == []
    assert not result.has_differences


def test_all_keys_present_in_entries():
    result = compare(LEFT, RIGHT)
    entry_keys = {e.key for e in result.entries}
    assert entry_keys == set(LEFT) | set(RIGHT)
