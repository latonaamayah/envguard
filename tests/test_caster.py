import pytest
from envguard.caster import cast, CastResult


@pytest.fixture
def env():
    return {
        "PORT": "8080",
        "RATE": "3.14",
        "DEBUG": "true",
        "NAME": "myapp",
        "RETRIES": "bad",
    }


def test_returns_cast_result(env):
    result = cast(env, {})
    assert isinstance(result, CastResult)


def test_cast_integer(env):
    result = cast(env, {"PORT": "int"})
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.cast == 8080
    assert entry.error is None


def test_cast_float(env):
    result = cast(env, {"RATE": "float"})
    entry = next(e for e in result.entries if e.key == "RATE")
    assert entry.cast == pytest.approx(3.14)


def test_cast_bool_true(env):
    result = cast(env, {"DEBUG": "bool"})
    entry = next(e for e in result.entries if e.key == "DEBUG")
    assert entry.cast is True


def test_cast_bool_false():
    result = cast({"ENABLED": "false"}, {"ENABLED": "bool"})
    entry = result.entries[0]
    assert entry.cast is False


def test_cast_str_default(env):
    result = cast({"NAME": "myapp"}, {})
    entry = result.entries[0]
    assert entry.cast == "myapp"
    assert entry.target_type == "str"


def test_cast_error_recorded(env):
    result = cast({"RETRIES": "bad"}, {"RETRIES": "int"})
    entry = result.entries[0]
    assert entry.error is not None
    assert entry.key == "RETRIES"


def test_has_errors_true(env):
    result = cast({"X": "notanint"}, {"X": "int"})
    assert result.has_errors


def test_has_errors_false():
    result = cast({"X": "42"}, {"X": "int"})
    assert not result.has_errors


def test_failed_keys(env):
    result = cast({"A": "bad", "B": "1"}, {"A": "int", "B": "int"})
    assert result.failed_keys == ["A"]


def test_as_dict_excludes_errors():
    result = cast({"A": "bad", "B": "2"}, {"A": "int", "B": "int"})
    d = result.as_dict
    assert "A" not in d
    assert d["B"] == 2


def test_summary_message():
    result = cast({"A": "1", "B": "bad"}, {"A": "int", "B": "int"})
    assert "2 keys" in result.summary()
    assert "1 cast error" in result.summary()
