"""Tests for schema parsing and validation logic."""

import pytest

from envguard.schema import EnvVarSchema, Schema
from envguard.validator import validate, ValidationResult


SAMPLE_SCHEMA_DICT = {
    "variables": {
        "DATABASE_URL": {"required": True, "type": "url"},
        "PORT": {"required": True, "type": "integer"},
        "DEBUG": {"required": False, "type": "boolean", "default": "false"},
        "LOG_LEVEL": {
            "required": True,
            "type": "string",
            "allowed_values": ["debug", "info", "warning", "error"],
        },
    }
}


@pytest.fixture
def schema():
    return Schema.from_dict(SAMPLE_SCHEMA_DICT)


def test_valid_env(schema):
    env = {
        "DATABASE_URL": "https://db.example.com/mydb",
        "PORT": "8080",
        "LOG_LEVEL": "info",
    }
    result = validate(env, schema)
    assert result.is_valid
    assert len(result.errors) == 0


def test_missing_required_variable(schema):
    env = {"PORT": "8080", "LOG_LEVEL": "info"}
    result = validate(env, schema)
    assert not result.is_valid
    assert any(e.variable == "DATABASE_URL" for e in result.errors)


def test_invalid_type_integer(schema):
    env = {
        "DATABASE_URL": "https://db.example.com/mydb",
        "PORT": "not-a-number",
        "LOG_LEVEL": "info",
    }
    result = validate(env, schema)
    assert not result.is_valid
    assert any(e.variable == "PORT" for e in result.errors)


def test_invalid_allowed_value(schema):
    env = {
        "DATABASE_URL": "https://db.example.com/mydb",
        "PORT": "8080",
        "LOG_LEVEL": "verbose",
    }
    result = validate(env, schema)
    assert not result.is_valid
    assert any(e.variable == "LOG_LEVEL" for e in result.errors)


def test_optional_variable_missing_generates_warning(schema):
    env = {
        "DATABASE_URL": "https://db.example.com/mydb",
        "PORT": "8080",
        "LOG_LEVEL": "info",
    }
    result = validate(env, schema)
    assert result.is_valid
    assert any(w.variable == "DEBUG" for w in result.warnings)


def test_invalid_schema_type_raises():
    with pytest.raises(ValueError, match="Invalid type"):
        EnvVarSchema(name="FOO", type="hexadecimal")


def test_schema_from_dict_parses_correctly():
    schema = Schema.from_dict(SAMPLE_SCHEMA_DICT)
    assert len(schema.variables) == 4
    names = [v.name for v in schema.variables]
    assert "DATABASE_URL" in names
    assert "PORT" in names
