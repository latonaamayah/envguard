import pytest
from envguard.rotator import rotate, RotateResult, RotateEntry


@pytest.fixture
def env():
    return {
        "DB_PASSWORD": "old_pass",
        "API_KEY": "old_key",
        "APP_NAME": "myapp",
    }


def test_rotate_all_keys_changes_all(env):
    result = rotate(env)
    assert result.has_rotated
    assert set(result.rotated_keys) == {"DB_PASSWORD", "API_KEY", "APP_NAME"}


def test_rotate_selected_keys_only(env):
    result = rotate(env, keys=["DB_PASSWORD"])
    assert result.rotated_keys == ["DB_PASSWORD"]
    assert "API_KEY" not in result.rotated_keys


def test_rotate_preserves_unselected_values(env):
    result = rotate(env, keys=["DB_PASSWORD"])
    d = result.as_dict()
    assert d["API_KEY"] == "old_key"
    assert d["APP_NAME"] == "myapp"


def test_rotate_new_value_differs_from_old(env):
    result = rotate(env, keys=["DB_PASSWORD"])
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert entry.new_value != entry.old_value


def test_rotate_custom_generator(env):
    result = rotate(env, keys=["API_KEY"], generator=lambda: "FIXED")
    d = result.as_dict()
    assert d["API_KEY"] == "FIXED"


def test_rotate_length_respected(env):
    result = rotate(env, keys=["DB_PASSWORD"], length=16)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert len(entry.new_value) == 16


def test_rotate_empty_keys_list_rotates_nothing(env):
    result = rotate(env, keys=[])
    assert not result.has_rotated


def test_summary_reflects_count(env):
    result = rotate(env, keys=["DB_PASSWORD", "API_KEY"])
    assert "2" in result.summary()


def test_as_dict_contains_all_keys(env):
    result = rotate(env)
    assert set(result.as_dict().keys()) == set(env.keys())


def test_returns_rotate_result_type(env):
    result = rotate(env)
    assert isinstance(result, RotateResult)
