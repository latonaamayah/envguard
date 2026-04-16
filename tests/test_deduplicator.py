import pytest
from envguard.deduplicator import deduplicate, DeduplicateResult, DeduplicateEntry


def test_no_duplicates_returns_clean_result():
    pairs = [("HOST", "localhost"), ("PORT", "5432")]
    result = deduplicate(pairs)
    assert not result.has_duplicates
    assert result.cleaned == {"HOST": "localhost", "PORT": "5432"}


def test_single_duplicate_detected():
    pairs = [("HOST", "localhost"), ("HOST", "remotehost")]
    result = deduplicate(pairs)
    assert result.has_duplicates
    assert len(result.entries) == 1


def test_last_value_wins():
    pairs = [("KEY", "first"), ("KEY", "second"), ("KEY", "third")]
    result = deduplicate(pairs)
    assert result.cleaned["KEY"] == "third"


def test_removed_values_recorded():
    pairs = [("KEY", "a"), ("KEY", "b"), ("KEY", "c")]
    result = deduplicate(pairs)
    entry = result.entries[0]
    assert entry.removed_values == ["a", "b"]


def test_duplicate_keys_list():
    pairs = [("A", "1"), ("B", "2"), ("A", "3")]
    result = deduplicate(pairs)
    assert "A" in result.duplicate_keys
    assert "B" not in result.duplicate_keys


def test_multiple_duplicate_keys():
    pairs = [("X", "1"), ("Y", "a"), ("X", "2"), ("Y", "b")]
    result = deduplicate(pairs)
    assert len(result.entries) == 2
    assert result.cleaned["X"] == "2"
    assert result.cleaned["Y"] == "b"


def test_entry_count_property():
    pairs = [("K", "v1"), ("K", "v2"), ("K", "v3")]
    result = deduplicate(pairs)
    assert result.entries[0].count == 2


def test_summary_no_duplicates():
    result = deduplicate([("A", "1")])
    assert "No duplicate" in result.summary()


def test_summary_with_duplicates():
    pairs = [("HOST", "a"), ("HOST", "b")]
    result = deduplicate(pairs)
    s = result.summary()
    assert "HOST" in s
    assert "kept" in s


def test_order_preserved_in_cleaned():
    pairs = [("Z", "1"), ("A", "2"), ("M", "3")]
    result = deduplicate(pairs)
    assert list(result.cleaned.keys()) == ["Z", "A", "M"]
