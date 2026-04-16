"""Tests for envguard.formatter."""
import pytest
from envguard.formatter import format_env, FormatChange, FormatResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def lines(*args: str):
    return list(args)


# ---------------------------------------------------------------------------
# FormatResult helpers
# ---------------------------------------------------------------------------

def test_returns_format_result():
    result = format_env(lines("KEY=value"))
    assert isinstance(result, FormatResult)


def test_no_changes_for_already_clean_line():
    result = format_env(lines("KEY=value"))
    assert not result.has_changes


def test_strips_surrounding_whitespace_from_value():
    result = format_env(lines("KEY=  value  "))
    assert result.has_changes
    assert "KEY" in result.changed_keys


def test_removes_double_quotes_from_value():
    result = format_env(lines('KEY="hello"'))
    assert result.has_changes
    assert result.formatted["KEY"] == "hello"


def test_removes_single_quotes_from_value():
    result = format_env(lines("KEY='world'"))
    assert result.has_changes
    assert result.formatted["KEY"] == "world"


def test_does_not_remove_mismatched_quotes():
    result = format_env(lines("KEY='hello\""))
    # mismatched — value kept as-is
    assert result.formatted["KEY"] == "'hello\""


def test_strips_whitespace_around_key():
    result = format_env(lines("  KEY  =value"))
    assert "KEY" in result.formatted


def test_blank_lines_ignored():
    result = format_env(lines("", "   ", "KEY=val"))
    assert len(result.changes) == 1


def test_comment_lines_ignored():
    result = format_env(lines("# this is a comment", "KEY=val"))
    assert len(result.changes) == 1


def test_lines_without_equals_ignored():
    result = format_env(lines("JUSTKEY", "KEY=val"))
    assert len(result.changes) == 1


def test_multiple_keys_tracked():
    result = format_env(lines("A=1", "B=2", "C=3"))
    assert len(result.changes) == 3


def test_changed_keys_only_includes_modified():
    result = format_env(lines("A=1", 'B="quoted"'))
    assert "A" not in result.changed_keys
    assert "B" in result.changed_keys


def test_summary_no_changes():
    result = format_env(lines("KEY=value"))
    assert "already" in result.summary()


def test_summary_with_changes():
    result = format_env(lines('KEY="value"'))
    assert "reformatted" in result.summary()


def test_format_change_changed_property():
    change = FormatChange(key="K", original_line="K=\"v\"", formatted_line="K=v")
    assert change.changed


def test_format_change_not_changed():
    change = FormatChange(key="K", original_line="K=v", formatted_line="K=v")
    assert not change.changed
