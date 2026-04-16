"""Tests for envguard.cli_format."""
import argparse
from pathlib import Path

import pytest

from envguard.cli_format import build_format_parser, run_format


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path: Path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content, encoding="utf-8")
    return p


def _args(env_file: str, check: bool = False, in_place: bool = False) -> argparse.Namespace:
    return argparse.Namespace(env_file=env_file, check=check, in_place=in_place)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_run_format_exits_zero_clean_file(tmp_env):
    f = _write(tmp_env, ".env", "KEY=value\n")
    assert run_format(_args(str(f))) == 0


def test_run_format_missing_file_exits_two(tmp_env):
    assert run_format(_args(str(tmp_env / "missing.env"))) == 2


def test_run_format_check_no_changes_exits_zero(tmp_env):
    f = _write(tmp_env, ".env", "KEY=value\n")
    assert run_format(_args(str(f), check=True)) == 0


def test_run_format_check_with_changes_exits_one(tmp_env):
    f = _write(tmp_env, ".env", 'KEY="value"\n')
    assert run_format(_args(str(f), check=True)) == 1


def test_run_format_in_place_rewrites_file(tmp_env):
    f = _write(tmp_env, ".env", 'KEY="hello"\n')
    run_format(_args(str(f), in_place=True))
    content = f.read_text(encoding="utf-8")
    assert 'KEY=hello' in content
    assert '"' not in content


def test_run_format_stdout_output(tmp_env, capsys):
    f = _write(tmp_env, ".env", 'A="one"\n')
    run_format(_args(str(f)))
    captured = capsys.readouterr()
    assert "A=one" in captured.out


def test_run_format_preserves_comments(tmp_env):
    f = _write(tmp_env, ".env", "# comment\nKEY=val\n")
    run_format(_args(str(f), in_place=True))
    content = f.read_text(encoding="utf-8")
    assert "# comment" in content


def test_build_format_parser_returns_parser():
    parser = build_format_parser()
    assert isinstance(parser, argparse.ArgumentParser)
