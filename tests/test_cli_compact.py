import pytest
from pathlib import Path
from envguard.cli_compact import build_compact_parser, run_compact


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    p = path / ".env"
    p.write_text(content)
    return p


def _args(parser, *argv):
    return parser.parse_args(list(argv))


def test_run_compact_exits_zero(tmp_env):
    env_file = _write(tmp_env, "HOST=localhost\nDSN=postgres://host/db\n")
    parser = build_compact_parser()
    args = _args(parser, str(env_file))
    assert run_compact(args) == 0


def test_run_compact_missing_file_exits_two(tmp_env):
    parser = build_compact_parser()
    args = _args(parser, str(tmp_env / "missing.env"))
    assert run_compact(args) == 2


def test_run_compact_outputs_all_keys(tmp_env, capsys):
    env_file = _write(tmp_env, "A=one\nB=two\n")
    parser = build_compact_parser()
    args = _args(parser, str(env_file))
    run_compact(args)
    out = capsys.readouterr().out
    assert "A=one" in out
    assert "B=two" in out


def test_run_compact_collapses_spaces(tmp_env, capsys):
    env_file = _write(tmp_env, "MSG=hello   world\n")
    parser = build_compact_parser()
    args = _args(parser, str(env_file))
    run_compact(args)
    out = capsys.readouterr().out
    assert "MSG=hello world" in out


def test_run_compact_show_only_changed(tmp_env, capsys):
    env_file = _write(tmp_env, "CLEAN=value\nSPACED=a   b\n")
    parser = build_compact_parser()
    args = _args(parser, str(env_file), "--show-only-changed")
    run_compact(args)
    out = capsys.readouterr().out
    assert "SPACED" in out
    assert "CLEAN" not in out


def test_run_compact_summary_flag(tmp_env, capsys):
    env_file = _write(tmp_env, "A=ok\nB=  padded  \n")
    parser = build_compact_parser()
    args = _args(parser, str(env_file), "--summary")
    run_compact(args)
    out = capsys.readouterr().out
    assert "compacted" in out
