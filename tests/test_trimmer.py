"""Tests for envguard.trimmer."""

import pytest

from envguard.schema import Schema, EnvVarSchema
from envguard.trimmer import trim, TrimResult


@pytest.fixture
def schema() -> Schema:
    return Schema(
        variables=[
            EnvVarSchema(name="APP_ENV", required=True, type="string"),
            EnvVarSchema(name="PORT", required=False, type="integer"),
            EnvVarSchema(name="DEBUG", required=False, type="boolean"),
        ]
    )


def test_no_removal_when_all_declared(schema):
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}
    result = trim(env, schema)
    assert not result.has_removed()
    assert result.trimmed == env
    assert result.removed_keys == []


def test_removes_single_undeclared_key(schema):
    env = {"APP_ENV": "production", "EXTRA_KEY": "surprise"}
    result = trim(env, schema)
    assert result.has_removed()
    assert "EXTRA_KEY" in result.removed_keys
    assert "EXTRA_KEY" not in result.trimmed
    assert "APP_ENV" in result.trimmed


def test_removes_multiple_undeclared_keys(schema):
    env = {
        "APP_ENV": "staging",
        "UNKNOWN_ONE": "foo",
        "UNKNOWN_TWO": "bar",
    }
    result = trim(env, schema)
    assert len(result.removed_keys) == 2
    assert "UNKNOWN_ONE" in result.removed_keys
    assert "UNKNOWN_TWO" in result.removed_keys
    assert result.trimmed == {"APP_ENV": "staging"}


def test_original_is_unchanged(schema):
    env = {"APP_ENV": "test", "GHOST": "boo"}
    result = trim(env, schema)
    assert result.original == env
    assert "GHOST" in result.original


def test_empty_env_returns_empty_trimmed(schema):
    result = trim({}, schema)
    assert result.trimmed == {}
    assert not result.has_removed()


def test_all_undeclared_removes_everything(schema):
    env = {"FOO": "1", "BAR": "2"}
    result = trim(env, schema)
    assert result.trimmed == {}
    assert len(result.removed_keys) == 2


def test_removed_keys_are_sorted(schema):
    env = {"APP_ENV": "dev", "ZEBRA": "z", "ALPHA": "a"}
    result = trim(env, schema)
    assert result.removed_keys == sorted(result.removed_keys)


def test_summary_no_removal(schema):
    env = {"APP_ENV": "dev"}
    result = trim(env, schema)
    assert "clean" in result.summary().lower()


def test_summary_with_removal(schema):
    env = {"APP_ENV": "dev", "GHOST": "boo"}
    result = trim(env, schema)
    summary = result.summary()
    assert "GHOST" in summary
    assert "1" in summary
