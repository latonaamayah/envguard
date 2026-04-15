"""Tests for envguard.cli_evaluate."""
import json
import os
import pytest

from envguard.cli_evaluate import build_evaluate_parser, run_evaluate


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


@pytest.fixture()
def schema_file(tmp_env):
    content = """variables:
  - name: APP_ENV
    required: true
    type: string
  - name: PORT
    required: true
    type: integer
"""
    return _write(tmp_env / "schema.yaml", content)


@pytest.fixture()
def valid_env_file(tmp_env):
    return _write(tmp_env / ".env", "APP_ENV=production\nPORT=8080\n")


@pytest.fixture()
def invalid_env_file(tmp_env):
    return _write(tmp_env / ".env.bad", "APP_ENV=production\n")


def _args(env_file, schema_file, fmt="text", fail_below=0):
    parser = build_evaluate_parser()
    return parser.parse_args([env_file, schema_file, "--format", fmt, "--fail-below", str(fail_below)])


def test_run_evaluate_exits_zero(valid_env_file, schema_file):
    args = _args(valid_env_file, schema_file)
    assert run_evaluate(args) == 0


def test_run_evaluate_missing_env_exits_two(tmp_env, schema_file):
    args = _args(str(tmp_env / "missing.env"), schema_file)
    assert run_evaluate(args) == 2


def test_run_evaluate_missing_schema_exits_two(valid_env_file, tmp_env):
    args = _args(valid_env_file, str(tmp_env / "missing.yaml"))
    assert run_evaluate(args) == 2


def test_run_evaluate_json_output(valid_env_file, schema_file, capsys):
    args = _args(valid_env_file, schema_file, fmt="json")
    run_evaluate(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "score" in data
    assert "grade" in data


def test_run_evaluate_fail_below_triggers(invalid_env_file, schema_file):
    args = _args(invalid_env_file, schema_file, fail_below=95)
    assert run_evaluate(args) == 1


def test_run_evaluate_text_output_contains_grade(valid_env_file, schema_file, capsys):
    args = _args(valid_env_file, schema_file, fmt="text")
    run_evaluate(args)
    captured = capsys.readouterr()
    assert "Grade:" in captured.out
