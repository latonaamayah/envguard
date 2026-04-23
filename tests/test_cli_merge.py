"""Tests for the merge CLI subcommand."""
import pytest
from argparse import Namespace
from pathlib import Path

from envguard.cli_merge import run_merge


@pytest.fixture
def tmp_env(tmp_path):
    def _write(filename: str, content: str) -> str:
        p = tmp_path / filename
        p.write_text(content)
        return str(p)
    return _write


def _args(**kwargs) -> Namespace:
    defaults = {
        "sources": [],
        "output": None,
        "no_override": False,
        "show_conflicts": False,
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_run_merge_exits_zero(tmp_env, capsys):
    f = tmp_env("a.env", "FOO=bar\n")
    code = run_merge(_args(sources=[f]))
    assert code == 0


def test_run_merge_outputs_vars(tmp_env, capsys):
    f = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    run_merge(_args(sources=[f]))
    out = capsys.readouterr().out
    assert "BAZ=qux" in out
    assert "FOO=bar" in out


def test_run_merge_writes_to_file(tmp_env, tmp_path):
    f = tmp_env("a.env", "FOO=bar\n")
    out_file = str(tmp_path / "merged.env")
    code = run_merge(_args(sources=[f], output=out_file))
    assert code == 0
    assert Path(out_file).read_text().strip() == "FOO=bar"


def test_run_merge_conflict_last_wins(tmp_env, capsys):
    f1 = tmp_env("a.env", "FOO=first\n")
    f2 = tmp_env("b.env", "FOO=second\n")
    run_merge(_args(sources=[f1, f2]))
    out = capsys.readouterr().out
    assert "FOO=second" in out


def test_run_merge_no_override_first_wins(tmp_env, capsys):
    f1 = tmp_env("a.env", "FOO=first\n")
    f2 = tmp_env("b.env", "FOO=second\n")
    run_merge(_args(sources=[f1, f2], no_override=True))
    out = capsys.readouterr().out
    assert "FOO=first" in out


def test_run_merge_show_conflicts_to_stderr(tmp_env, capsys):
    f1 = tmp_env("a.env", "FOO=first\n")
    f2 = tmp_env("b.env", "FOO=second\n")
    run_merge(_args(sources=[f1, f2], show_conflicts=True))
    err = capsys.readouterr().err
    assert "conflict" in err
    assert "FOO" in err


def test_run_merge_missing_file_exits_two(tmp_path):
    code = run_merge(_args(sources=[str(tmp_path / "nonexistent.env")]))
    assert code == 2


def test_run_merge_no_sources_exits_zero(capsys):
    """Merging zero source files should succeed and produce no output."""
    code = run_merge(_args(sources=[]))
    assert code == 0
    out = capsys.readouterr().out
    assert out.strip() == ""
