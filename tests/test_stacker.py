import pytest
from envguard.stacker import stack, StackResult, StackEntry


@pytest.fixture
def base():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


@pytest.fixture
def override():
    return {"PORT": "9999", "NEW_KEY": "hello"}


def test_returns_stack_result(base):
    result = stack([base])
    assert isinstance(result, StackResult)


def test_single_layer_no_conflicts(base):
    result = stack([base])
    assert not result.has_conflicts()


def test_merged_contains_all_keys(base, override):
    result = stack([base, override])
    assert "HOST" in result.merged
    assert "PORT" in result.merged
    assert "NEW_KEY" in result.merged


def test_last_wins_strategy(base, override):
    result = stack([base, override], strategy="last")
    assert result.merged["PORT"] == "9999"


def test_first_wins_strategy(base, override):
    result = stack([base, override], strategy="first")
    assert result.merged["PORT"] == "5432"


def test_conflict_detected_on_differing_values(base, override):
    result = stack([base, override])
    assert result.has_conflicts()
    assert "PORT" in result.conflict_keys()


def test_no_conflict_when_same_value():
    a = {"KEY": "same"}
    b = {"KEY": "same"}
    result = stack([a, b])
    assert not result.has_conflicts()


def test_new_key_only_in_override_no_conflict(base, override):
    result = stack([base, override])
    assert "NEW_KEY" not in result.conflict_keys()


def test_entry_source_count(base, override):
    result = stack([base, override])
    port_entry = next(e for e in result.entries if e.key == "PORT")
    assert port_entry.source_count == 2


def test_entry_source_count_single_layer(base):
    result = stack([base])
    for entry in result.entries:
        assert entry.source_count == 1


def test_summary_no_conflicts(base):
    result = stack([base])
    assert "no conflicts" in result.summary()


def test_summary_with_conflicts(base, override):
    result = stack([base, override])
    assert "conflict" in result.summary()


def test_empty_layers_returns_empty_result():
    result = stack([])
    assert result.merged == {}
    assert result.entries == []
