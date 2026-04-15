"""Tests for envguard.deprecator."""
import pytest
from envguard.deprecator import DeprecationEntry, DeprecationResult, deprecate


DEPRECATED_MAP = {
    "OLD_DB_URL": {
        "reason": "replaced by DATABASE_URL",
        "replacement": "DATABASE_URL",
    },
    "LEGACY_SECRET": {
        "reason": "no longer supported",
    },
}


def test_no_deprecations_clean_env():
    env = {"DATABASE_URL": "postgres://localhost/db", "APP_PORT": "8080"}
    result = deprecate(env, DEPRECATED_MAP)
    assert not result.has_deprecations()
    assert result.entries == []
    assert set(result.clean) == {"DATABASE_URL", "APP_PORT"}


def test_single_deprecated_key_detected():
    env = {"OLD_DB_URL": "postgres://localhost/old", "APP_PORT": "8080"}
    result = deprecate(env, DEPRECATED_MAP)
    assert result.has_deprecations()
    assert len(result.entries) == 1
    assert result.entries[0].key == "OLD_DB_URL"


def test_deprecated_entry_has_reason():
    env = {"OLD_DB_URL": "postgres://localhost/old"}
    result = deprecate(env, DEPRECATED_MAP)
    assert result.entries[0].reason == "replaced by DATABASE_URL"


def test_deprecated_entry_has_replacement():
    env = {"OLD_DB_URL": "postgres://localhost/old"}
    result = deprecate(env, DEPRECATED_MAP)
    assert result.entries[0].replacement == "DATABASE_URL"


def test_deprecated_entry_without_replacement():
    env = {"LEGACY_SECRET": "abc123"}
    result = deprecate(env, DEPRECATED_MAP)
    assert result.entries[0].replacement is None


def test_multiple_deprecated_keys():
    env = {"OLD_DB_URL": "x", "LEGACY_SECRET": "y", "APP_ENV": "prod"}
    result = deprecate(env, DEPRECATED_MAP)
    assert len(result.entries) == 2
    assert set(result.deprecated_keys()) == {"OLD_DB_URL", "LEGACY_SECRET"}
    assert result.clean == ["APP_ENV"]


def test_message_includes_replacement():
    entry = DeprecationEntry(
        key="OLD_DB_URL",
        reason="replaced by DATABASE_URL",
        replacement="DATABASE_URL",
    )
    msg = entry.message()
    assert "OLD_DB_URL" in msg
    assert "DATABASE_URL" in msg


def test_message_without_replacement():
    entry = DeprecationEntry(key="LEGACY_SECRET", reason="no longer supported")
    msg = entry.message()
    assert "LEGACY_SECRET" in msg
    assert "use" not in msg


def test_summary_no_deprecations():
    env = {"APP_ENV": "prod", "PORT": "8080"}
    result = deprecate(env, DEPRECATED_MAP)
    summary = result.summary()
    assert "No deprecated" in summary
    assert "2 checked" in summary


def test_summary_with_deprecations():
    env = {"OLD_DB_URL": "x", "APP_ENV": "prod"}
    result = deprecate(env, DEPRECATED_MAP)
    summary = result.summary()
    assert "1 deprecated" in summary
    assert "OLD_DB_URL" in summary


def test_empty_env_returns_no_deprecations():
    result = deprecate({}, DEPRECATED_MAP)
    assert not result.has_deprecations()
    assert result.clean == []


def test_empty_deprecated_map_returns_clean():
    env = {"OLD_DB_URL": "x", "APP_ENV": "prod"}
    result = deprecate(env, {})
    assert not result.has_deprecations()
    assert set(result.clean) == {"OLD_DB_URL", "APP_ENV"}
