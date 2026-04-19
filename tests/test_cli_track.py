import pytest
from pathlib import Path
from envguard.cli_track import build_track_parser, run_track


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(before, after, strict=False):
    parser = build_track_parser()
    argv = [str(before), str(after)]
    if strict:
        argv.append("--strict")
    return parser.parse_args(argv)


def test_run_track_exits_zero_no_changes(tmp_env):
    f = _write(tmp_env / "a.env", "KEY=value\n")
    b = _write(tmp_env / "b.env", "KEY=value\n")
    assert run_track(_args(f, b)) == 0


def test_run_track_exits_zero_with_changes_no_strict(tmp_env):
    f = _write(tmp_env / "a.env", "KEY=old\n")
    b = _write(tmp_env / "b.env", "KEY=new\n")
    assert run_track(_args(f, b)) == 0


def test_run_track_exits_one_with_changes_strict(tmp_env):
    f = _write(tmp_env / "a.env", "KEY=old\n")
    b = _write(tmp_env / "b.env", "KEY=new\n")
    assert run_track(_args(f, b, strict=True)) == 1


def test_run_track_missing_before_exits_two(tmp_env):
    missing = tmp_env / "missing.env"
    existing = _write(tmp_env / "b.env", "KEY=val\n")
    assert run_track(_args(missing, existing)) == 2


def test_run_track_missing_after_exits_two(tmp_env):
    existing = _write(tmp_env / "a.env", "KEY=val\n")
    missing = tmp_env / "missing.env"
    assert run_track(_args(existing, missing)) == 2


def test_run_track_detects_added_key(tmp_env, capsys):
    f = _write(tmp_env / "a.env", "A=1\n")
    b = _write(tmp_env / "b.env", "A=1\nB=2\n")
    run_track(_args(f, b))
    out = capsys.readouterr().out
    assert "added" in out
