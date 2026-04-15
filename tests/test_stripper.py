"""Tests for envguard.stripper."""
from __future__ import annotations

import pytest

from envguard.stripper import StripResult, strip


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def lines(*args: str):
    """Return list of lines with newlines appended."""
    return [f"{a}\n" for a in args]


# ---------------------------------------------------------------------------
# strip() behaviour
# ---------------------------------------------------------------------------

def test_no_changes_for_clean_env():
    result = strip(lines("KEY=value", "PORT=8080"))
    assert result.stripped == {"KEY": "value", "PORT": "8080"}
    assert not result.has_changes()


def test_blank_lines_removed():
    result = strip(lines("KEY=value", "", "   ", "PORT=8080"))
    assert result.removed_blanks == 2
    assert "KEY" in result.stripped
    assert "PORT" in result.stripped


def test_comment_lines_removed():
    result = strip(lines("# This is a comment", "KEY=value"))
    assert len(result.removed_comments) == 1
    assert result.removed_comments[0] == "# This is a comment"
    assert "KEY" in result.stripped


def test_inline_comment_stripped_from_value():
    result = strip(lines("KEY=hello # world"))
    assert result.stripped["KEY"] == "hello"
    assert len(result.removed_inline_comments) == 1
    assert "KEY" in result.removed_inline_comments[0]


def test_quoted_value_preserved():
    result = strip(lines('KEY="hello world"'))
    assert result.stripped["KEY"] == "hello world"


def test_quoted_value_with_inline_comment():
    result = strip(lines('KEY="hello" # trailing comment'))
    assert result.stripped["KEY"] == "hello"
    assert len(result.removed_inline_comments) == 1


def test_single_quoted_value():
    result = strip(lines("KEY='my value'"))
    assert result.stripped["KEY"] == "my value"


def test_has_changes_when_comments_present():
    result = strip(lines("# comment", "KEY=val"))
    assert result.has_changes()


def test_has_changes_false_for_clean():
    result = strip(lines("A=1", "B=2"))
    assert not result.has_changes()


def test_summary_nothing_stripped():
    result = strip(lines("A=1"))
    assert "clean" in result.summary()


def test_summary_with_comment_and_blank():
    result = strip(lines("# comment", "", "A=1"))
    summary = result.summary()
    assert "comment" in summary
    assert "blank" in summary


def test_summary_with_inline_comment():
    result = strip(lines("A=hello # note"))
    assert "inline" in result.summary()


def test_multiple_vars_all_present():
    raw = lines("DB_HOST=localhost", "DB_PORT=5432", "DB_NAME=mydb")
    result = strip(raw)
    assert len(result.stripped) == 3


def test_invalid_line_without_equals_skipped():
    result = strip(lines("NOTANASSIGNMENT", "KEY=value"))
    assert "NOTANASSIGNMENT" not in result.stripped
    assert "KEY" in result.stripped
