import json
import pytest
from envguard.sealer import seal, verify, save_seal, load_seal, SealResult


@pytest.fixture
def env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


def test_returns_seal_result(env):
    result = seal(env)
    assert isinstance(result, SealResult)


def test_entry_count_matches_env(env):
    result = seal(env)
    assert len(result.entries) == len(env)


def test_has_entries_true(env):
    result = seal(env)
    assert result.has_entries()


def test_has_entries_false_empty():
    result = seal({})
    assert not result.has_entries()


def test_checksum_is_16_chars(env):
    result = seal(env)
    for entry in result.entries:
        assert len(entry.checksum) == 16


def test_no_tampering_when_values_unchanged(env):
    sealed = seal(env)
    result = verify(env, sealed.as_dict())
    assert not result.has_tampering()


def test_tampering_detected_on_changed_value(env):
    sealed = seal(env)
    modified = dict(env)
    modified["DB_HOST"] = "evil-host"
    result = verify(modified, sealed.as_dict())
    assert result.has_tampering()
    assert "DB_HOST" in result.tampered


def test_unmodified_keys_not_in_tampered(env):
    sealed = seal(env)
    modified = dict(env)
    modified["API_KEY"] = "changed"
    result = verify(modified, sealed.as_dict())
    assert "DB_HOST" not in result.tampered
    assert "DB_PORT" not in result.tampered


def test_new_key_not_in_seal_not_tampered(env):
    sealed = seal(env)
    extended = dict(env)
    extended["NEW_KEY"] = "value"
    result = verify(extended, sealed.as_dict())
    assert "NEW_KEY" not in result.tampered


def test_summary_no_tampering(env):
    result = seal(env)
    assert "no tampering" in result.summary()


def test_summary_with_tampering(env):
    sealed = seal(env)
    modified = dict(env)
    modified["DB_HOST"] = "hacked"
    result = verify(modified, sealed.as_dict())
    assert "tampered" in result.summary()


def test_save_and_load_seal(env, tmp_path):
    path = str(tmp_path / "seal.json")
    result = seal(env)
    save_seal(result, path)
    loaded = load_seal(path)
    assert loaded == result.as_dict()


def test_save_seal_is_valid_json(env, tmp_path):
    path = str(tmp_path / "seal.json")
    save_seal(seal(env), path)
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, dict)
