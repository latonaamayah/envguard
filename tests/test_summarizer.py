"""Tests for envguard.summarizer."""
import pytest
from envguard.summarizer import summarize, SummaryResult


@pytest.fixture()
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "EMPTY_VAR": "",
        "ANOTHER_EMPTY": "",
        "PLAIN": "value",
    }


def test_returns_summary_result(env):
    result = summarize(env)
    assert isinstance(result, SummaryResult)


def test_total_count(env):
    result = summarize(env)
    assert result.total == 8


def test_empty_count(env):
    result = summarize(env)
    assert result.empty_count == 2


def test_sensitive_count(env):
    result = summarize(env)
    # DB_PASSWORD and API_KEY are sensitive
    assert result.sensitive_count == 2


def test_longest_key(env):
    result = summarize(env)
    assert result.longest_key == "ANOTHER_EMPTY"


def test_longest_value_key(env):
    result = summarize(env)
    assert result.longest_value_key == "DB_PASSWORD"


def test_prefix_distribution(env):
    result = summarize(env)
    assert result.prefix_distribution["DB"] == 3
    assert result.prefix_distribution["API"] == 1
    assert result.prefix_distribution["APP"] == 1


def test_no_prefix_key_excluded_from_distribution(env):
    result = summarize(env)
    assert "PLAIN" not in result.prefix_distribution


def test_has_empty_true(env):
    result = summarize(env)
    assert result.has_empty() is True


def test_has_empty_false():
    result = summarize({"KEY": "val"})
    assert result.has_empty() is False


def test_has_sensitive_true(env):
    result = summarize(env)
    assert result.has_sensitive() is True


def test_has_sensitive_false():
    result = summarize({"HOST": "localhost", "PORT": "8080"})
    assert result.has_sensitive() is False


def test_empty_env_returns_zero_totals():
    result = summarize({})
    assert result.total == 0
    assert result.empty_count == 0
    assert result.sensitive_count == 0


def test_summary_string_contains_total(env):
    result = summarize(env)
    text = result.summary()
    assert "8" in text


def test_summary_string_contains_prefix_distribution(env):
    result = summarize(env)
    text = result.summary()
    assert "DB" in text
