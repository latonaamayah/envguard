import pytest
from envguard.quoter import quote, QuoteResult, QuoteEntry, _needs_quoting


@pytest.fixture
def env():
    return {
        "HOST": "localhost",
        "GREETING": "hello world",
        "DB_PASS": "p@ss#word",
        "PORT": "5432",
        "EMPTY": "",
    }


def test_returns_quote_result(env):
    result = quote(env)
    assert isinstance(result, QuoteResult)


def test_no_change_for_simple_values(env):
    result = quote(env)
    entry = next(e for e in result.entries if e.key == "HOST")
    assert not entry.changed


def test_value_with_space_is_quoted(env):
    result = quote(env)
    entry = next(e for e in result.entries if e.key == "GREETING")
    assert entry.changed
    assert entry.quoted == '"hello world"'


def test_value_with_hash_is_quoted(env):
    result = quote(env)
    entry = next(e for e in result.entries if e.key == "DB_PASS")
    assert entry.changed


def test_empty_value_not_quoted(env):
    result = quote(env)
    entry = next(e for e in result.entries if e.key == "EMPTY")
    assert not entry.changed


def test_as_dict_contains_all_keys(env):
    result = quote(env)
    assert set(result.as_dict.keys()) == set(env.keys())


def test_has_changes_true_when_some_quoted(env):
    result = quote(env)
    assert result.has_changes


def test_has_changes_false_when_nothing_needs_quoting():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = quote(env)
    assert not result.has_changes


def test_changed_keys_lists_only_modified(env):
    result = quote(env)
    assert "GREETING" in result.changed_keys
    assert "HOST" not in result.changed_keys


def test_single_quote_style(env):
    result = quote(env, style="single")
    entry = next(e for e in result.entries if e.key == "GREETING")
    assert entry.quoted == "'hello world'"


def test_explicit_keys_forces_quoting(env):
    result = quote(env, keys=["HOST", "PORT"])
    keys_changed = result.changed_keys
    assert "HOST" in keys_changed
    assert "PORT" in keys_changed
    assert "GREETING" not in keys_changed


def test_summary_reflects_count(env):
    result = quote(env)
    n = len(result.changed_keys)
    assert result.summary() == f"{n} key(s) quoted."


def test_needs_quoting_space():
    assert _needs_quoting("hello world")


def test_needs_quoting_already_double_quoted():
    assert not _needs_quoting('"hello world"')


def test_needs_quoting_plain_value():
    assert not _needs_quoting("localhost")
