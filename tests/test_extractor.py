import pytest
from envguard.extractor import extract, ExtractResult, ExtractEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIAIOSFODNN7EXAMPLE",
        "AWS_SECRET": "wJalrXUtnFEMI",
        "APP_DEBUG": "true",
        "LOG_LEVEL": "info",
    }


def test_returns_extract_result(env):
    result = extract(env, ["DB_"])
    assert isinstance(result, ExtractResult)


def test_extract_by_prefix(env):
    result = extract(env, [r"^DB_"])
    assert result.has_matches()
    assert set(result.as_dict().keys()) == {"DB_HOST", "DB_PORT"}


def test_extract_multiple_patterns(env):
    result = extract(env, [r"^DB_", r"^AWS_"])
    keys = set(result.as_dict().keys())
    assert "DB_HOST" in keys
    assert "AWS_ACCESS_KEY" in keys


def test_unmatched_keys_populated(env):
    result = extract(env, [r"^DB_"])
    assert "APP_DEBUG" in result.unmatched_keys
    assert "LOG_LEVEL" in result.unmatched_keys


def test_no_matches_when_pattern_misses(env):
    result = extract(env, [r"^NONEXISTENT_"])
    assert not result.has_matches()
    assert len(result.unmatched_keys) == len(env)


def test_keys_for_pattern(env):
    result = extract(env, [r"^DB_", r"^AWS_"])
    db_keys = result.keys_for_pattern(r"^DB_")
    assert "DB_HOST" in db_keys
    assert "AWS_ACCESS_KEY" not in db_keys


def test_match_values_flag(env):
    result = extract(env, [r"localhost"], match_values=True)
    assert result.has_matches()
    assert "DB_HOST" in result.as_dict()


def test_match_values_does_not_match_keys(env):
    # pattern matches a key name but match_values=True so should not match
    result = extract(env, [r"^DB_HOST$"], match_values=True)
    assert not result.has_matches()


def test_summary_with_matches(env):
    result = extract(env, [r"^DB_"])
    s = result.summary()
    assert "extracted" in s
    assert "unmatched" in s


def test_summary_no_matches(env):
    result = extract(env, [r"^NOPE_"])
    assert "No keys matched" in result.summary()


def test_invalid_regex_pattern_skipped(env):
    # Should not raise, just skip the bad pattern
    result = extract(env, [r"[invalid", r"^DB_"])
    assert result.has_matches()
    assert "DB_HOST" in result.as_dict()


def test_entry_fields(env):
    result = extract(env, [r"^APP_"])
    assert len(result.matches) == 1
    entry = result.matches[0]
    assert isinstance(entry, ExtractEntry)
    assert entry.key == "APP_DEBUG"
    assert entry.value == "true"
    assert entry.pattern == r"^APP_"
