"""Tests for envguard.cli_validate_schema."""
import json
import os
import pytest

from envguard.cli_validate_schema import build_validate_schema_parser, run_validate_schema


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


@pytest.fixture
def schema_file(tmp_env):
    data = json.dumps(
        [
            {"name": "APP_ENV", "required": True, "type": "string", "allowed_values": ["dev", "prod"]},
            {"name": "PORT", "required": True, "type": "integer"},
            {"name": "DEBUG", "required": False, "type": "boolean"},
        ]
    )
    return _write(tmp_env / "schema.json", data)


@pytest.fixture
def valid_env_file(tmp_env):
    return _write(tmp_env / ".env", "APP_ENV=dev\nPORT=8080\nDEBUG=true\n")


@pytest.fixture
def invalid_env_file(tmp_env):
    return _write(tmp_env / ".env.bad", "APP_ENV=unknown\nPORT=notanint\n")


def _args(env_file, schema_file, fmt="text", strict=False):
    parser = build_validate_schema_parser()
    argv = [env_file, schema_file, "--format", fmt]
    if strict:
        argv.append("--strict")
    return parser.parse_args(argv)


def test_run_validate_schema_exits_zero(valid_env_file, schema_file):
    args = _args(valid_env_file, schema_file)
    assert run_validate_schema(args) == 0


def test_run_validate_schema_exits_one_on_violations(invalid_env_file, schema_file):
    args = _args(invalid_env_file, schema_file)
    assert run_validate_schema(args) == 1


def test_run_validate_schema_missing_env_exits_two(tmp_env, schema_file):
    args = _args(str(tmp_env / "nonexistent.env"), schema_file)
    assert run_validate_schema(args) == 2


def test_run_validate_schema_missing_schema_exits_two(valid_env_file, tmp_env):
    args = _args(valid_env_file, str(tmp_env / "no_schema.json"))
    assert run_validate_schema(args) == 2


def test_run_validate_schema_json_format_valid(valid_env_file, schema_file, capsys):
    args = _args(valid_env_file, schema_file, fmt="json")
    code = run_validate_schema(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert code == 0
    assert "passed" in data
    assert "violations" in data


def test_run_validate_schema_json_format_violations(invalid_env_file, schema_file, capsys):
    args = _args(invalid_env_file, schema_file, fmt="json")
    run_validate_schema(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data["violations"]) > 0


def test_run_validate_schema_text_output_contains_summary(valid_env_file, schema_file, capsys):
    args = _args(valid_env_file, schema_file)
    run_validate_schema(args)
    captured = capsys.readouterr()
    assert "passed" in captured.out
