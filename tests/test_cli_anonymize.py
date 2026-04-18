import argparse
import pytest
from pathlib import Path
from envguard.cli_anonymize import run_anonymize, build_anonymize_parser
from io import StringIO


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(env_file, placeholder="***", keys=None, summary=False):
    return argparse.Namespace(
        env_file=str(env_file),
        placeholder=placeholder,
        keys=keys,
        summary=summary,
    )


def test_run_anonymize_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=localhost\nDB_PASSWORD=secret\n")
    out = StringIO()
    code = run_anonymize(_args(f), out=out)
    assert code == 0


def test_run_anonymize_missing_file_exits_two(tmp_env):
    err = StringIO()
    code = run_anonymize(_args(tmp_env / "missing.env"), err=err)
    assert code == 2


def test_run_anonymize_sensitive_value_replaced(tmp_env):
    f = _write(tmp_env / ".env", "DB_PASSWORD=secret\n")
    out = StringIO()
    run_anonymize(_args(f), out=out)
    assert "***" in out.getvalue()
    assert "secret" not in out.getvalue()


def test_run_anonymize_non_sensitive_value_unchanged(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=localhost\n")
    out = StringIO()
    run_anonymize(_args(f), out=out)
    assert "localhost" in out.getvalue()


def test_run_anonymize_custom_placeholder(tmp_env):
    f = _write(tmp_env / ".env", "API_KEY=abc123\n")
    out = StringIO()
    run_anonymize(_args(f, placeholder="[HIDDEN]"), out=out)
    assert "[HIDDEN]" in out.getvalue()


def test_run_anonymize_summary_flag(tmp_env):
    f = _write(tmp_env / ".env", "DB_PASSWORD=secret\n")
    out = StringIO()
    run_anonymize(_args(f, summary=True), out=out)
    assert "anonymized" in out.getvalue()
