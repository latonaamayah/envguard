"""Tests for envguard.cli_compare."""
import argparse
import pytest
from pathlib import Path
from envguard.cli_compare import build_compare_parser, run_compare


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(left: str, right: str, no_unchanged: bool = False, strict: bool = False):
    return argparse.Namespace(
        left=left,
        right=right,
        no_unchanged=no_unchanged,
        strict=strict,
    )


def test_run_compare_exits_zero_identical(tmp_env):
    f = _write(tmp_env / ".env", "KEY=value\n")
    args = _args(str(f), str(f))
    assert run_compare(args) == 0


def test_run_compare_exits_zero_with_diff_no_strict(tmp_env):
    left = _write(tmp_env / "left.env", "KEY=old\n")
    right = _write(tmp_env / "right.env", "KEY=new\n")
    args = _args(str(left), str(right), strict=False)
    assert run_compare(args) == 0


def test_run_compare_exits_one_with_diff_strict(tmp_env):
    left = _write(tmp_env / "left.env", "KEY=old\n")
    right = _write(tmp_env / "right.env", "KEY=new\n")
    args = _args(str(left), str(right), strict=True)
    assert run_compare(args) == 1


def test_run_compare_missing_left_exits_two(tmp_env):
    right = _write(tmp_env / "right.env", "KEY=value\n")
    args = _args("/nonexistent/left.env", str(right))
    assert run_compare(args) == 2


def test_run_compare_missing_right_exits_two(tmp_env):
    left = _write(tmp_env / "left.env", "KEY=value\n")
    args = _args(str(left), "/nonexistent/right.env")
    assert run_compare(args) == 2


def test_run_compare_outputs_added_key(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=1\nB=2\n")
    args = _args(str(left), str(right))
    run_compare(args)
    captured = capsys.readouterr()
    assert "[+]" in captured.out
    assert "B" in captured.out


def test_run_compare_outputs_removed_key(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\nB=2\n")
    right = _write(tmp_env / "right.env", "A=1\n")
    args = _args(str(left), str(right))
    run_compare(args)
    captured = capsys.readouterr()
    assert "[-]" in captured.out
    assert "B" in captured.out


def test_run_compare_outputs_summary(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=2\n")
    args = _args(str(left), str(right))
    run_compare(args)
    captured = capsys.readouterr()
    assert "Summary:" in captured.out


def test_build_compare_parser_returns_parser():
    parser = build_compare_parser()
    assert isinstance(parser, argparse.ArgumentParser)
