import json
import pytest
from pathlib import Path
from envguard.cli_freeze import run_freeze, build_freeze_parser


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> str:
    path.write_text(content)
    return str(path)


@pytest.fixture
def _args(tmp_env):
    def factory(**kwargs):
        parser = build_freeze_parser()
        env_file = _write(tmp_env / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
        defaults = {
            "env_file": env_file,
            "output": str(tmp_env / ".env.freeze"),
            "check": False,
            "freeze_file": str(tmp_env / ".env.freeze"),
            "keys": None,
        }
        defaults.update(kwargs)
        return argparse.Namespace(**defaults)
    return factory


import argparse


def test_run_freeze_exits_zero(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
    freeze_path = str(tmp_env / ".env.freeze")
    parser = build_freeze_parser()
    args = parser.parse_args([env_path, "--output", freeze_path])
    assert run_freeze(args) == 0


def test_run_freeze_creates_file(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
    freeze_path = str(tmp_env / ".env.freeze")
    parser = build_freeze_parser()
    args = parser.parse_args([env_path, "--output", freeze_path])
    run_freeze(args)
    assert Path(freeze_path).exists()


def test_run_freeze_creates_valid_json(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
    freeze_path = str(tmp_env / ".env.freeze")
    parser = build_freeze_parser()
    args = parser.parse_args([env_path, "--output", freeze_path])
    run_freeze(args)
    data = json.loads(Path(freeze_path).read_text())
    assert "frozen" in data


def test_run_freeze_check_no_drift(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
    freeze_path = str(tmp_env / ".env.freeze")
    parser = build_freeze_parser()
    args_save = parser.parse_args([env_path, "--output", freeze_path])
    run_freeze(args_save)
    args_check = parser.parse_args(
        [env_path, "--check", "--freeze-file", freeze_path]
    )
    assert run_freeze(args_check) == 0


def test_run_freeze_check_detects_drift(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
    freeze_path = str(tmp_env / ".env.freeze")
    parser = build_freeze_parser()
    args_save = parser.parse_args([env_path, "--output", freeze_path])
    run_freeze(args_save)
    _write(tmp_env / ".env", "DB_HOST=newhost\nAPI_KEY=secret\n")
    args_check = parser.parse_args(
        [env_path, "--check", "--freeze-file", freeze_path]
    )
    assert run_freeze(args_check) == 1


def test_run_freeze_missing_env_file_exits_two(tmp_env):
    freeze_path = str(tmp_env / ".env.freeze")
    parser = build_freeze_parser()
    args = parser.parse_args(
        [str(tmp_env / "nonexistent.env"), "--output", freeze_path]
    )
    assert run_freeze(args) == 2


def test_run_freeze_check_missing_freeze_file_exits_two(tmp_env):
    env_path = _write(tmp_env / ".env", "DB_HOST=localhost\n")
    parser = build_freeze_parser()
    args = parser.parse_args(
        [env_path, "--check", "--freeze-file", str(tmp_env / "missing.freeze")]
    )
    assert run_freeze(args) == 2
