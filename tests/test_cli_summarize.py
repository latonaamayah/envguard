"""Tests for envguard.cli_summarize."""
import argparse
import io
import os
import pytest

from envguard.cli_summarize import build_summarize_parser, run_summarize


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(env_file: str, fmt: str = "text") -> argparse.Namespace:
    return argparse.Namespace(env_file=env_file, fmt=fmt)


def test_run_summarize_exits_zero(tmp_env):
    path = _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\n")
    out, err = io.StringIO(), io.StringIO()
    code = run_summarize(_args(path), out=out, err=err)
    assert code == 0


def test_run_summarize_missing_file_exits_two(tmp_path):
    out, err = io.StringIO(), io.StringIO()
    code = run_summarize(_args(str(tmp_path / "missing.env")), out=out, err=err)
    assert code == 2
    assert "error" in err.getvalue().lower()


def test_run_summarize_text_output_contains_total(tmp_env):
    path = _write(tmp_env, "A=1\nB=2\nC=3\n")
    out, err = io.StringIO(), io.StringIO()
    run_summarize(_args(path), out=out, err=err)
    assert "3" in out.getvalue()


def test_run_summarize_json_output_is_valid(tmp_env):
    import json
    path = _write(tmp_env, "DB_HOST=localhost\nDB_PASSWORD=secret\n")
    out, err = io.StringIO(), io.StringIO()
    code = run_summarize(_args(path, fmt="json"), out=out, err=err)
    assert code == 0
    data = json.loads(out.getvalue())
    assert data["total"] == 2


def test_run_summarize_json_sensitive_count(tmp_env):
    import json
    path = _write(tmp_env, "API_KEY=abc\nHOST=localhost\n")
    out, err = io.StringIO(), io.StringIO()
    run_summarize(_args(path, fmt="json"), out=out, err=err)
    data = json.loads(out.getvalue())
    assert data["sensitive_count"] == 1


def test_run_summarize_json_prefix_distribution(tmp_env):
    import json
    path = _write(tmp_env, "DB_HOST=h\nDB_PORT=p\nAPP_NAME=n\n")
    out, err = io.StringIO(), io.StringIO()
    run_summarize(_args(path, fmt="json"), out=out, err=err)
    data = json.loads(out.getvalue())
    assert data["prefix_distribution"]["DB"] == 2
    assert data["prefix_distribution"]["APP"] == 1


def test_build_summarize_parser_returns_parser():
    parser = build_summarize_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_run_summarize_empty_file_exits_zero(tmp_env):
    path = _write(tmp_env, "")
    out, err = io.StringIO(), io.StringIO()
    code = run_summarize(_args(path), out=out, err=err)
    assert code == 0
