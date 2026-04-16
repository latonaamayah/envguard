import json
import pytest
from envguard.freezer import (
    freeze,
    save_freeze,
    load_freeze,
    FreezeResult,
    FreezeEntry,
    _checksum,
)


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret123",
        "DEBUG": "true",
    }


def test_freeze_all_keys(env):
    result = freeze(env)
    assert len(result.entries) == 4


def test_freeze_selected_keys(env):
    result = freeze(env, keys=["DB_HOST", "API_KEY"])
    keys = [e.key for e in result.entries]
    assert keys == ["DB_HOST", "API_KEY"]


def test_freeze_ignores_missing_key(env):
    result = freeze(env, keys=["DB_HOST", "NONEXISTENT"])
    keys = [e.key for e in result.entries]
    assert "NONEXISTENT" not in keys
    assert "DB_HOST" in keys


def test_checksum_is_16_chars(env):
    result = freeze(env)
    for entry in result.entries:
        assert len(entry.checksum) == 16


def test_has_frozen_true(env):
    result = freeze(env)
    assert result.has_frozen() is True


def test_has_frozen_false_empty():
    result = FreezeResult(entries=[])
    assert result.has_frozen() is False


def test_no_drift_when_env_unchanged(env):
    result = freeze(env)
    drifted = result.drifted(env)
    assert drifted == []


def test_drift_detected_when_value_changes(env):
    result = freeze(env)
    modified = dict(env)
    modified["DB_HOST"] = "newhost"
    drifted = result.drifted(modified)
    assert "DB_HOST" in drifted


def test_drift_detected_when_key_missing(env):
    result = freeze(env)
    partial = {k: v for k, v in env.items() if k != "API_KEY"}
    drifted = result.drifted(partial)
    assert "API_KEY" in drifted


def test_summary_contains_count(env):
    result = freeze(env)
    assert "4" in result.summary()


def test_to_dict_roundtrip(env):
    result = freeze(env)
    data = result.to_dict()
    restored = FreezeResult.from_dict(data)
    assert len(restored.entries) == len(result.entries)
    for orig, rest in zip(result.entries, restored.entries):
        assert orig.key == rest.key
        assert orig.checksum == rest.checksum


def test_save_and_load_freeze(env, tmp_path):
    path = str(tmp_path / "freeze.json")
    result = freeze(env)
    save_freeze(result, path)
    loaded = load_freeze(path)
    assert loaded.loaded_from == path
    assert len(loaded.entries) == len(result.entries)


def test_save_creates_valid_json(env, tmp_path):
    path = str(tmp_path / "freeze.json")
    result = freeze(env)
    save_freeze(result, path)
    with open(path) as f:
        data = json.load(f)
    assert "frozen" in data
