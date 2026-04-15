"""Tests for envguard.cli_rename."""
import argparse
import os
import pytest

from envguard.cli_rename import build_rename_parser, run_rename


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(env_file: str, renames, strict=False, quiet=True):
    ns = argparse.Namespace(
        env_file=env_file,
        renames=renames,
        strict=strict,
        quiet=quiet,
    )
    return ns


def test_run_rename_exits_zero(tmp_env):
    path = _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\n")
    args = _args(path, ["DB_HOST:DATABASE_HOST"])
    assert run_rename(args) == 0


def test_run_rename_outputs_renamed_key(tmp_env, capsys):
    path = _write(tmp_env, "DB_HOST=localhost\n")
    args = _args(path, ["DB_HOST:DATABASE_HOST"])
    run_rename(args)
    captured = capsys.readouterr()
    assert "DATABASE_HOST=localhost" in captured.out
    assert "DB_HOST" not in captured.out


def test_run_rename_missing_file_exits_two(tmp_path):
    args = _args(str(tmp_path / "missing.env"), ["A:B"])
    assert run_rename(args) == 2


def test_run_rename_invalid_spec_exits_two(tmp_env):
    path = _write(tmp_env, "A=1\n")
    args = _args(path, ["BADSPEC"])
    assert run_rename(args) == 2


def test_run_rename_strict_exits_one_on_missing_key(tmp_env):
    path = _write(tmp_env, "A=1\n")
    args = _args(path, ["GHOST:PHANTOM"], strict=True)
    assert run_rename(args) == 1


def test_run_rename_non_strict_exits_zero_on_missing_key(tmp_env):
    path = _write(tmp_env, "A=1\n")
    args = _args(path, ["GHOST:PHANTOM"], strict=False)
    assert run_rename(args) == 0


def test_run_rename_multiple_renames(tmp_env, capsys):
    path = _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\n")
    args = _args(path, ["DB_HOST:DATABASE_HOST", "DB_PORT:DATABASE_PORT"])
    code = run_rename(args)
    captured = capsys.readouterr()
    assert code == 0
    assert "DATABASE_HOST=localhost" in captured.out
    assert "DATABASE_PORT=5432" in captured.out
