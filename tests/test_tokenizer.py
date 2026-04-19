import pytest
from envguard.tokenizer import tokenize, TokenResult, TokenEntry, _tokenize_value


@pytest.fixture
def env():
    return {
        "SIMPLE": "hello",
        "CSV": "a,b,c",
        "PIPE": "x|y|z",
        "SPACED": "one two three",
        "SEMICOLON": "alpha;beta",
        "EMPTY": "",
        "MIXED": "foo,bar baz",
    }


def test_returns_token_result(env):
    result = tokenize(env)
    assert isinstance(result, TokenResult)


def test_entry_count_matches_env(env):
    result = tokenize(env)
    assert len(result.entries) == len(env)


def test_has_entries_true(env):
    result = tokenize(env)
    assert result.has_entries()


def test_has_entries_false_empty():
    result = tokenize({})
    assert not result.has_entries()


def test_simple_value_single_token(env):
    result = tokenize(env)
    entry = next(e for e in result.entries if e.key == "SIMPLE")
    assert entry.tokens == ["hello"]
    assert entry.token_count == 1


def test_csv_splits_correctly(env):
    result = tokenize(env)
    entry = next(e for e in result.entries if e.key == "CSV")
    assert entry.tokens == ["a", "b", "c"]


def test_pipe_splits_correctly(env):
    result = tokenize(env)
    entry = next(e for e in result.entries if e.key == "PIPE")
    assert entry.tokens == ["x", "y", "z"]


def test_space_splits_correctly(env):
    result = tokenize(env)
    entry = next(e for e in result.entries if e.key == "SPACED")
    assert entry.tokens == ["one", "two", "three"]


def test_empty_value_has_no_tokens(env):
    result = tokenize(env)
    entry = next(e for e in result.entries if e.key == "EMPTY")
    assert entry.tokens == []
    assert entry.token_count == 0


def test_keys_with_multiple_tokens(env):
    result = tokenize(env)
    multi = result.keys_with_multiple_tokens()
    assert "CSV" in multi
    assert "PIPE" in multi
    assert "SPACED" in multi
    assert "SIMPLE" not in multi


def test_as_dict(env):
    result = tokenize(env)
    d = result.as_dict()
    assert d["CSV"] == ["a", "b", "c"]
    assert d["SIMPLE"] == ["hello"]


def test_summary_string(env):
    result = tokenize(env)
    s = result.summary()
    assert "keys tokenized" in s
    assert "total tokens" in s


def test_tokenize_value_semicolon():
    tokens = _tokenize_value("alpha;beta;gamma")
    assert tokens == ["alpha", "beta", "gamma"]
