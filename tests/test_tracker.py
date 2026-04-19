import pytest
from envguard.tracker import track, TrackEntry, TrackResult


@pytest.fixture
def before():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "old-key"}


@pytest.fixture
def after():
    return {"DB_HOST": "prod-host", "DB_PORT": "5432", "NEW_VAR": "hello"}


def test_returns_track_result(before, after):
    result = track(before, after)
    assert isinstance(result, TrackResult)


def test_no_changes_when_identical():
    env = {"A": "1", "B": "2"}
    result = track(env, env)
    assert not result.has_changes()


def test_added_key_detected(before, after):
    result = track(before, after)
    assert "NEW_VAR" in result.added_keys()


def test_removed_key_detected(before, after):
    result = track(before, after)
    assert "API_KEY" in result.removed_keys()


def test_modified_key_detected(before, after):
    result = track(before, after)
    assert "DB_HOST" in result.modified_keys()


def test_unchanged_key_not_in_any_list(before, after):
    result = track(before, after)
    assert "DB_PORT" not in result.added_keys()
    assert "DB_PORT" not in result.removed_keys()
    assert "DB_PORT" not in result.modified_keys()


def test_has_changes_true(before, after):
    result = track(before, after)
    assert result.has_changes()


def test_summary_format(before, after):
    result = track(before, after)
    s = result.summary()
    assert "added=" in s
    assert "removed=" in s
    assert "modified=" in s


def test_entry_message_added():
    e = TrackEntry(key="X", old_value=None, new_value="val")
    assert "added" in e.message()


def test_entry_message_removed():
    e = TrackEntry(key="X", old_value="val", new_value=None)
    assert "removed" in e.message()


def test_entry_message_modified():
    e = TrackEntry(key="X", old_value="old", new_value="new")
    assert "changed" in e.message()


def test_empty_envs_no_changes():
    result = track({}, {})
    assert not result.has_changes()
    assert result.entries == []
