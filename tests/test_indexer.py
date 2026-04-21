import pytest
from envguard.indexer import IndexEntry, IndexResult, index


@pytest.fixture
def env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret123",
        "EMPTY_VAR": "",
        "WHITESPACE_VAR": "   ",
    }


def test_returns_index_result(env):
    result = index(env)
    assert isinstance(result, IndexResult)


def test_entry_count_matches_env(env):
    result = index(env)
    assert len(result.entries) == len(env)


def test_has_entries_true(env):
    result = index(env)
    assert result.has_entries() is True


def test_has_entries_false_empty():
    result = index({})
    assert result.has_entries() is False


def test_positions_are_sequential(env):
    result = index(env)
    positions = [e.position for e in result.entries]
    assert positions == list(range(len(env)))


def test_get_returns_entry_by_key(env):
    result = index(env)
    entry = result.get("DB_HOST")
    assert entry is not None
    assert entry.key == "DB_HOST"
    assert entry.value == "localhost"


def test_get_returns_none_for_missing_key(env):
    result = index(env)
    assert result.get("NONEXISTENT") is None


def test_length_is_value_length(env):
    result = index(env)
    entry = result.get("DB_HOST")
    assert entry.length == len("localhost")


def test_empty_var_is_marked(env):
    result = index(env)
    entry = result.get("EMPTY_VAR")
    assert entry.is_empty is True


def test_whitespace_var_is_marked_empty(env):
    result = index(env)
    entry = result.get("WHITESPACE_VAR")
    assert entry.is_empty is True


def test_non_empty_var_not_marked(env):
    result = index(env)
    entry = result.get("DB_HOST")
    assert entry.is_empty is False


def test_empty_keys_returns_empty_vars(env):
    result = index(env)
    empty = result.empty_keys()
    assert "EMPTY_VAR" in empty
    assert "WHITESPACE_VAR" in empty
    assert "DB_HOST" not in empty


def test_keys_returns_all_keys(env):
    result = index(env)
    assert set(result.keys()) == set(env.keys())


def test_longest_returns_max_length_entry(env):
    result = index(env)
    longest = result.longest()
    assert longest is not None
    assert longest.key == "API_KEY"
    assert longest.length == len("secret123")


def test_shortest_returns_min_length_entry():
    result = index({"A": "x", "B": "longer_value"})
    shortest = result.shortest()
    assert shortest is not None
    assert shortest.key == "A"


def test_longest_returns_none_for_empty_env():
    result = index({})
    assert result.longest() is None


def test_summary_contains_total(env):
    result = index(env)
    summary = result.summary()
    assert str(len(env)) in summary


def test_str_representation(env):
    result = index(env)
    entry = result.get("DB_PORT")
    s = str(entry)
    assert "DB_PORT" in s
    assert "5432" in s
