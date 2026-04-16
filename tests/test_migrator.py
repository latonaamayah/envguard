import pytest
from envguard.migrator import migrate, MigrateResult, MigrateEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASS": "secret",
        "APP_PORT": "8080",
    }


def test_returns_migrate_result(env):
    result = migrate(env, {})
    assert isinstance(result, MigrateResult)


def test_no_changes_when_mapping_empty(env):
    result = migrate(env, {})
    assert not result.has_changes
    assert result.output == env


def test_single_rename(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.output
    assert result.output["DATABASE_HOST"] == "localhost"


def test_old_key_removed_by_default(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" not in result.output


def test_keep_old_retains_original(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST"}, keep_old=True)
    assert "DB_HOST" in result.output
    assert "DATABASE_HOST" in result.output


def test_skipped_when_key_missing(env):
    result = migrate(env, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.output


def test_renamed_keys_list(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST", "DB_PASS": "DATABASE_PASSWORD"})
    assert "DB_HOST" in result.renamed_keys
    assert "DB_PASS" in result.renamed_keys


def test_has_changes_true(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.has_changes


def test_summary_format(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST", "MISSING": "X"})
    assert "1 key(s) migrated" in result.summary()
    assert "1 skipped" in result.summary()


def test_entry_message(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST"})
    entry = result.entries[0]
    assert "DB_HOST" in entry.message
    assert "DATABASE_HOST" in entry.message


def test_unrelated_keys_preserved(env):
    result = migrate(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.output["APP_PORT"] == "8080"
