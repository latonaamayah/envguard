"""Tests for envguard.cli_graph."""
import argparse
import os
import pytest

from envguard.cli_graph import build_graph_parser, run_graph


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(env_file: str, cycles_only: bool = False, summary: bool = False) -> argparse.Namespace:
    return argparse.Namespace(env_file=env_file, cycles_only=cycles_only, summary=summary)


def test_run_graph_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "BASE=hello\nDERIVED=${BASE}/path\n")
    assert run_graph(_args(f)) == 0


def test_run_graph_missing_file_exits_two(tmp_env):
    assert run_graph(_args(str(tmp_env / "missing.env"))) == 2


def test_run_graph_no_references_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "A=1\nB=2\n")
    assert run_graph(_args(f)) == 0


def test_run_graph_cycles_only_exits_one_on_cycle(tmp_env):
    f = _write(tmp_env / ".env", "A=${B}\nB=${A}\n")
    assert run_graph(_args(f, cycles_only=True)) == 1


def test_run_graph_cycles_only_exits_zero_no_cycle(tmp_env):
    f = _write(tmp_env / ".env", "A=hello\nB=${A}\n")
    assert run_graph(_args(f, cycles_only=True)) == 0


def test_run_graph_summary_flag(tmp_env, capsys):
    f = _write(tmp_env / ".env", "A=hello\nB=${A}\n")
    code = run_graph(_args(f, summary=True))
    out = capsys.readouterr().out
    assert "nodes=" in out
    assert code == 0


def test_build_graph_parser_returns_parser():
    parser = build_graph_parser()
    assert isinstance(parser, argparse.ArgumentParser)
