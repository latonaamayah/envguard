"""Tests for envguard.linter."""
import pytest

from envguard.linter import lint, LintResult
from envguard.schema import Schema, EnvVarSchema


@pytest.fixture()
def schema() -> Schema:
    return Schema(
        variables={
            "APP_NAME": EnvVarSchema(required=True, description="Application name"),
            "DB_PASSWORD": EnvVarSchema(required=True, description=""),
            "API_KEY": EnvVarSchema(required=False, description=""),
            "PORT": EnvVarSchema(required=False, description="HTTP port"),
        }
    )


def test_no_issues_for_clean_env(schema):
    env = {"APP_NAME": "myapp", "DB_PASSWORD": "s3cr3t", "PORT": "8080"}
    result = lint(env, schema)
    assert not result.has_issues


def test_error_on_required_empty_value(schema):
    env = {"APP_NAME": "", "DB_PASSWORD": "s3cr3t"}
    result = lint(env, schema)
    errors = [i for i in result.errors if i.key == "APP_NAME"]
    assert errors, "Expected an error for empty required variable"
    assert errors[0].severity == "error"


def test_warning_sensitive_key_no_description(schema):
    env = {"APP_NAME": "myapp", "DB_PASSWORD": "s3cr3t", "API_KEY": "abc"}
    result = lint(env, schema)
    warnings = [i for i in result.warnings if i.key in ("DB_PASSWORD", "API_KEY")]
    # Both DB_PASSWORD and API_KEY have no description
    keys_warned = {w.key for w in warnings}
    assert "DB_PASSWORD" in keys_warned
    assert "API_KEY" in keys_warned


def test_warning_value_with_leading_whitespace(schema):
    env = {"APP_NAME": "  myapp", "DB_PASSWORD": "s3cr3t"}
    result = lint(env, schema)
    ws_warnings = [i for i in result.warnings if "whitespace" in i.message]
    assert any(i.key == "APP_NAME" for i in ws_warnings)


def test_warning_value_with_trailing_whitespace(schema):
    env = {"APP_NAME": "myapp  ", "DB_PASSWORD": "s3cr3t"}
    result = lint(env, schema)
    ws_warnings = [i for i in result.warnings if "whitespace" in i.message]
    assert any(i.key == "APP_NAME" for i in ws_warnings)


def test_warning_very_long_value(schema):
    env = {"APP_NAME": "x" * 513, "DB_PASSWORD": "s3cr3t"}
    result = lint(env, schema)
    long_warnings = [i for i in result.warnings if "512" in i.message]
    assert any(i.key == "APP_NAME" for i in long_warnings)


def test_summary_no_issues(schema):
    result = lint({"APP_NAME": "ok", "DB_PASSWORD": "ok"}, schema)
    assert result.summary() == "No lint issues found."


def test_summary_with_issues(schema):
    env = {"APP_NAME": "", "DB_PASSWORD": "s3cr3t"}
    result = lint(env, schema)
    assert "error" in result.summary()


def test_has_issues_false_when_clean(schema):
    result = lint({"APP_NAME": "clean", "DB_PASSWORD": "pass"}, schema)
    assert result.has_issues is False


def test_errors_and_warnings_properties(schema):
    env = {"APP_NAME": "", "DB_PASSWORD": "  secret  "}
    result = lint(env, schema)
    assert isinstance(result.errors, list)
    assert isinstance(result.warnings, list)
