"""Tests for envguard.cli_group."""
import argparse
import pytest
from envguard.cli_group import build_group_parser, run_group


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(env_file, separator="_", min_group_size=1, show_ungrouped=False):
    return argparse.Namespace(
        env_file=env_file,
        separator=separator,
        min_group_size=min_group_size,
        show_ungrouped=show_ungrouped,
    )


def test_run_group_exits_zero(tmp_env):
    path = _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\n")
    assert run_group(_args(path)) == 0


def test_run_group_missing_file_exits_two():
    assert run_group(_args("/nonexistent/.env")) == 2


def test_run_group_outputs_group_name(tmp_env, capsys):
    path = _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\n")
    run_group(_args(path))
    captured = capsys.readouterr()
    assert "DB" in captured.out


def test_run_group_outputs_variable_keys(tmp_env, capsys):
    path = _write(tmp_env, "AWS_KEY=abc\nAWS_SECRET=xyz\n")
    run_group(_args(path))
    captured = capsys.readouterr()
    assert "AWS_KEY" in captured.out
    assert "AWS_SECRET" in captured.out


def test_run_group_show_ungrouped(tmp_env, capsys):
    path = _write(tmp_env, "DB_HOST=localhost\nPORT=8080\n")
    run_group(_args(path, show_ungrouped=True))
    captured = capsys.readouterr()
    assert "ungrouped" in captured.out
    assert "PORT" in captured.out


def test_run_group_hide_ungrouped_by_default(tmp_env, capsys):
    path = _write(tmp_env, "DB_HOST=localhost\nPORT=8080\n")
    run_group(_args(path, show_ungrouped=False))
    captured = capsys.readouterr()
    assert "PORT" not in captured.out


def test_build_group_parser_returns_parser():
    parser = build_group_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_group_parser_default_separator():
    parser = build_group_parser()
    args = parser.parse_args(["myfile.env"])
    assert args.separator == "_"
