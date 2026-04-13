"""Tests for envguard.auditor module."""
import pytest

from envguard.auditor import AuditResult, audit
from envguard.schema import EnvVarSchema, Schema


@pytest.fixture()
def schema() -> Schema:
    return Schema(
        variables={
            "DATABASE_URL": EnvVarSchema(name="DATABASE_URL", required=True, type="string"),
            "PORT": EnvVarSchema(name="PORT", required=True, type="integer"),
            "DEBUG": EnvVarSchema(name="DEBUG", required=False, type="boolean"),
            "CACHE_TTL": EnvVarSchema(name="CACHE_TTL", required=False, type="integer"),
        }
    )


def test_no_issues_when_env_matches_schema(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432", "DEBUG": "true"}
    result = audit(env, schema)
    assert result.undeclared == []
    # CACHE_TTL is optional and missing — should appear in unused_optional
    assert "CACHE_TTL" in result.unused_optional


def test_undeclared_variable_detected(schema):
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "PORT": "5432",
        "SECRET_TOKEN": "abc123",  # not in schema
    }
    result = audit(env, schema)
    assert "SECRET_TOKEN" in result.undeclared


def test_multiple_undeclared_variables(schema):
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "PORT": "5432",
        "EXTRA_ONE": "1",
        "EXTRA_TWO": "2",
    }
    result = audit(env, schema)
    assert sorted(result.undeclared) == ["EXTRA_ONE", "EXTRA_TWO"]


def test_unused_optional_detected(schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"}
    result = audit(env, schema)
    assert "DEBUG" in result.unused_optional
    assert "CACHE_TTL" in result.unused_optional


def test_has_issues_false_when_clean(schema):
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "PORT": "5432",
        "DEBUG": "false",
        "CACHE_TTL": "300",
    }
    result = audit(env, schema)
    assert not result.has_issues


def test_has_issues_true_when_undeclared(schema):
    env = {"DATABASE_URL": "x", "PORT": "1", "GHOST": "y"}
    result = audit(env, schema)
    assert result.has_issues


def test_summary_no_issues(schema):
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "PORT": "5432",
        "DEBUG": "true",
        "CACHE_TTL": "60",
    }
    result = audit(env, schema)
    assert result.summary() == "No audit issues found."


def test_summary_with_issues(schema):
    env = {"DATABASE_URL": "x", "PORT": "1", "UNKNOWN": "val"}
    result = audit(env, schema)
    summary = result.summary()
    assert "undeclared" in summary
    assert "UNKNOWN" in summary
