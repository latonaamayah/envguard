"""Tests for envguard.differ module."""

import pytest

from envguard.differ import DiffEntry, DiffResult, diff_envs
from envguard.schema import EnvVarSchema, Schema


@pytest.fixture
def schema() -> Schema:
    return Schema(
        variables=[
            EnvVarSchema(name="DATABASE_URL", type="string", required=True),
            EnvVarSchema(name="DEBUG", type="boolean", required=False),
            EnvVarSchema(name="PORT", type="integer", required=True),
        ]
    )


def test_no_changes_when_envs_identical():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = diff_envs(env, env)
    assert not result.has_changes
    assert result.summary() == "no changes"


def test_detects_added_key():
    old = {"FOO": "bar"}
    new = {"FOO": "bar", "NEW_KEY": "value"}
    result = diff_envs(old, new)
    assert result.has_changes
    added = [e for e in result.entries if e.status == "added"]
    assert len(added) == 1
    assert added[0].key == "NEW_KEY"
    assert added[0].new_value == "value"


def test_detects_removed_key():
    old = {"FOO": "bar", "GONE": "bye"}
    new = {"FOO": "bar"}
    result = diff_envs(old, new)
    removed = [e for e in result.entries if e.status == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "GONE"
    assert removed[0].old_value == "bye"


def test_detects_changed_value():
    old = {"PORT": "8080"}
    new = {"PORT": "9090"}
    result = diff_envs(old, new)
    changed = [e for e in result.entries if e.status == "changed"]
    assert len(changed) == 1
    assert changed[0].old_value == "8080"
    assert changed[0].new_value == "9090"


def test_schema_regression_when_required_key_removed(schema):
    old = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"}
    new = {"PORT": "5432"}
    result = diff_envs(old, new, schema=schema)
    assert result.has_regressions
    assert "DATABASE_URL" in result.schema_regressions


def test_no_regression_when_optional_key_removed(schema):
    old = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432", "DEBUG": "true"}
    new = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"}
    result = diff_envs(old, new, schema=schema)
    assert not result.has_regressions
    removed = [e for e in result.entries if e.status == "removed"]
    assert removed[0].key == "DEBUG"


def test_declared_in_schema_flag_set_correctly(schema):
    old = {"DATABASE_URL": "old", "UNDECLARED": "x"}
    new = {"DATABASE_URL": "new", "UNDECLARED": "y"}
    result = diff_envs(old, new, schema=schema)
    db_entry = next(e for e in result.entries if e.key == "DATABASE_URL")
    undeclared_entry = next(e for e in result.entries if e.key == "UNDECLARED")
    assert db_entry.declared_in_schema is True
    assert undeclared_entry.declared_in_schema is False


def test_summary_string_reflects_counts():
    old = {"A": "1", "B": "2"}
    new = {"B": "changed", "C": "3"}
    result = diff_envs(old, new)
    summary = result.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "changed" in summary
