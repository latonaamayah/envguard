import pytest
from envguard.cascader import cascade, CascadeEntry, CascadeResult


@pytest.fixture
def base() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "development"}


@pytest.fixture
def override() -> dict:
    return {"DB_HOST": "prod.db.example.com", "APP_SECRET": "s3cr3t"}


def test_returns_cascade_result(base):
    result = cascade([base])
    assert isinstance(result, CascadeResult)


def test_single_layer_no_overrides(base):
    result = cascade([base])
    assert not result.has_overrides


def test_merged_contains_all_keys(base):
    result = cascade([base])
    assert set(result.merged.keys()) == {"DB_HOST", "DB_PORT", "APP_ENV"}


def test_merged_values_match_layer(base):
    result = cascade([base])
    assert result.merged["DB_HOST"] == "localhost"


def test_two_layers_override_detected(base, override):
    result = cascade([base, override])
    assert result.has_overrides


def test_overridden_keys_listed(base, override):
    result = cascade([base, override])
    assert "DB_HOST" in result.overridden_keys


def test_non_overridden_key_not_in_overridden_keys(base, override):
    result = cascade([base, override])
    assert "DB_PORT" not in result.overridden_keys


def test_later_layer_wins(base, override):
    result = cascade([base, override])
    assert result.merged["DB_HOST"] == "prod.db.example.com"


def test_new_key_from_later_layer(base, override):
    result = cascade([base, override])
    assert result.merged["APP_SECRET"] == "s3cr3t"


def test_layer_count_single(base):
    result = cascade([base])
    assert result.layer_count == 1


def test_layer_count_two(base, override):
    result = cascade([base, override])
    assert result.layer_count == 2


def test_custom_layer_names(base, override):
    result = cascade([base, override], layer_names=["base", "production"])
    overridden = [e for e in result.entries if e.was_overridden]
    assert overridden[0].source == "production"


def test_default_layer_names_generated(base):
    result = cascade([base])
    assert result.entries[0].source == "layer_0"


def test_entry_message_no_override(base):
    result = cascade([base], layer_names=["base"])
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert "resolved from layer 'base'" in entry.message


def test_entry_message_override(base, override):
    result = cascade([base, override], layer_names=["base", "prod"])
    entry = next(
        e for e in result.entries if e.key == "DB_HOST" and e.was_overridden
    )
    assert "overridden in layer 'prod'" in entry.message
    assert "localhost" in entry.message


def test_summary_string(base, override):
    result = cascade([base, override])
    s = result.summary()
    assert "key(s)" in s
    assert "layer(s)" in s
    assert "override(s)" in s


def test_empty_layers_returns_empty_result():
    result = cascade([])
    assert result.merged == {}
    assert result.entries == []
