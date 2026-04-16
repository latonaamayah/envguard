"""Tests for envguard.placeholder."""
import pytest
from envguard.placeholder import detect, PlaceholderResult, PlaceholderEntry


@pytest.fixture
def env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "changeme",
        "API_TOKEN": "your_api_token_here",
        "DEBUG": "true",
        "UNRESOLVED": "${SOME_VAR}",
        "PLACEHOLDER_HOST": "<your-host>",
        "PORT": "8080",
    }


def test_returns_placeholder_result(env):
    result = detect(env)
    assert isinstance(result, PlaceholderResult)


def test_has_placeholders_true(env):
    result = detect(env)
    assert result.has_placeholders is True


def test_no_placeholders_for_clean_env():
    clean = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}
    result = detect(clean)
    assert result.has_placeholders is False


def test_changeme_detected(env):
    result = detect(env)
    assert "SECRET_KEY" in result.placeholder_keys


def test_your_prefix_detected(env):
    result = detect(env)
    assert "API_TOKEN" in result.placeholder_keys


def test_unresolved_variable_detected(env):
    result = detect(env)
    assert "UNRESOLVED" in result.placeholder_keys


def test_angle_bracket_detected(env):
    result = detect(env)
    assert "PLACEHOLDER_HOST" in result.placeholder_keys


def test_clean_keys_not_in_placeholder_keys(env):
    result = detect(env)
    assert "DATABASE_URL" not in result.placeholder_keys
    assert "PORT" not in result.placeholder_keys


def test_clean_list_populated(env):
    result = detect(env)
    assert "DATABASE_URL" in result.clean
    assert "PORT" in result.clean


def test_entry_has_reason(env):
    result = detect(env)
    entry = next(e for e in result.entries if e.key == "SECRET_KEY")
    assert isinstance(entry, PlaceholderEntry)
    assert "changeme" in entry.reason


def test_summary_mentions_count(env):
    result = detect(env)
    summary = result.summary()
    assert "placeholder" in summary.lower()


def test_summary_no_placeholders():
    result = detect({"A": "1", "B": "2"})
    assert "No placeholders" in result.summary()
