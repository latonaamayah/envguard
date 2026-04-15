"""Tests for envguard.cli_transform."""
import argparse
import io
import os
import pytest

from envguard.cli_transform import build_transform_parser, run_transform


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content):
    path.write_text(content)
    return str(path)


def _args(env_file, rules=None, show_only_changed=False):
    ns = argparse.Namespace(
        env_file=env_file,
        rules=rules or [],
        show_only_changed=show_only_changed,
    )
    return ns


def test_run_transform_exits_zero(tmp_env):
    path = _write(tmp_env, "LOG_LEVEL=debug\n")
    out, err = io.StringIO(), io.StringIO()
    code = run_transform(_args(path, rules=["LOG_LEVEL=uppercase"]), out=out, err=err)
    assert code == 0


def test_run_transform_outputs_transformed_value(tmp_env):
    path = _write(tmp_env, "LOG_LEVEL=debug\n")
    out, err = io.StringIO(), io.StringIO()
    run_transform(_args(path, rules=["LOG_LEVEL=uppercase"]), out=out, err=err)
    assert "LOG_LEVEL=DEBUG" in out.getvalue()


def test_run_transform_missing_file_exits_two(tmp_path):
    out, err = io.StringIO(), io.StringIO()
    code = run_transform(_args(str(tmp_path / "missing.env")), out=out, err=err)
    assert code == 2


def test_run_transform_invalid_rule_format_exits_two(tmp_env):
    path = _write(tmp_env, "KEY=value\n")
    out, err = io.StringIO(), io.StringIO()
    code = run_transform(_args(path, rules=["BADRULE"]), out=out, err=err)
    assert code == 2
    assert "Error" in err.getvalue()


def test_run_transform_show_only_changed(tmp_env):
    path = _write(tmp_env, "LOG_LEVEL=debug\nAPP_ENV=production\n")
    out, err = io.StringIO(), io.StringIO()
    run_transform(_args(path, rules=["LOG_LEVEL=uppercase"], show_only_changed=True), out=out, err=err)
    output = out.getvalue()
    assert "LOG_LEVEL=DEBUG" in output
    assert "APP_ENV" not in output


def test_run_transform_no_rules_outputs_all_keys(tmp_env):
    path = _write(tmp_env, "A=1\nB=2\n")
    out, err = io.StringIO(), io.StringIO()
    run_transform(_args(path), out=out, err=err)
    output = out.getvalue()
    assert "A=1" in output
    assert "B=2" in output


def test_build_transform_parser_returns_parser():
    parser = build_transform_parser()
    assert parser is not None


def test_run_transform_strip_rule(tmp_env):
    path = _write(tmp_env, "DB_HOST=  localhost  \n")
    out, err = io.StringIO(), io.StringIO()
    run_transform(_args(path, rules=["DB_HOST=strip"]), out=out, err=err)
    assert "DB_HOST=localhost" in out.getvalue()
