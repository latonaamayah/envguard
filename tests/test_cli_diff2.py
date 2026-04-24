"""Tests for envguard.cli_diff2."""
import argparse
import pytest
from envguard.cli_diff2 import build_diff2_parser, run_diff2


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(left: str, right: str, no_unchanged: bool = False, strict: bool = False):
    return argparse.Namespace(
        left=left,
        right=right,
        no_unchanged=no_unchanged,
        strict=strict,
    )


def test_run_diff2_exits_zero_identical(tmp_env):
    content = "DB_HOST=localhost\nDB_PORT=5432\n"
    left = _write(tmp_env / "left.env", content)
    right = _write(tmp_env / "right.env", content)
    assert run_diff2(_args(left, right)) == 0


def test_run_diff2_exits_zero_with_changes_no_strict(tmp_env):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=2\n")
    assert run_diff2(_args(left, right)) == 0


def test_run_diff2_exits_one_with_changes_strict(tmp_env):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=2\n")
    assert run_diff2(_args(left, right, strict=True)) == 1


def test_run_diff2_exits_two_missing_left(tmp_env):
    right = _write(tmp_env / "right.env", "A=1\n")
    assert run_diff2(_args("/nonexistent.env", right)) == 2


def test_run_diff2_exits_two_missing_right(tmp_env):
    left = _write(tmp_env / "left.env", "A=1\n")
    assert run_diff2(_args(left, "/nonexistent.env")) == 2


def test_run_diff2_outputs_added_key(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=1\nB=2\n")
    run_diff2(_args(left, right))
    out = capsys.readouterr().out
    assert "+ B" in out


def test_run_diff2_outputs_removed_key(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\nB=2\n")
    right = _write(tmp_env / "right.env", "A=1\n")
    run_diff2(_args(left, right))
    out = capsys.readouterr().out
    assert "- B" in out


def test_run_diff2_no_unchanged_suppresses_unchanged(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\nB=2\n")
    right = _write(tmp_env / "right.env", "A=1\nB=3\n")
    run_diff2(_args(left, right, no_unchanged=True))
    out = capsys.readouterr().out
    assert "A" not in out
    assert "B" in out


def test_run_diff2_summary_in_output(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=2\n")
    run_diff2(_args(left, right))
    out = capsys.readouterr().out
    assert "+" in out
    assert "-" in out
    assert "~" in out
