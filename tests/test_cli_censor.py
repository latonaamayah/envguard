import pytest
from pathlib import Path
from envguard.cli_censor import build_censor_parser, run_censor


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(parser, *argv):
    return parser.parse_args(argv)


def test_run_censor_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "APP_HOST=localhost\nDB_PASSWORD=secret\n")
    parser = build_censor_parser()
    args = _args(parser, str(f))
    assert run_censor(args) == 0


def test_run_censor_missing_file_exits_two(tmp_env):
    parser = build_censor_parser()
    args = _args(parser, str(tmp_env / "missing.env"))
    assert run_censor(args) == 2


def test_run_censor_masks_sensitive_key(tmp_env, capsys):
    f = _write(tmp_env / ".env", "DB_PASSWORD=secret\n")
    parser = build_censor_parser()
    args = _args(parser, str(f))
    run_censor(args)
    out = capsys.readouterr().out
    assert "***" in out
    assert "secret" not in out


def test_run_censor_preserves_non_sensitive(tmp_env, capsys):
    f = _write(tmp_env / ".env", "APP_HOST=localhost\n")
    parser = build_censor_parser()
    args = _args(parser, str(f))
    run_censor(args)
    out = capsys.readouterr().out
    assert "localhost" in out


def test_run_censor_explicit_keys(tmp_env, capsys):
    f = _write(tmp_env / ".env", "APP_HOST=localhost\nDB_PASSWORD=secret\n")
    parser = build_censor_parser()
    args = _args(parser, str(f), "--keys", "APP_HOST")
    run_censor(args)
    out = capsys.readouterr().out
    assert "APP_HOST=***" in out
    assert "secret" in out


def test_run_censor_show_summary(tmp_env, capsys):
    f = _write(tmp_env / ".env", "DB_PASSWORD=secret\nAPP_HOST=localhost\n")
    parser = build_censor_parser()
    args = _args(parser, str(f), "--show-summary")
    run_censor(args)
    out = capsys.readouterr().out
    assert "censored" in out
