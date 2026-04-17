import pytest
from envguard.cloner import clone, CloneResult, CloneEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret123",
    }


def test_returns_clone_result(env):
    result = clone(env, {})
    assert isinstance(result, CloneResult)


def test_no_clones_when_mapping_empty(env):
    result = clone(env, {})
    assert not result.has_clones


def test_single_clone(env):
    result = clone(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.has_clones
    assert "DATABASE_HOST" in result.cloned_keys


def test_cloned_value_matches_original(env):
    result = clone(env, {"DB_PORT": "PORT_COPY"})
    assert result.as_dict()["PORT_COPY"] == "5432"


def test_multiple_clones(env):
    result = clone(env, {"DB_HOST": "HOST_COPY", "DB_PORT": "PORT_COPY"})
    assert len(result.entries) == 2


def test_missing_key_goes_to_skipped(env):
    result = clone(env, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert not result.has_clones


def test_transform_upper(env):
    result = clone({"GREETING": "hello"}, {"GREETING": "GREETING_UPPER"}, transform="upper")
    assert result.as_dict()["GREETING_UPPER"] == "HELLO"


def test_transform_lower(env):
    result = clone({"LABEL": "WORLD"}, {"LABEL": "LABEL_LOWER"}, transform="lower")
    assert result.as_dict()["LABEL_LOWER"] == "world"


def test_original_value_preserved_in_entry(env):
    result = clone({"X": "hello"}, {"X": "Y"}, transform="upper")
    entry = result.entries[0]
    assert entry.original_value == "hello"
    assert entry.cloned_value == "HELLO"


def test_summary_no_clones():
    result = clone({}, {})
    assert result.summary() == "No keys cloned."


def test_summary_with_clones(env):
    result = clone(env, {"DB_HOST": "HOST_COPY"})
    summary = result.summary()
    assert "DB_HOST" in summary
    assert "HOST_COPY" in summary


def test_changed_key_property(env):
    result = clone(env, {"DB_HOST": "DATABASE_HOST"})
    entry = result.entries[0]
    assert entry.changed_key is True
