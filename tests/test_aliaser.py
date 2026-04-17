import pytest
from envguard.aliaser import alias, AliasEntry, AliasResult


@pytest.fixture
def env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "APP_SECRET": "supersecret",
        "PORT": "8080",
    }


def test_returns_alias_result(env):
    result = alias(env, {})
    assert isinstance(result, AliasResult)


def test_no_aliases_when_mapping_empty(env):
    result = alias(env, {})
    assert not result.has_aliases
    assert result.entries == []


def test_single_alias_created(env):
    result = alias(env, {"DB_URL": "DATABASE_URL"})
    assert result.has_aliases
    assert "DB_URL" in result.aliased_keys


def test_alias_value_matches_original(env):
    result = alias(env, {"DB_URL": "DATABASE_URL"})
    assert result.entries[0].value == "postgres://localhost/db"


def test_alias_entry_fields(env):
    result = alias(env, {"DB_URL": "DATABASE_URL"})
    entry = result.entries[0]
    assert entry.original_key == "DATABASE_URL"
    assert entry.alias_key == "DB_URL"


def test_missing_source_key_skipped(env):
    result = alias(env, {"ALIAS": "NONEXISTENT_KEY"})
    assert not result.has_aliases
    assert "NONEXISTENT_KEY" in result.skipped


def test_existing_alias_key_skipped_without_overwrite(env):
    env_with_alias = {**env, "DB_URL": "already_set"}
    result = alias(env_with_alias, {"DB_URL": "DATABASE_URL"}, overwrite=False)
    assert not result.has_aliases
    assert "DB_URL" in result.skipped


def test_existing_alias_key_overwritten_with_flag(env):
    env_with_alias = {**env, "DB_URL": "already_set"}
    result = alias(env_with_alias, {"DB_URL": "DATABASE_URL"}, overwrite=True)
    assert result.has_aliases
    assert result.entries[0].value == "postgres://localhost/db"


def test_multiple_aliases(env):
    result = alias(env, {"DB_URL": "DATABASE_URL", "SECRET": "APP_SECRET"})
    assert len(result.entries) == 2
    assert set(result.aliased_keys) == {"DB_URL", "SECRET"}


def test_as_dict_returns_alias_values(env):
    result = alias(env, {"DB_URL": "DATABASE_URL", "SECRET": "APP_SECRET"})
    d = result.as_dict()
    assert d["DB_URL"] == "postgres://localhost/db"
    assert d["SECRET"] == "supersecret"


def test_summary_no_aliases(env):
    result = alias(env, {})
    assert "No aliases" in result.summary()


def test_summary_with_aliases(env):
    result = alias(env, {"DB_URL": "DATABASE_URL"})
    assert "Aliases created: 1" in result.summary()
    assert "DB_URL" in result.summary()


def test_entry_message_format(env):
    result = alias(env, {"DB_URL": "DATABASE_URL"})
    msg = result.entries[0].message
    assert "DB_URL" in msg
    assert "DATABASE_URL" in msg
