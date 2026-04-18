import pytest
from envguard.tracer import trace, TraceResult, TraceEntry


@pytest.fixture
def base():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "development"}


@pytest.fixture
def override():
    return {"DB_HOST": "prod.db.example.com", "APP_ENV": "production"}


def test_returns_trace_result(base):
    result = trace([base])
    assert isinstance(result, TraceResult)


def test_single_layer_no_overrides(base):
    result = trace([base])
    assert not result.has_overrides


def test_entry_count_matches_unique_keys(base, override):
    result = trace([base, override])
    assert len(result.entries) == 3


def test_overridden_key_detected(base, override):
    result = trace([base, override])
    assert "DB_HOST" in result.overridden_keys


def test_non_overridden_key_not_in_overridden(base, override):
    result = trace([base, override])
    assert "DB_PORT" not in result.overridden_keys


def test_final_value_reflects_last_layer(base, override):
    result = trace([base, override])
    d = result.as_dict()
    assert d["DB_HOST"] == "prod.db.example.com"
    assert d["APP_ENV"] == "production"


def test_non_overridden_value_preserved(base, override):
    result = trace([base, override])
    d = result.as_dict()
    assert d["DB_PORT"] == "5432"


def test_labels_used_in_source(base, override):
    result = trace([base, override], labels=["base", "prod"])
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.source == "base"
    assert entry.overridden_by == "prod"


def test_default_labels_assigned(base):
    result = trace([base])
    assert result.entries[0].source.startswith("layer_")


def test_summary_string(base, override):
    result = trace([base, override])
    s = result.summary()
    assert "3" in s
    assert "2" in s


def test_message_no_override(base):
    result = trace([base], labels=["env"])
    entry = next(e for e in result.entries if e.key == "DB_PORT")
    msg = entry.message()
    assert "5432" in msg
    assert "env" in msg
    assert "overridden" not in msg


def test_message_with_override(base, override):
    result = trace([base, override], labels=["base", "prod"])
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    msg = entry.message()
    assert "overridden" in msg
    assert "prod" in msg
