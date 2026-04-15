"""Tests for envguard.cli_sort."""
import json
import os
import pytest
from pathlib import Path
from envguard.cli_sort import build_sort_parser, run_sort


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> str:
    p = path / ".env"
    p.write_text(content)
    return str(p)


def _args(parser, *argv):
    return parser.parse_args(list(argv))


def test_run_sort_exits_zero(tmp_env):
    env_file = _write(tmp_env, "Z=last\nA=first\nM=middle\n")
    parser = build_sort_parser()
    args = _args(parser, env_file)
    assert run_sort(args) == 0


def test_run_sort_outputs_sorted_keys(tmp_env, capsys):
    env_file = _write(tmp_env, "Z=last\nA=first\nM=middle\n")
    parser = build_sort_parser()
    args = _args(parser, env_file)
    run_sort(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)


def test_run_sort_reverse(tmp_env, capsys):
    env_file = _write(tmp_env, "A=1\nB=2\nC=3\n")
    parser = build_sort_parser()
    args = _args(parser, env_file, "--reverse")
    run_sort(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == ["C", "B", "A"]


def test_run_sort_in_place(tmp_env):
    env_file = _write(tmp_env, "Z=last\nA=first\n")
    parser = build_sort_parser()
    args = _args(parser, env_file, "--in-place")
    run_sort(args)
    content = Path(env_file).read_text()
    lines = [l for l in content.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == ["A", "Z"]


def test_run_sort_missing_file_exits_two(tmp_env):
    parser = build_sort_parser()
    args = _args(parser, str(tmp_env / "nonexistent.env"))
    assert run_sort(args) == 2


def test_run_sort_length_strategy(tmp_env, capsys):
    env_file = _write(tmp_env, "LONGKEY=1\nA=2\nMED=3\n")
    parser = build_sort_parser()
    args = _args(parser, env_file, "--strategy", "length")
    run_sort(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    lengths = [len(k) for k in keys]
    assert lengths == sorted(lengths)
