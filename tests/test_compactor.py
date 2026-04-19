import pytest
from envguard.compactor import compact, CompactResult, CompactEntry


@pytest.fixture
def env():
    return {
        "HOST": "localhost",
        "DSN": "postgres://user:pass@host/db",
        "DESCRIPTION": "hello   world",
        "PADDED": "  trimmed  ",
        "MULTI_SPACE": "one   two   three",
    }


def test_returns_compact_result(env):
    result = compact(env)
    assert isinstance(result, CompactResult)


def test_entry_count_matches_env(env):
    result = compact(env)
    assert len(result.entries) == len(env)


def test_no_change_for_clean_value(env):
    result = compact(env)
    entry = next(e for e in result.entries if e.key == "HOST")
    assert not entry.changed


def test_strips_surrounding_whitespace(env):
    result = compact(env)
    entry = next(e for e in result.entries if e.key == "PADDED")
    assert entry.compacted_value == "trimmed"
    assert entry.changed


def test_collapses_internal_spaces(env):
    result = compact(env)
    entry = next(e for e in result.entries if e.key == "DESCRIPTION")
    assert entry.compacted_value == "hello world"
    assert entry.changed


def test_multi_space_collapsed(env):
    result = compact(env)
    entry = next(e for e in result.entries if e.key == "MULTI_SPACE")
    assert entry.compacted_value == "one two three"


def test_has_changes_true(env):
    result = compact(env)
    assert result.has_changes


def test_has_changes_false():
    result = compact({"A": "clean", "B": "value"})
    assert not result.has_changes


def test_changed_keys(env):
    result = compact(env)
    assert "PADDED" in result.changed_keys
    assert "DESCRIPTION" in result.changed_keys
    assert "HOST" not in result.changed_keys


def test_as_dict_contains_all_keys(env):
    result = compact(env)
    assert set(result.as_dict.keys()) == set(env.keys())


def test_as_dict_values_are_compacted(env):
    result = compact(env)
    d = result.as_dict
    assert d["PADDED"] == "trimmed"
    assert d["MULTI_SPACE"] == "one two three"


def test_summary_format(env):
    result = compact(env)
    s = result.summary()
    assert "/" in s
    assert "compacted" in s


def test_empty_env():
    result = compact({})
    assert not result.has_changes
    assert result.entries == []
