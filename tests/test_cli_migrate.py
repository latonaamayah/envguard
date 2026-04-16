import argparse
import pytest
from pathlib import Path
from envguard.cli_migrate import run_migrate, build_migrate_parser


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def _args(env_file, rename=None, keep_old=False, strict=False):
    return argparse.Namespace(
        env_file=str(env_file),
        rename=rename or [],
        keep_old=keep_old,
        strict=strict,
    )


def test_run_migrate_exits_zero(tmp_env):
    _write(tmp_env, "DB_HOST=localhost\nAPP_PORT=8080\n")
    code = run_migrate(_args(tmp_env, rename=["DB_HOST=DATABASE_HOST"]))
    assert code == 0


def test_run_migrate_missing_file_exits_two(tmp_path):
    code = run_migrate(_args(tmp_path / "missing.env"))
    assert code == 2


def test_run_migrate_outputs_new_key(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\n")
    run_migrate(_args(tmp_env, rename=["DB_HOST=DATABASE_HOST"]))
    out = capsys.readouterr().out
    assert "DATABASE_HOST=localhost" in out


def test_run_migrate_removes_old_key(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\n")
    run_migrate(_args(tmp_env, rename=["DB_HOST=DATABASE_HOST"]))
    out = capsys.readouterr().out
    assert "DB_HOST=" not in out


def test_run_migrate_keep_old_retains_key(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\n")
    run_migrate(_args(tmp_env, rename=["DB_HOST=DATABASE_HOST"], keep_old=True))
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "DATABASE_HOST=localhost" in out


def test_run_migrate_strict_exits_one_on_missing(tmp_env):
    _write(tmp_env, "APP_PORT=8080\n")
    code = run_migrate(_args(tmp_env, rename=["MISSING_KEY=NEW_KEY"], strict=True))
    assert code == 1


def test_run_migrate_no_rename_passthrough(tmp_env, capsys):
    _write(tmp_env, "APP_PORT=8080\n")
    run_migrate(_args(tmp_env))
    out = capsys.readouterr().out
    assert "APP_PORT=8080" in out
