"""Tests for envguard.cli_pin."""
import json
import pytest
from envguard.cli_pin import run_pin


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content):
    path.write_text(content)
    return str(path)


def _args(command, env_file, **kwargs):
    import argparse
    ns = argparse.Namespace(command=command, env_file=env_file)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_run_pin_save_exits_zero(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    pin_path = str(tmp_env / ".env.pin")
    args = _args("save", env_path, output=pin_path)
    assert run_pin(args) == 0


def test_run_pin_save_creates_file(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\n")
    pin_path = str(tmp_env / ".env.pin")
    args = _args("save", env_path, output=pin_path)
    run_pin(args)
    assert (tmp_env / ".env.pin").exists()


def test_run_pin_save_valid_json(tmp_env):
    env_path = _write(tmp_env / ".env", "KEY=value\n")
    pin_path = str(tmp_env / ".env.pin")
    args = _args("save", env_path, output=pin_path)
    run_pin(args)
    with open(pin_path) as f:
        data = json.load(f)
    assert "KEY" in data


def test_run_pin_check_no_drift_exits_zero(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\n")
    pin_path = str(tmp_env / ".env.pin")
    _args_save = _args("save", env_path, output=pin_path)
    run_pin(_args_save)
    args = _args("check", env_path, pin=pin_path)
    assert run_pin(args) == 0


def test_run_pin_check_drift_exits_one(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\n")
    pin_path = str(tmp_env / ".env.pin")
    _args_save = _args("save", env_path, output=pin_path)
    run_pin(_args_save)
    _write(tmp_env / ".env", "DB_HOST=remotehost\n")
    args = _args("check", env_path, pin=pin_path)
    assert run_pin(args) == 1


def test_run_pin_missing_env_file_exits_two(tmp_env):
    args = _args("save", str(tmp_env / "missing.env"), output=str(tmp_env / ".env.pin"))
    assert run_pin(args) == 2


def test_run_pin_check_missing_pin_file_exits_two(tmp_env):
    env_path = _write(tmp_env / ".env", "KEY=val\n")
    args = _args("check", env_path, pin=str(tmp_env / "missing.pin"))
    assert run_pin(args) == 2
