import pytest
from envguard.combiner import combine, CombineEntry, CombineResult


@pytest.fixture
def base() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}


@pytest.fixture
def override() -> dict:
    return {"DB_HOST": "prod-db", "SECRET_KEY": "abc123"}


def test_returns_combine_result(base):
    result = combine([base])
    assert isinstance(result, CombineResult)


def test_single_source_no_overrides(base):
    result = combine([base])
    assert not result.has_overrides()


def test_merged_contains_all_keys_from_single_source(base):
    result = combine([base])
    assert set(result.merged().keys()) == set(base.keys())


def test_merged_values_match_source(base):
    result = combine([base])
    for key, val in base.items():
        assert result.merged()[key] == val


def test_two_sources_non_overlapping():
    a = {"A": "1"}
    b = {"B": "2"}
    result = combine([a, b])
    assert set(result.merged().keys()) == {"A", "B"}
    assert not result.has_overrides()


def test_overlapping_key_marked_overridden(base, override):
    result = combine([base, override])
    assert "DB_HOST" in result.overridden_keys()


def test_later_source_wins_on_conflict(base, override):
    result = combine([base, override])
    assert result.merged()["DB_HOST"] == "prod-db"


def test_non_overlapping_key_not_overridden(base, override):
    result = combine([base, override])
    assert "APP_ENV" not in result.overridden_keys()


def test_new_key_from_second_source_included(base, override):
    result = combine([base, override])
    assert "SECRET_KEY" in result.merged()


def test_source_labels_stored(base, override):
    result = combine([base, override], labels=["base", "prod"])
    assert result.source_labels == ["base", "prod"]


def test_default_labels_generated(base, override):
    result = combine([base, override])
    assert result.source_labels == ["source_0", "source_1"]


def test_entry_sources_list_single(base):
    result = combine([base], labels=["env"])
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.sources == ["env"]


def test_entry_sources_list_multiple(base, override):
    result = combine([base, override], labels=["base", "prod"])
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert "base" in entry.sources and "prod" in entry.sources


def test_summary_contains_key_count(base, override):
    result = combine([base, override])
    assert str(len(result.entries)) in result.summary()


def test_summary_contains_source_count(base, override):
    result = combine([base, override])
    assert "2 source(s)" in result.summary()


def test_entry_message_overridden():
    result = combine([{"X": "1"}, {"X": "2"}])
    entry = result.entries[0]
    assert "last-write wins" in entry.message()


def test_entry_message_not_overridden():
    result = combine([{"X": "1"}])
    entry = result.entries[0]
    assert "last-write wins" not in entry.message()
