"""Tests for envguard.normalizer."""
import pytest
from envguard.normalizer import normalize, NormalizeResult, NormalizeChange


def test_no_changes_for_clean_values():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = normalize(env)
    assert result.variables == env
    assert not result.has_changes


def test_strips_surrounding_whitespace():
    env = {"KEY": "  value  "}
    result = normalize(env)
    assert result.variables["KEY"] == "value"
    assert result.has_changes
    assert any("whitespace" in c.reason for c in result.changes)


def test_removes_double_quotes():
    env = {"KEY": '"hello"'}
    result = normalize(env)
    assert result.variables["KEY"] == "hello"
    assert result.has_changes
    assert any("quotes" in c.reason for c in result.changes)


def test_removes_single_quotes():
    env = {"KEY": "'world'"}
    result = normalize(env)
    assert result.variables["KEY"] == "world"
    assert result.has_changes


def test_does_not_remove_mismatched_quotes():
    env = {"KEY": "'mismatched\""}
    result = normalize(env)
    assert result.variables["KEY"] == "'mismatched\""
    assert not result.has_changes


def test_lowercases_true():
    env = {"FLAG": "True"}
    result = normalize(env)
    assert result.variables["FLAG"] == "true"
    assert result.has_changes
    assert any("boolean" in c.reason for c in result.changes)


def test_lowercases_false():
    env = {"FLAG": "FALSE"}
    result = normalize(env)
    assert result.variables["FLAG"] == "false"


def test_lowercases_yes_and_no():
    env = {"A": "YES", "B": "No"}
    result = normalize(env)
    assert result.variables["A"] == "yes"
    assert result.variables["B"] == "no"


def test_already_lowercase_boolean_no_change():
    env = {"FLAG": "true"}
    result = normalize(env)
    assert not result.has_changes


def test_multiple_keys_independent():
    env = {"A": "  clean  ", "B": "untouched"}
    result = normalize(env)
    assert result.variables["A"] == "clean"
    assert result.variables["B"] == "untouched"
    assert len(result.changes) == 1
    assert result.changes[0].key == "A"


def test_summary_no_changes():
    result = normalize({"X": "ok"})
    assert "No normalization" in result.summary()


def test_summary_with_changes():
    result = normalize({"FLAG": "True"})
    summary = result.summary()
    assert "1 change(s)" in summary
    assert "FLAG" in summary
