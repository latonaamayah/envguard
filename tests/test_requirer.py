"""Tests for envguard.requirer."""
import pytest

from envguard.schema import Schema, EnvVarSchema
from envguard.requirer import require, RequireResult


@pytest.fixture()
def schema() -> Schema:
    return Schema(
        variables=[
            EnvVarSchema(name="DATABASE_URL", required=True, type="string"),
            EnvVarSchema(name="SECRET_KEY", required=True, type="string"),
            EnvVarSchema(name="DEBUG", required=False, type="boolean"),
            EnvVarSchema(name="PORT", required=False, type="integer"),
        ]
    )


def test_all_required_present_no_missing(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    result = require(schema, env)
    assert not result.has_missing


def test_satisfied_keys_recorded(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    result = require(schema, env)
    assert "DATABASE_URL" in result.satisfied
    assert "SECRET_KEY" in result.satisfied


def test_missing_required_key_detected(schema):
    env = {"DATABASE_URL": "postgres://localhost/db"}  # SECRET_KEY absent
    result = require(schema, env)
    assert result.has_missing
    assert "SECRET_KEY" in result.missing_keys


def test_empty_required_value_detected(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "   "}
    result = require(schema, env)
    assert result.has_missing
    entry = next(e for e in result.missing if e.key == "SECRET_KEY")
    assert entry.reason == "empty"


def test_optional_key_absence_not_flagged(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc"}
    result = require(schema, env)
    assert "DEBUG" not in result.missing_keys
    assert "PORT" not in result.missing_keys


def test_missing_entry_message_missing_reason(schema):
    env = {"DATABASE_URL": "postgres://localhost/db"}
    result = require(schema, env)
    entry = next(e for e in result.missing if e.key == "SECRET_KEY")
    assert "required" in entry.message
    assert "not present" in entry.message


def test_missing_entry_message_empty_reason(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": ""}
    result = require(schema, env)
    entry = next(e for e in result.missing if e.key == "SECRET_KEY")
    assert "empty" in entry.message


def test_summary_all_satisfied(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc"}
    result = require(schema, env)
    assert "present" in result.summary()


def test_summary_with_missing(schema):
    env = {"DATABASE_URL": "postgres://localhost/db"}
    result = require(schema, env)
    summary = result.summary()
    assert "SECRET_KEY" in summary
    assert "missing" in summary.lower() or "empty" in summary.lower()


def test_empty_env_flags_all_required(schema):
    result = require(schema, {})
    assert set(result.missing_keys) == {"DATABASE_URL", "SECRET_KEY"}
