"""Tests for envguard.duplicates."""
import os
import pytest

from envguard.duplicates import find_duplicates, DuplicateResult


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content, encoding="utf-8")
    return str(path)


# ── single-file tests ──────────────────────────────────────────────────────

def test_no_duplicates_clean_file(tmp_env):
    f = _write(tmp_env / ".env", "FOO=1\nBAR=2\n")
    result = find_duplicates(f)
    assert not result.has_duplicates


def test_single_duplicate_key(tmp_env):
    f = _write(tmp_env / ".env", "FOO=1\nBAR=2\nFOO=3\n")
    result = find_duplicates(f)
    assert result.has_duplicates
    assert len(result.duplicates) == 1
    assert result.duplicates[0].key == "FOO"
    assert result.duplicates[0].count == 2


def test_duplicate_line_numbers_correct(tmp_env):
    f = _write(tmp_env / ".env", "A=1\nB=2\nA=3\nA=4\n")
    result = find_duplicates(f)
    entry = result.duplicates[0]
    line_numbers = [ln for _, ln in entry.occurrences]
    assert line_numbers == [1, 3, 4]


def test_blank_lines_and_comments_ignored(tmp_env):
    content = "# comment\n\nFOO=1\n\n# another\nFOO=2\n"
    f = _write(tmp_env / ".env", content)
    result = find_duplicates(f)
    assert result.has_duplicates
    assert result.duplicates[0].key == "FOO"


def test_no_duplicates_returns_empty_list(tmp_env):
    f = _write(tmp_env / ".env", "X=hello\n")
    result = find_duplicates(f)
    assert result.duplicates == []


# ── multi-file tests ───────────────────────────────────────────────────────

def test_cross_file_duplicate_detected(tmp_env):
    f1 = _write(tmp_env / ".env.base", "SHARED=1\nONLY_A=yes\n")
    f2 = _write(tmp_env / ".env.local", "SHARED=2\nONLY_B=no\n")
    result = find_duplicates(f1, f2)
    assert result.has_duplicates
    keys = [e.key for e in result.duplicates]
    assert "SHARED" in keys


def test_cross_file_unique_keys_no_duplicate(tmp_env):
    f1 = _write(tmp_env / ".env.a", "ALPHA=1\n")
    f2 = _write(tmp_env / ".env.b", "BETA=2\n")
    result = find_duplicates(f1, f2)
    assert not result.has_duplicates


# ── summary tests ──────────────────────────────────────────────────────────

def test_summary_no_duplicates(tmp_env):
    f = _write(tmp_env / ".env", "A=1\n")
    result = find_duplicates(f)
    assert result.summary() == "No duplicate keys found."


def test_summary_contains_key_name(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=a\nDB_HOST=b\n")
    result = find_duplicates(f)
    assert "DB_HOST" in result.summary()
    assert "2x" in result.summary()
