"""Tests for envguard.filterer."""
import pytest

from envguard.filterer import FilterResult, filter_env


@pytest.fixture()
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "s3cr3t",
        "APP_DEBUG": "true",
        "LOG_LEVEL": "info",
    }


def test_filter_by_prefix(env):
    result = filter_env(env, prefix="DB_")
    assert set(result.matched) == {"DB_HOST", "DB_PORT"}


def test_filter_by_suffix(env):
    result = filter_env(env, suffix="_KEY")
    assert "AWS_ACCESS_KEY" in result.matched


def test_filter_by_pattern(env):
    result = filter_env(env, pattern=r"^AWS_")
    assert set(result.matched) == {"AWS_ACCESS_KEY", "AWS_SECRET"}


def test_filter_by_keys(env):
    result = filter_env(env, keys=["APP_DEBUG", "LOG_LEVEL"])
    assert set(result.matched) == {"APP_DEBUG", "LOG_LEVEL"}


def test_excluded_contains_remainder(env):
    result = filter_env(env, prefix="DB_")
    assert "APP_DEBUG" in result.excluded
    assert "DB_HOST" not in result.excluded


def test_invert_flag(env):
    result = filter_env(env, prefix="DB_", invert=True)
    assert "DB_HOST" not in result.matched
    assert "APP_DEBUG" in result.matched


def test_has_matches_true(env):
    result = filter_env(env, prefix="DB_")
    assert result.has_matches()


def test_has_matches_false(env):
    result = filter_env(env, prefix="NONEXISTENT_")
    assert not result.has_matches()


def test_summary_format(env):
    result = filter_env(env, prefix="DB_")
    assert "2 matched" in result.summary()
    assert "4 excluded" in result.summary()


def test_no_criteria_raises():
    with pytest.raises(ValueError, match="Provide at least one"):
        filter_env({"KEY": "val"})


def test_multiple_criteria_union(env):
    # prefix OR keys — union behaviour
    result = filter_env(env, prefix="DB_", keys=["LOG_LEVEL"])
    assert "DB_HOST" in result.matched
    assert "LOG_LEVEL" in result.matched
    assert "AWS_SECRET" not in result.matched
