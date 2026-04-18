import pytest
from envguard.highlighter import highlight, HighlightResult, HighlightEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret123",
        "APP_DEBUG": "true",
        "AWS_SECRET_KEY": "abc",
        "PORT": "8080",
    }


def test_returns_highlight_result(env):
    result = highlight(env, [])
    assert isinstance(result, HighlightResult)


def test_no_highlights_when_no_patterns(env):
    result = highlight(env, [])
    assert not result.has_highlights()


def test_highlight_by_key_substring(env):
    result = highlight(env, ["PASSWORD"])
    assert "DB_PASSWORD" in result.highlighted_keys()


def test_highlight_by_value_substring(env):
    result = highlight(env, ["localhost"])
    assert "DB_HOST" in result.highlighted_keys()


def test_highlight_multiple_patterns(env):
    result = highlight(env, ["PASSWORD", "SECRET"])
    keys = result.highlighted_keys()
    assert "DB_PASSWORD" in keys
    assert "AWS_SECRET_KEY" in keys


def test_keys_for_pattern(env):
    result = highlight(env, ["DB"])
    keys = result.keys_for_pattern("DB")
    assert "DB_HOST" in keys
    assert "DB_PASSWORD" in keys


def test_unmatched_key_not_highlighted(env):
    result = highlight(env, ["NONEXISTENT"])
    assert "PORT" not in result.highlighted_keys()


def test_entry_count_matches_env(env):
    result = highlight(env, ["DB"])
    assert len(result.entries) == len(env)


def test_summary_format(env):
    result = highlight(env, ["DB"])
    summary = result.summary()
    assert "/" in summary
    assert "matched" in summary


def test_glob_pattern_matches_key(env):
    result = highlight(env, ["DB_*"])
    keys = result.highlighted_keys()
    assert "DB_HOST" in keys
    assert "DB_PASSWORD" in keys
    assert "PORT" not in keys


def test_no_duplicate_patterns_per_entry(env):
    result = highlight(env, ["DB", "DB"])
    for entry in result.entries:
        assert len(entry.patterns) == len(set(entry.patterns))
