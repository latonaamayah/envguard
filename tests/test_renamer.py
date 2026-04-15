"""Tests for envguard.renamer."""
import pytest

from envguard.renamer import rename, RenameEntry, RenameResult


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
    }


def test_no_changes_when_empty_renames(env):
    result = rename(env, [])
    assert not result.has_changes
    assert result.output == env


def test_single_rename(env):
    result = rename(env, [("DB_HOST", "DATABASE_HOST")])
    assert result.has_changes
    assert "DATABASE_HOST" in result.output
    assert "DB_HOST" not in result.output
    assert result.output["DATABASE_HOST"] == "localhost"


def test_renamed_entry_recorded(env):
    result = rename(env, [("DB_PORT", "DATABASE_PORT")])
    assert len(result.renamed) == 1
    entry = result.renamed[0]
    assert entry.old_key == "DB_PORT"
    assert entry.new_key == "DATABASE_PORT"
    assert entry.value == "5432"


def test_multiple_renames(env):
    renames = [("DB_HOST", "DATABASE_HOST"), ("DB_PORT", "DATABASE_PORT")]
    result = rename(env, renames)
    assert len(result.renamed) == 2
    assert "DATABASE_HOST" in result.output
    assert "DATABASE_PORT" in result.output
    assert "DB_HOST" not in result.output
    assert "DB_PORT" not in result.output


def test_missing_key_recorded_as_skipped(env):
    result = rename(env, [("MISSING_KEY", "NEW_KEY")])
    assert not result.has_changes
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.output


def test_partial_rename_with_missing(env):
    renames = [("DB_HOST", "DATABASE_HOST"), ("GHOST", "PHANTOM")]
    result = rename(env, renames)
    assert len(result.renamed) == 1
    assert "GHOST" in result.skipped


def test_original_env_not_mutated(env):
    original_keys = set(env.keys())
    rename(env, [("DB_HOST", "DATABASE_HOST")])
    assert set(env.keys()) == original_keys


def test_overwrite_existing_key(env):
    # Renaming DB_HOST -> DB_PORT overwrites the existing DB_PORT value
    result = rename(env, [("DB_HOST", "DB_PORT")])
    assert result.output["DB_PORT"] == "localhost"
    assert "DB_HOST" not in result.output


def test_summary_with_skipped(env):
    result = rename(env, [("DB_HOST", "DATABASE_HOST"), ("GHOST", "PHANTOM")])
    summary = result.summary()
    assert "1 renamed" in summary
    assert "1 not found" in summary


def test_summary_no_skipped(env):
    result = rename(env, [("DB_HOST", "DATABASE_HOST")])
    summary = result.summary()
    assert "1 renamed" in summary
    assert "not found" not in summary
