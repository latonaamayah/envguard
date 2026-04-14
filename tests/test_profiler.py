"""Tests for envguard.profiler."""
import pytest

from envguard.profiler import profile, ProfileResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_env():
    return {
        "APP_NAME": "myapp",
        "PORT": "8080",
        "DEBUG": "true",
        "SECRET_KEY": "supersecret",
        "EMPTY_VAR": "",
        "LONG_VAR": "x" * 70,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_total_count(simple_env):
    result = profile(simple_env)
    assert result.total == 6


def test_empty_count(simple_env):
    result = profile(simple_env)
    assert result.empty_count == 1


def test_sensitive_count(simple_env):
    result = profile(simple_env)
    # SECRET_KEY should be flagged as sensitive
    assert result.sensitive_count >= 1


def test_long_value_count(simple_env):
    result = profile(simple_env)
    assert result.long_value_count == 1


def test_numeric_count(simple_env):
    result = profile(simple_env)
    assert result.numeric_count == 1  # PORT


def test_boolean_count(simple_env):
    result = profile(simple_env)
    assert result.boolean_count == 1  # DEBUG


def test_avg_key_length(simple_env):
    result = profile(simple_env)
    expected = sum(len(k) for k in simple_env) / len(simple_env)
    assert result.avg_key_length == pytest.approx(expected)


def test_avg_value_length_empty_env():
    result = profile({})
    assert result.avg_value_length == 0.0
    assert result.avg_key_length == 0.0


def test_summary_contains_total(simple_env):
    result = profile(simple_env)
    assert "6" in result.summary()


def test_negative_numeric_value():
    result = profile({"OFFSET": "-42"})
    assert result.numeric_count == 1


def test_float_numeric_value():
    result = profile({"RATE": "3.14"})
    assert result.numeric_count == 1


def test_empty_env():
    result = profile({})
    assert result.total == 0
    assert result.empty_count == 0
    assert result.sensitive_count == 0
