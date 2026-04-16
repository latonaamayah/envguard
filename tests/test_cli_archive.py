import json
import pytest
from pathlib import Path
from argparse import Namespace
from envguard.cli_archive import run_archive


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(tmp_path, command, **kwargs):
    base = {
        "command": command,
        "archive": str(tmp_path / ".envarchive.json"),
    }
    base.update(kwargs)
    return Namespace(**base)


def test_run_save_exits_zero(tmp_env):
    env_file = _write(tmp_env / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    args = _args(tmp_env, "save", env_file=str(env_file), label="v1")
    assert run_archive(args) == 0


def test_run_save_creates_archive_file(tmp_env):
    env_file = _write(tmp_env / ".env", "APP_ENV=prod\n")
    args = _args(tmp_env, "save", env_file=str(env_file), label="release-1")
    run_archive(args)
    archive_path = tmp_env / ".envarchive.json"
    assert archive_path.exists()
    data = json.loads(archive_path.read_text())
    assert data[0]["label"] == "release-1"


def test_run_save_missing_env_file_exits_two(tmp_env):
    args = _args(tmp_env, "save", env_file="/nonexistent/.env", label="v1")
    assert run_archive(args) == 2


def test_run_list_exits_zero(tmp_env):
    args = _args(tmp_env, "list")
    assert run_archive(args) == 0


def test_run_list_shows_labels(tmp_env, capsys):
    env_file = _write(tmp_env / ".env", "X=1\n")
    save_args = _args(tmp_env, "save", env_file=str(env_file), label="alpha")
    run_archive(save_args)
    list_args = _args(tmp_env, "list")
    run_archive(list_args)
    out = capsys.readouterr().out
    assert "alpha" in out


def test_run_show_existing_label(tmp_env, capsys):
    env_file = _write(tmp_env / ".env", "KEY=value\n")
    run_archive(_args(tmp_env, "save", env_file=str(env_file), label="v2"))
    run_archive(_args(tmp_env, "show", label="v2"))
    out = capsys.readouterr().out
    assert "KEY=value" in out


def test_run_show_missing_label_exits_one(tmp_env):
    args = _args(tmp_env, "show", label="ghost")
    assert run_archive(args) == 1
