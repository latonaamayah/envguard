"""Tests for envguard.patcher."""
import pytest
from envguard.patcher import patch, PatchResult


@pytest.fixture
def env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


def test_no_changes_when_updates_empty(env):
    result = patch(env, {})
    assert result.patched == env
    assert not result.has_changes()


def test_single_update(env):
    result = patch(env, {"PORT": "6543"})
    assert result.patched["PORT"] == "6543"
    assert result.has_changes()


def test_updated_entry_recorded(env):
    result = patch(env, {"DEBUG": "true"})
    entry = next(e for e in result.entries if e.key == "DEBUG")
    assert entry.action == "updated"
    assert entry.old_value == "false"
    assert entry.new_value == "true"


def test_added_entry_recorded(env):
    result = patch(env, {"NEW_KEY": "new_value"})
    entry = next(e for e in result.entries if e.key == "NEW_KEY")
    assert entry.action == "added"
    assert entry.old_value is None


def test_unchanged_entry_recorded(env):
    result = patch(env, {"HOST": "localhost"})
    entry = next(e for e in result.entries if e.key == "HOST")
    assert entry.action == "unchanged"
    assert not result.has_changes()


def test_original_env_not_mutated(env):
    original = dict(env)
    patch(env, {"PORT": "9999"})
    assert env == original


def test_summary_counts(env):
    result = patch(env, {"PORT": "9999", "NEW": "val", "HOST": "localhost"})
    assert "1 added" in result.summary()
    assert "1 updated" in result.summary()


def test_multiple_updates(env):
    result = patch(env, {"PORT": "1111", "DEBUG": "true", "EXTRA": "x"})
    assert result.patched["PORT"] == "1111"
    assert result.patched["DEBUG"] == "true"
    assert result.patched["EXTRA"] == "x"
    assert result.patched["HOST"] == "localhost"
