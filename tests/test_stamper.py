import json
import pytest
from envguard.stamper import stamp, StampEntry, StampResult


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret123",
        "APP_ENV": "production",
    }


def test_returns_stamp_result(env):
    result = stamp(env)
    assert isinstance(result, StampResult)


def test_entry_count_matches_env(env):
    result = stamp(env)
    assert len(result.entries) == len(env)


def test_has_entries_true(env):
    result = stamp(env)
    assert result.has_entries()


def test_has_entries_false_empty():
    result = stamp({})
    assert not result.has_entries()


def test_entry_fingerprint_is_16_chars(env):
    result = stamp(env)
    for entry in result.entries.values():
        assert len(entry.fingerprint) == 16


def test_entry_has_stamped_at(env):
    result = stamp(env)
    for entry in result.entries.values():
        assert "T" in entry.stamped_at  # ISO format


def test_get_returns_entry(env):
    result = stamp(env)
    entry = result.get("DB_HOST")
    assert isinstance(entry, StampEntry)
    assert entry.key == "DB_HOST"
    assert entry.value == "localhost"


def test_get_missing_key_returns_none(env):
    result = stamp(env)
    assert result.get("NONEXISTENT") is None


def test_stamp_selected_keys_only(env):
    result = stamp(env, keys=["DB_HOST", "API_KEY"])
    assert set(result.entries.keys()) == {"DB_HOST", "API_KEY"}


def test_stamp_ignores_missing_key(env):
    result = stamp(env, keys=["DB_HOST", "MISSING_KEY"])
    assert "MISSING_KEY" not in result.entries
    assert "DB_HOST" in result.entries


def test_label_stored_in_result(env):
    result = stamp(env, label="v1.2.3")
    assert result.label == "v1.2.3"


def test_summary_includes_count(env):
    result = stamp(env)
    assert "4" in result.summary()


def test_summary_includes_label(env):
    result = stamp(env, label="release")
    assert "release" in result.summary()


def test_as_dict_structure(env):
    result = stamp(env, label="test")
    d = result.as_dict()
    assert d["label"] == "test"
    assert "DB_HOST" in d["entries"]
    assert "fingerprint" in d["entries"]["DB_HOST"]


def test_to_json_is_valid(env):
    result = stamp(env)
    parsed = json.loads(result.to_json())
    assert "entries" in parsed


def test_str_entry(env):
    result = stamp(env)
    entry = result.get("DB_HOST")
    s = str(entry)
    assert "DB_HOST" in s
    assert entry.fingerprint in s
