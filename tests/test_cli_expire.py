import pytest
from io import StringIO
from pathlib import Path
from envguard.cli_expire import build_expire_parser, run_expire


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content):
    path.write_text(content)


def _args(env_file, expiry=None, warn_only=False):
    parser = build_expire_parser()
    parts = [str(env_file)]
    if expiry:
        parts += ["--expiry"] + expiry
    if warn_only:
        parts.append("--warn-only")
    return parser.parse_args(parts)


def test_run_expire_exits_zero_no_expiry(tmp_env):
    _write(tmp_env, "API_KEY=abc\nDB_PASS=secret\n")
    code = run_expire(_args(tmp_env), out=StringIO())
    assert code == 0


def test_run_expire_missing_file_exits_two(tmp_path):
    missing = tmp_path / "missing.env"
    code = run_expire(_args(missing), out=StringIO())
    assert code == 2


def test_run_expire_expired_key_exits_one(tmp_env):
    _write(tmp_env, "API_KEY=abc\n")
    args = _args(tmp_env, expiry=["API_KEY=2000-01-01"])
    code = run_expire(args, out=StringIO())
    assert code == 1


def test_run_expire_expired_warn_only_exits_zero(tmp_env):
    _write(tmp_env, "API_KEY=abc\n")
    args = _args(tmp_env, expiry=["API_KEY=2000-01-01"], warn_only=True)
    code = run_expire(args, out=StringIO())
    assert code == 0


def test_run_expire_future_key_exits_zero(tmp_env):
    _write(tmp_env, "API_KEY=abc\n")
    args = _args(tmp_env, expiry=["API_KEY=2099-12-31"])
    code = run_expire(args, out=StringIO())
    assert code == 0


def test_run_expire_output_contains_summary(tmp_env):
    _write(tmp_env, "API_KEY=abc\n")
    out = StringIO()
    run_expire(_args(tmp_env), out=out)
    assert "checked" in out.getvalue()
