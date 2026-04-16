import pytest
import argparse
from pathlib import Path
from envguard.cli_score import run_score, build_score_parser


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def _args(env_file: str, verbose: bool = False) -> argparse.Namespace:
    return argparse.Namespace(env_file=env_file, verbose=verbose)


def test_run_score_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "HOST=localhost\nPORT=8080\n")
    assert run_score(_args(str(f))) == 0


def test_run_score_missing_file_exits_two(tmp_env):
    assert run_score(_args(str(tmp_env / "missing.env"))) == 2


def test_run_score_verbose_exits_zero(tmp_env, capsys):
    f = _write(tmp_env / ".env", "HOST=localhost\n")
    code = run_score(_args(str(f), verbose=True))
    assert code == 0
    captured = capsys.readouterr()
    assert "HOST" in captured.out


def test_run_score_outputs_grade(tmp_env, capsys):
    f = _write(tmp_env / ".env", "HOST=localhost\nPORT=8080\n")
    run_score(_args(str(f)))
    captured = capsys.readouterr()
    assert "Grade" in captured.out


def test_run_score_outputs_percent(tmp_env, capsys):
    f = _write(tmp_env / ".env", "HOST=localhost\n")
    run_score(_args(str(f)))
    captured = capsys.readouterr()
    assert "%" in captured.out


def test_build_score_parser_returns_parser():
    parser = build_score_parser()
    assert isinstance(parser, argparse.ArgumentParser)
