"""Tests for envguard.mapper."""
import pytest
from envguard.mapper import map_env, MapResult, MapEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
        "LOG_LEVEL": "info",
    }


def test_returns_map_result(env):
    result = map_env(env, {})
    assert isinstance(result, MapResult)


def test_entry_count_matches_env(env):
    result = map_env(env, {})
    assert len(result.entries) == len(env)


def test_no_mapping_all_unchanged(env):
    result = map_env(env, {})
    assert not result.has_mapped()


def test_single_key_mapped(env):
    result = map_env(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.has_mapped()
    assert "DB_HOST" in result.mapped_keys()


def test_mapped_key_appears_in_as_dict(env):
    result = map_env(env, {"DB_HOST": "DATABASE_HOST"})
    d = result.as_dict()
    assert "DATABASE_HOST" in d
    assert d["DATABASE_HOST"] == "localhost"


def test_original_key_absent_from_as_dict_when_mapped(env):
    result = map_env(env, {"DB_HOST": "DATABASE_HOST"})
    d = result.as_dict()
    assert "DB_HOST" not in d


def test_multiple_keys_mapped(env):
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = map_env(env, mapping)
    assert len(result.mapped_keys()) == 2


def test_unmapped_keys_preserved_by_default(env):
    result = map_env(env, {"DB_HOST": "DATABASE_HOST"})
    d = result.as_dict()
    assert "LOG_LEVEL" in d


def test_drop_unmapped_excludes_non_mapped_keys(env):
    result = map_env(env, {"DB_HOST": "DATABASE_HOST"}, drop_unmapped=True)
    d = result.as_dict()
    assert list(d.keys()) == ["DATABASE_HOST"]


def test_unmapped_translations_recorded(env):
    result = map_env(env, {"NONEXISTENT_KEY": "SOMETHING_ELSE"})
    assert "NONEXISTENT_KEY" in result.unmapped_keys


def test_no_unmapped_translations_when_all_present(env):
    result = map_env(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.unmapped_keys == []


def test_entry_message_mapped():
    entry = MapEntry(original_key="A", mapped_key="B", value="v", was_mapped=True)
    assert "A" in entry.message()
    assert "B" in entry.message()


def test_entry_message_unchanged():
    entry = MapEntry(original_key="A", mapped_key="A", value="v", was_mapped=False)
    assert "unchanged" in entry.message()


def test_summary_string(env):
    result = map_env(env, {"DB_HOST": "DATABASE_HOST"})
    s = result.summary()
    assert "mapped" in s


def test_empty_env_returns_empty_result():
    result = map_env({}, {"FOO": "BAR"})
    assert len(result.entries) == 0
    assert "FOO" in result.unmapped_keys
