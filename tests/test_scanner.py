"""Tests for envguard.scanner."""
import pytest
from envguard.scanner import scan, ScanResult, ScanIssue


def test_no_issues_for_clean_env():
    env = {"HOST": "localhost", "PORT": "8080", "DEBUG": "false"}
    result = scan(env)
    assert not result.has_issues
    assert result.summary() == "No security issues detected."


def test_placeholder_value_is_warning():
    env = {"DB_PASSWORD": "changeme"}
    result = scan(env)
    assert result.has_issues
    issue = result.issues[0]
    assert issue.key == "DB_PASSWORD"
    assert issue.severity == "warning"
    assert "placeholder" in issue.reason


def test_placeholder_variants():
    placeholders = ["todo", "fixme", "example", "dummy", "fake", "<YOUR_TOKEN>", "[REPLACE]"]
    for val in placeholders:
        result = scan({"SECRET": val})
        assert result.has_issues, f"Expected issue for placeholder value: {val!r}"
        assert result.issues[0].severity == "warning"


def test_credentials_in_url_is_warning():
    env = {"DATABASE_URL": "postgres://admin:s3cr3t@db.host:5432/mydb"}
    result = scan(env)
    assert result.has_issues
    assert any("credentials embedded" in i.reason for i in result.issues)


def test_clean_url_no_issue():
    env = {"DATABASE_URL": "postgres://db.host:5432/mydb"}
    result = scan(env)
    assert not result.has_issues


def test_errors_property_filters_correctly():
    env = {
        "AWS_SECRET_ACCESS_KEY": "AKIAIOSFODNN7EXAMPLE",
        "API_TOKEN": "changeme",
    }
    result = scan(env)
    errors = result.errors
    warnings = result.warnings
    # AWS credential should be an error
    assert any(i.key == "AWS_SECRET_ACCESS_KEY" for i in errors)
    # placeholder should be a warning
    assert any(i.key == "API_TOKEN" for i in warnings)


def test_summary_counts_correctly():
    env = {
        "AWS_SECRET_ACCESS_KEY": "AKIAIOSFODNN7EXAMPLE",
        "DB_TOKEN": "placeholder",
    }
    result = scan(env)
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_multiple_clean_vars_no_issues():
    env = {
        "APP_NAME": "envguard",
        "LOG_LEVEL": "info",
        "MAX_RETRIES": "3",
        "ENABLE_FEATURE_X": "true",
    }
    result = scan(env)
    assert not result.has_issues
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_empty_env_returns_no_issues():
    result = scan({})
    assert isinstance(result, ScanResult)
    assert not result.has_issues
