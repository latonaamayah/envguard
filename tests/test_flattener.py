"""Tests for envguard.flattener."""
import pytest

from envguard.flattener import FlattenEntry, FlattenResult, flatten, _flatten_key


@pytest.fixture
def env() -> dict:
    return {
        "DB__HOST": "localhost",
        "DB__PORT": "5432",
        "APP_NAME": "envguard",
        "AWS__S3__BUCKET": "my-bucket",
    }


def test_flat_key_with_separator():
    assert _flatten_key("DB__HOST") == "db.host"


def test_flat_key_without_separator():
    assert _flatten_key("APP_NAME") == "APP_NAME"


def test_flat_key_multi_segment():
    assert _flatten_key("AWS__S3__BUCKET") == "aws.s3.bucket"


def test_flatten_returns_result_type(env):
    result = flatten(env)
    assert isinstance(result, FlattenResult)


def test_flatten_entry_count(env):
    result = flatten(env)
    assert len(result.entries) == 4


def test_flatten_has_changes(env):
    result = flatten(env)
    assert result.has_changes is True


def test_flatten_no_changes_when_no_separator():
    result = flatten({"APP_NAME": "envguard", "PORT": "8080"})
    assert result.has_changes is False


def test_flatten_db_host_key(env):
    result = flatten(env)
    assert "db.host" in result.flattened


def test_flatten_db_host_value(env):
    result = flatten(env)
    assert result.flattened["db.host"] == "localhost"


def test_flatten_app_name_unchanged(env):
    result = flatten(env)
    assert "APP_NAME" in result.flattened
    assert result.flattened["APP_NAME"] == "envguard"


def test_flatten_multi_segment_key(env):
    result = flatten(env)
    assert "aws.s3.bucket" in result.flattened


def test_flatten_preserve_case(env):
    result = flatten(env, preserve_case=True)
    assert "DB.HOST" in result.flattened


def test_flatten_custom_separator():
    env = {"DB-HOST": "localhost", "DB-PORT": "5432"}
    result = flatten(env, separator="-")
    assert "db.host" in result.flattened
    assert "db.port" in result.flattened


def test_flatten_entry_changed_flag(env):
    result = flatten(env)
    changed = [e for e in result.entries if e.changed]
    unchanged = [e for e in result.entries if not e.changed]
    assert len(changed) == 3
    assert len(unchanged) == 1


def test_summary_contains_counts(env):
    result = flatten(env)
    summary = result.summary()
    assert "3" in summary
    assert "4" in summary
