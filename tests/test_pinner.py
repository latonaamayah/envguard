"""Tests for envguard.pinner."""
import json
import pytest
from envguard.pinner import pin, save_pin, load_pin, PinEntry


@pytest.fixture
def env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}


def test_pin_creates_entry_for_each_key(env):
    result = pin(env)
    assert set(result.pinned.keys()) == set(env.keys())


def test_pin_entry_checksum_is_16_chars(env):
    result = pin(env)
    for entry in result.pinned.values():
        assert len(entry.checksum) == 16


def test_no_drift_when_no_existing(env):
    result = pin(env)
    assert not result.has_drift()
    assert result.new_keys == []
    assert result.changed == []
    assert result.removed_keys == []


def test_new_keys_detected_when_existing_empty(env):
    existing = {k: PinEntry.compute_checksum(v) for k, v in env.items()}
    new_env = dict(env)
    new_env["NEW_KEY"] = "newvalue"
    result = pin(new_env, existing)
    assert "NEW_KEY" in result.new_keys


def test_changed_key_detected(env):
    existing = {k: PinEntry.compute_checksum(v) for k, v in env.items()}
    modified = dict(env)
    modified["DB_HOST"] = "remotehost"
    result = pin(modified, existing)
    assert "DB_HOST" in result.changed


def test_removed_key_detected(env):
    existing = {k: PinEntry.compute_checksum(v) for k, v in env.items()}
    reduced = {k: v for k, v in env.items() if k != "SECRET"}
    result = pin(reduced, existing)
    assert "SECRET" in result.removed_keys


def test_summary_no_drift(env):
    result = pin(env)
    assert result.summary() == "No drift detected."


def test_summary_with_changes(env):
    existing = {k: PinEntry.compute_checksum(v) for k, v in env.items()}
    modified = dict(env)
    modified["DB_PORT"] = "9999"
    result = pin(modified, existing)
    assert "changed" in result.summary()


def test_save_and_load_pin(env, tmp_path):
    result = pin(env)
    path = str(tmp_path / "pin.json")
    save_pin(result, path)
    loaded = load_pin(path)
    assert set(loaded.keys()) == set(env.keys())
    for key in env:
        assert loaded[key] == result.pinned[key].checksum


def test_save_pin_is_valid_json(env, tmp_path):
    result = pin(env)
    path = str(tmp_path / "pin.json")
    save_pin(result, path)
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_checksum_deterministic():
    c1 = PinEntry.compute_checksum("hello")
    c2 = PinEntry.compute_checksum("hello")
    assert c1 == c2


def test_checksum_differs_for_different_values():
    c1 = PinEntry.compute_checksum("hello")
    c2 = PinEntry.compute_checksum("world")
    assert c1 != c2
