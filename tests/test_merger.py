"""Tests for envguard.merger module."""
import pytest
from pathlib import Path

from envguard.merger import merge, MergeResult, MergeConflict


@pytest.fixture
def tmp_env(tmp_path):
    def _write(filename: str, content: str) -> str:
        p = tmp_path / filename
        p.write_text(content)
        return str(p)
    return _write


def test_merge_single_file(tmp_env):
    f = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    result = merge([f])
    assert result.merged == {"FOO": "bar", "BAZ": "qux"}
    assert not result.has_conflicts


def test_merge_two_files_no_overlap(tmp_env):
    f1 = tmp_env("a.env", "FOO=bar\n")
    f2 = tmp_env("b.env", "BAZ=qux\n")
    result = merge([f1, f2])
    assert result.merged["FOO"] == "bar"
    assert result.merged["BAZ"] == "qux"
    assert not result.has_conflicts


def test_merge_conflict_last_wins(tmp_env):
    f1 = tmp_env("a.env", "FOO=first\n")
    f2 = tmp_env("b.env", "FOO=second\n")
    result = merge([f1, f2], override=True)
    assert result.merged["FOO"] == "second"
    assert result.has_conflicts
    assert len(result.conflicts) == 1
    assert result.conflicts[0].key == "FOO"
    assert result.conflicts[0].winning_value == "second"


def test_merge_conflict_first_wins_when_no_override(tmp_env):
    f1 = tmp_env("a.env", "FOO=first\n")
    f2 = tmp_env("b.env", "FOO=second\n")
    result = merge([f1, f2], override=False)
    assert result.merged["FOO"] == "first"


def test_merge_tracks_sources(tmp_env):
    f1 = tmp_env("a.env", "A=1\n")
    f2 = tmp_env("b.env", "B=2\n")
    result = merge([f1, f2])
    assert len(result.sources) == 2


def test_merge_summary_no_conflicts(tmp_env):
    f = tmp_env("a.env", "X=1\nY=2\n")
    result = merge([f])
    summary = result.summary()
    assert "1 source" in summary
    assert "2 variable" in summary


def test_merge_summary_with_conflicts(tmp_env):
    f1 = tmp_env("a.env", "FOO=1\n")
    f2 = tmp_env("b.env", "FOO=2\n")
    result = merge([f1, f2])
    summary = result.summary()
    assert "conflict" in summary


def test_merge_empty_files(tmp_env):
    f1 = tmp_env("a.env", "")
    f2 = tmp_env("b.env", "")
    result = merge([f1, f2])
    assert result.merged == {}
    assert not result.has_conflicts
