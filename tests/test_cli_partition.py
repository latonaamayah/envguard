"""Tests for envguard.cli_partition."""
import json
import pytest
from pathlib import Path
from envguard.cli_partition import build_partition_parser, run_partition


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(parser, *argv):
    return parser.parse_args(list(argv))


def test_run_partition_exits_zero(tmp_env):
    env_file = _write(tmp_env / ".env", "DB_HOST=localhost\nAPP_ENV=prod\n")
    parser = build_partition_parser()
    args = _args(parser, str(env_file))
    assert run_partition(args) == 0


def test_run_partition_missing_file_exits_two(tmp_env):
    parser = build_partition_parser()
    args = _args(parser, str(tmp_env / "missing.env"))
    assert run_partition(args) == 2


def test_run_partition_text_output(tmp_env, capsys):
    env_file = _write(tmp_env / ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=prod\n")
    parser = build_partition_parser()
    args = _args(parser, str(env_file), "--rule", "database=^DB_")
    run_partition(args)
    out = capsys.readouterr().out
    assert "database" in out
    assert "DB_HOST" in out


def test_run_partition_json_output(tmp_env, capsys):
    env_file = _write(tmp_env / ".env", "DB_HOST=localhost\nAPP_ENV=prod\n")
    parser = build_partition_parser()
    args = _args(parser, str(env_file), "--rule", "database=^DB_", "--format", "json")
    run_partition(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "database" in data
    assert data["database"]["DB_HOST"] == "localhost"


def test_run_partition_custom_default_bucket(tmp_env, capsys):
    env_file = _write(tmp_env / ".env", "LOG_LEVEL=info\n")
    parser = build_partition_parser()
    args = _args(parser, str(env_file), "--default-bucket", "misc")
    run_partition(args)
    out = capsys.readouterr().out
    assert "misc" in out


def test_run_partition_invalid_rule_exits_two(tmp_env):
    env_file = _write(tmp_env / ".env", "KEY=val\n")
    parser = build_partition_parser()
    args = _args(parser, str(env_file), "--rule", "badformat")
    assert run_partition(args) == 2


def test_run_partition_multiple_rules(tmp_env, capsys):
    content = "DB_HOST=h\nAWS_KEY=k\nAPP_ENV=p\n"
    env_file = _write(tmp_env / ".env", content)
    parser = build_partition_parser()
    args = _args(
        parser,
        str(env_file),
        "--rule", "database=^DB_",
        "--rule", "cloud=^AWS_",
        "--format", "json",
    )
    run_partition(args)
    data = json.loads(capsys.readouterr().out)
    assert "database" in data
    assert "cloud" in data
    assert "default" in data
