"""Tests for envguard.coercer."""
import pytest
from envguard.coercer import coerce, CoerceEntry, CoerceResult


@pytest.fixture()
def env():
    return {
        "PORT": "8080",
        "RATIO": "0.75",
        "DEBUG": "true",
        "NAME": "envguard",
        "FLAG_OFF": "false",
        "FLAG_YES": "yes",
        "FLAG_NO": "no",
    }


def test_coerce_integer(env):
    result = coerce(env, {"PORT": "int"})
    assert result.entries[0].coerced == 8080


def test_coerce_float(env):
    result = coerce(env, {"RATIO": "float"})
    assert result.entries[0].coerced == pytest.approx(0.75)


def test_coerce_bool_true(env):
    result = coerce(env, {"DEBUG": "bool"})
    assert result.entries[0].coerced is True


def test_coerce_bool_false(env):
    result = coerce(env, {"FLAG_OFF": "bool"})
    assert result.entries[0].coerced is False


def test_coerce_bool_yes(env):
    result = coerce(env, {"FLAG_YES": "bool"})
    assert result.entries[0].coerced is True


def test_coerce_bool_no(env):
    result = coerce(env, {"FLAG_NO": "bool"})
    assert result.entries[0].coerced is False


def test_coerce_str(env):
    result = coerce(env, {"NAME": "str"})
    assert result.entries[0].coerced == "envguard"


def test_coerce_invalid_int(env):
    result = coerce({"PORT": "not_a_number"}, {"PORT": "int"})
    assert result.has_errors
    assert "PORT" in result.failed_keys


def test_coerce_invalid_bool(env):
    result = coerce({"FLAG": "maybe"}, {"FLAG": "bool"})
    assert result.has_errors


def test_coerce_unknown_type(env):
    result = coerce(env, {"PORT": "datetime"})
    assert result.has_errors
    assert result.entries[0].error != ""


def test_as_dict_excludes_failed(env):
    result = coerce({"PORT": "8080", "X": "bad"}, {"PORT": "int", "X": "float"})
    d = result.as_dict()
    assert "PORT" in d
    assert "X" not in d


def test_summary_counts(env):
    result = coerce({"PORT": "8080", "X": "bad"}, {"PORT": "int", "X": "float"})
    assert "1 coerced successfully" in result.summary()
    assert "1 failed" in result.summary()


def test_changed_flag_true(env):
    result = coerce(env, {"PORT": "int"})
    assert result.entries[0].changed is True


def test_changed_flag_false_for_str(env):
    result = coerce(env, {"NAME": "str"})
    assert result.entries[0].changed is False


def test_no_errors_all_valid(env):
    result = coerce(env, {"PORT": "int", "RATIO": "float", "DEBUG": "bool"})
    assert not result.has_errors
