"""Tests for envguard.sanitizer."""
import pytest
from envguard.sanitizer import sanitize, SanitizeResult, SanitizeEntry


@pytest.fixture
def env():
    return {
        "APP_NAME": "  myapp  ",
        "DB_PASS": '"secret"',
        "API_KEY": "key\nwith\nnewlines",
        "PORT": "8080",
        "TOKEN": "abc\x00def",
    }


def test_returns_sanitize_result(env):
    result = sanitize(env)
    assert isinstance(result, SanitizeResult)


def test_default_strip_rule(env):
    result = sanitize({"KEY": "  hello  "}, rules=["strip"])
    assert result.as_dict["KEY"] == "hello"


def test_no_change_for_clean_value():
    result = sanitize({"KEY": "clean"}, rules=["strip"])
    assert not result.has_changes


def test_strip_quotes_double(env):
    result = sanitize({"DB_PASS": '"secret"'}, rules=["strip_quotes"])
    assert result.as_dict["DB_PASS"] == "secret"


def test_strip_quotes_single():
    result = sanitize({"KEY": "'value'"}, rules=["strip_quotes"])
    assert result.as_dict["KEY"] == "value"


def test_remove_newlines(env):
    result = sanitize({"API_KEY": "key\nwith\nnewlines"}, rules=["remove_newlines"])
    assert "\n" not in result.as_dict["API_KEY"]


def test_remove_nulls(env):
    result = sanitize({"TOKEN": "abc\x00def"}, rules=["remove_nulls"])
    assert "\x00" not in result.as_dict["TOKEN"]


def test_alphanumeric_only():
    result = sanitize({"KEY": "hello-world_123!"}, rules=["alphanumeric_only"])
    assert result.as_dict["KEY"] == "helloworld123"


def test_lowercase_rule():
    result = sanitize({"KEY": "HELLO"}, rules=["lowercase"])
    assert result.as_dict["KEY"] == "hello"


def test_uppercase_rule():
    result = sanitize({"KEY": "hello"}, rules=["uppercase"])
    assert result.as_dict["KEY"] == "HELLO"


def test_has_changes_when_value_modified():
    result = sanitize({"KEY": "  val  "}, rules=["strip"])
    assert result.has_changes
    assert "KEY" in result.changed_keys


def test_per_key_rules_override_global():
    env = {"GLOBAL": "  trim me  ", "SPECIAL": "UPPER"}
    result = sanitize(env, rules=["strip"], key_rules={"SPECIAL": ["lowercase"]})
    assert result.as_dict["GLOBAL"] == "trim me"
    assert result.as_dict["SPECIAL"] == "upper"


def test_summary_no_changes():
    result = sanitize({"KEY": "clean"}, rules=["strip"])
    assert "No sanitization" in result.summary()


def test_summary_with_changes():
    result = sanitize({"KEY": "  val  "}, rules=["strip"])
    assert "1 value(s) sanitized" in result.summary()


def test_multiple_rules_applied_in_order():
    result = sanitize({"KEY": '  "hello"  '}, rules=["strip", "strip_quotes"])
    assert result.as_dict["KEY"] == "hello"


def test_entry_changed_flag():
    result = sanitize({"KEY": "  val  "}, rules=["strip"])
    entry = result.entries[0]
    assert isinstance(entry, SanitizeEntry)
    assert entry.changed is True
    assert entry.original == "  val  "
    assert entry.sanitized == "val"
