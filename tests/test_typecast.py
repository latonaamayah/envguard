"""Tests for envguard.typecast module."""

import pytest

from envguard.schema import Schema, EnvVarSchema
from envguard.typecast import typecast, CastResult


@pytest.fixture()
def schema() -> Schema:
    return Schema(
        variables={
            "PORT": EnvVarSchema(name="PORT", type="integer", required=True),
            "RATE": EnvVarSchema(name="RATE", type="float", required=False),
            "DEBUG": EnvVarSchema(name="DEBUG", type="boolean", required=False),
            "APP_NAME": EnvVarSchema(name="APP_NAME", type="string", required=True),
        }
    )


def test_integer_cast(schema):
    result = typecast({"PORT": "8080"}, schema)
    assert not result.has_errors()
    assert result.as_dict()["PORT"] == 8080
    assert isinstance(result.as_dict()["PORT"], int)


def test_float_cast(schema):
    result = typecast({"RATE": "3.14"}, schema)
    assert not result.has_errors()
    assert result.as_dict()["RATE"] == pytest.approx(3.14)


def test_boolean_cast_true_variants(schema):
    for val in ("true", "1", "yes"):
        result = typecast({"DEBUG": val}, schema)
        assert result.as_dict()["DEBUG"] is True


def test_boolean_cast_false_variants(schema):
    for val in ("false", "0", "no"):
        result = typecast({"DEBUG": val}, schema)
        assert result.as_dict()["DEBUG"] is False


def test_string_cast_unchanged(schema):
    result = typecast({"APP_NAME": "myapp"}, schema)
    assert result.as_dict()["APP_NAME"] == "myapp"


def test_invalid_integer_produces_error(schema):
    result = typecast({"PORT": "not-a-number"}, schema)
    assert result.has_errors()
    assert any("PORT" in e for e in result.errors)


def test_invalid_boolean_produces_error(schema):
    result = typecast({"DEBUG": "maybe"}, schema)
    assert result.has_errors()
    assert any("DEBUG" in e for e in result.errors)


def test_missing_key_skipped(schema):
    result = typecast({}, schema)
    assert not result.has_errors()
    assert result.entries == []


def test_summary_message(schema):
    result = typecast({"PORT": "80", "APP_NAME": "svc"}, schema)
    summary = result.summary()
    assert "2 variable(s) processed" in summary
    assert "0 cast error(s)" in summary


def test_summary_with_errors(schema):
    result = typecast({"PORT": "bad"}, schema)
    assert "1 cast error(s)" in result.summary()
