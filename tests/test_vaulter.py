import pytest
from envguard.vaulter import vault, VaultResult, VaultEntry, _mask, _checksum


@pytest.fixture
def env():
    return {
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123xyz",
        "APP_HOST": "localhost",
    }


def test_returns_vault_result(env):
    result = vault(env)
    assert isinstance(result, VaultResult)


def test_entry_count_matches_env(env):
    result = vault(env)
    assert len(result.entries) == 3


def test_has_entries_true(env):
    result = vault(env)
    assert result.has_entries()


def test_has_entries_false_empty():
    result = vault({})
    assert not result.has_entries()


def test_vault_selected_keys_only(env):
    result = vault(env, keys=["DB_PASSWORD"])
    assert len(result.entries) == 1
    assert result.entries[0].key == "DB_PASSWORD"


def test_vault_ignores_missing_key(env):
    result = vault(env, keys=["DB_PASSWORD", "MISSING_KEY"])
    assert len(result.entries) == 1


def test_entry_has_checksum(env):
    result = vault(env)
    entry = result.get("API_KEY")
    assert entry is not None
    assert len(entry.checksum) == 16


def test_entry_masked_hides_value(env):
    result = vault(env)
    entry = result.get("DB_PASSWORD")
    assert entry.masked != entry.value
    assert "*" in entry.masked


def test_mask_short_value():
    assert _mask("ab") == "**"


def test_mask_long_value():
    masked = _mask("supersecret", visible=4)
    assert masked.startswith("supe")
    assert masked.endswith("*" * (len("supersecret") - 4))


def test_checksum_is_deterministic():
    assert _checksum("hello") == _checksum("hello")


def test_checksum_differs_for_different_values():
    assert _checksum("hello") != _checksum("world")


def test_as_dict_returns_plain_values(env):
    result = vault(env)
    d = result.as_dict()
    assert d["DB_PASSWORD"] == "supersecret"


def test_to_json_is_valid_json(env):
    import json
    result = vault(env)
    data = json.loads(result.to_json())
    assert "DB_PASSWORD" in data


def test_summary_string(env):
    result = vault(env)
    assert "3" in result.summary()
