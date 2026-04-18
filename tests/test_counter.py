import pytest
from envguard.counter import count, CountResult, CountEntry


@pytest.fixture
def env():
    return {
        "HOST": "localhost",
        "PORT": "5432",
        "DEBUG": "true",
        "EMPTY_VAR": "",
        "RATIO": "3.14",
        "ENABLED": "yes",
    }


def test_returns_count_result(env):
    result = count(env)
    assert isinstance(result, CountResult)


def test_total_matches_env_size(env):
    result = count(env)
    assert result.total == len(env)


def test_has_entries_true(env):
    result = count(env)
    assert result.has_entries() is True


def test_has_entries_false_empty():
    result = count({})
    assert result.has_entries() is False


def test_empty_count(env):
    result = count(env)
    assert result.empty_count == 1


def test_numeric_count(env):
    result = count(env)
    # PORT=5432 and RATIO=3.14 are numeric; DEBUG/ENABLED are boolean
    assert result.numeric_count == 2


def test_boolean_count(env):
    result = count(env)
    # DEBUG=true, ENABLED=yes
    assert result.boolean_count == 2


def test_no_empty_when_all_filled():
    result = count({"A": "1", "B": "hello"})
    assert result.empty_count == 0


def test_entry_has_correct_key(env):
    result = count(env)
    keys = [e.key for e in result.entries]
    assert "HOST" in keys
    assert "PORT" in keys


def test_entry_value_length():
    result = count({"KEY": "hello"})
    assert result.entries[0].value_length == 5


def test_summary_string(env):
    result = count(env)
    s = result.summary()
    assert "variables" in s
    assert "empty" in s
    assert "numeric" in s
    assert "boolean" in s


def test_empty_env_summary():
    result = count({})
    assert "0 variables" in result.summary()
