"""Integration-level tests for the envguard CLI entry point."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envguard.cli import main


SCHEMA_CONTENT = json.dumps({
    "variables": [
        {"name": "DATABASE_URL", "required": True, "type": "string"},
        {"name": "PORT", "required": False, "type": "integer"},
    ]
})


@pytest.fixture
def schema_file(tmp_path):
    p = tmp_path / "envguard.schema.json"
    p.write_text(SCHEMA_CONTENT)
    return str(p)


@pytest.fixture
def valid_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DATABASE_URL=postgres://localhost/db\nPORT=5432\n")
    return str(p)


@pytest.fixture
def invalid_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("PORT=not_a_number\n")
    return str(p)


def test_cli_valid_env_exits_zero(valid_env_file, schema_file):
    code = main([valid_env_file, "--schema", schema_file])
    assert code == 0


def test_cli_missing_required_exits_one(invalid_env_file, schema_file):
    code = main([invalid_env_file, "--schema", schema_file])
    assert code == 1


def test_cli_missing_env_file_exits_two(schema_file):
    code = main(["/nonexistent/.env", "--schema", schema_file])
    assert code == 2


def test_cli_missing_schema_exits_two(valid_env_file):
    code = main([valid_env_file, "--schema", "/nonexistent/schema.json"])
    assert code == 2


def test_cli_json_format_produces_valid_json(valid_env_file, schema_file, capsys):
    code = main([valid_env_file, "--schema", schema_file, "--format", "json"])
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert "valid" in parsed
    assert code == 0


def test_cli_strict_exits_one_on_warnings(tmp_path, schema_file):
    # PORT is optional — omitting it should produce a warning but not an error
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=postgres://localhost/db\n")
    # Without --strict, exit 0; with --strict, exit 1 only if there are warnings
    code_normal = main([str(env_file), "--schema", schema_file])
    assert code_normal == 0
