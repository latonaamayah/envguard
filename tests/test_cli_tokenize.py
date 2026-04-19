import pytest
import argparse
from pathlib import Path
from envguard.cli_tokenize import run_tokenize, build_tokenize_parser


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def _args(env_file, key=None, multi_only=False):
    return argparse.Namespace(env_file=str(env_file), key=key, multi_only=multi_only)


def test_run_tokenize_exits_zero(tmp_env):
    _write(tmp_env, "FOO=a,b,c\nBAR=hello\n")
    assert run_tokenize(_args(tmp_env)) == 0


def test_run_tokenize_missing_file_exits_two(tmp_path):
    missing = tmp_path / "missing.env"
    assert run_tokenize(_args(missing)) == 2


def test_run_tokenize_outputs_tokens(tmp_env, capsys):
    _write(tmp_env, "CSV=x,y,z\n")
    run_tokenize(_args(tmp_env))
    out = capsys.readouterr().out
    assert "CSV" in out
    assert "x, y, z" in out


def test_run_tokenize_key_filter(tmp_env, capsys):
    _write(tmp_env, "FOO=a,b\nBAR=hello\n")
    run_tokenize(_args(tmp_env, key="FOO"))
    out = capsys.readouterr().out
    assert "FOO" in out
    assert "BAR" not in out


def test_run_tokenize_multi_only(tmp_env, capsys):
    _write(tmp_env, "MULTI=a,b,c\nSINGLE=hello\n")
    run_tokenize(_args(tmp_env, multi_only=True))
    out = capsys.readouterr().out
    assert "MULTI" in out
    assert "SINGLE" not in out


def test_run_tokenize_summary_in_output(tmp_env, capsys):
    _write(tmp_env, "A=1,2\nB=x\n")
    run_tokenize(_args(tmp_env))
    out = capsys.readouterr().out
    assert "keys tokenized" in out


def test_build_tokenize_parser_returns_parser():
    parser = build_tokenize_parser()
    assert isinstance(parser, argparse.ArgumentParser)
