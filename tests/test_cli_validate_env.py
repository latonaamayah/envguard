"""Tests for envguard.cli_validate_env."""
import argparse
import pytest
from envguard.cli_validate_env import run_validate_env


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(env_file, keys=None, max_length=512, strict=False):
    return argparse.Namespace(
        env_file=env_file,
        keys=keys,
        max_length=max_length,
        strict=strict,
    )


def test_run_validate_env_exits_zero_clean(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    assert run_validate_env(_args(f)) == 0


def test_run_validate_env_missing_file_exits_two(tmp_env):
    assert run_validate_env(_args(str(tmp_env / "missing.env"))) == 2


def test_run_validate_env_empty_value_no_strict_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "EMPTY=\n")
    assert run_validate_env(_args(f, strict=False)) == 0


def test_run_validate_env_empty_value_strict_exits_one(tmp_env):
    f = _write(tmp_env / ".env", "EMPTY=\n")
    assert run_validate_env(_args(f, strict=True)) == 1


def test_run_validate_env_keys_filter_skips_bad_key(tmp_env):
    f = _write(tmp_env / ".env", "GOOD=ok\nBAD=\n")
    assert run_validate_env(_args(f, keys=["GOOD"], strict=True)) == 0


def test_run_validate_env_custom_max_length_triggers_violation(tmp_env):
    f = _write(tmp_env / ".env", "LONG=" + "x" * 20 + "\n")
    assert run_validate_env(_args(f, max_length=5, strict=True)) == 1


def test_run_validate_env_custom_max_length_passes(tmp_env):
    f = _write(tmp_env / ".env", "SHORT=hi\n")
    assert run_validate_env(_args(f, max_length=100, strict=True)) == 0
