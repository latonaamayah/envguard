"""Tests for envguard.composer."""
import pytest
from envguard.composer import compose, ComposeEntry, ComposeResult


@pytest.fixture
def base() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "development"}


@pytest.fixture
def override() -> dict:
    return {"DB_HOST": "prod.db.example.com", "APP_ENV": "production", "NEW_KEY": "new"}


def test_returns_compose_result(base):
    result = compose([base])
    assert isinstance(result, ComposeResult)


def test_single_source_no_overrides(base):
    result = compose([base], sources=["base.env"])
    assert not result.has_overrides


def test_merged_contains_all_keys_from_single_source(base):
    result = compose([base])
    assert set(result.merged.keys()) == {"DB_HOST", "DB_PORT", "APP_ENV"}


def test_later_source_overrides_earlier(base, override):
    result = compose([base, override], sources=["base.env", "override.env"])
    assert result.merged["DB_HOST"] == "prod.db.example.com"
    assert result.merged["APP_ENV"] == "production"


def test_non_overridden_key_preserved(base, override):
    result = compose([base, override])
    assert result.merged["DB_PORT"] == "5432"


def test_new_key_from_later_source_included(base, override):
    result = compose([base, override])
    assert "NEW_KEY" in result.merged
    assert result.merged["NEW_KEY"] == "new"


def test_has_overrides_true_when_key_overridden(base, override):
    result = compose([base, override])
    assert result.has_overrides


def test_overridden_keys_listed(base, override):
    result = compose([base, override])
    assert "DB_HOST" in result.overridden_keys
    assert "APP_ENV" in result.overridden_keys


def test_overridden_entry_has_overridden_by_set(base, override):
    result = compose([base, override], sources=["base.env", "override.env"])
    overridden = [e for e in result.entries if e.key == "DB_HOST" and e.was_overridden]
    assert len(overridden) == 1
    assert overridden[0].overridden_by == "override.env"


def test_winning_entry_not_overridden(base, override):
    result = compose([base, override], sources=["base.env", "override.env"])
    winners = [e for e in result.entries if e.key == "DB_HOST" and not e.was_overridden]
    assert len(winners) == 1
    assert winners[0].source == "override.env"


def test_sources_recorded(base, override):
    result = compose([base, override], sources=["a.env", "b.env"])
    assert result.sources == ["a.env", "b.env"]


def test_default_source_names_generated(base):
    result = compose([base])
    assert result.sources == ["source_0"]


def test_empty_envs_returns_empty_merged():
    result = compose([])
    assert result.merged == {}
    assert not result.has_overrides


def test_summary_contains_key_count(base, override):
    result = compose([base, override])
    summary = result.summary()
    assert "4" in summary  # DB_HOST, DB_PORT, APP_ENV, NEW_KEY


def test_summary_contains_source_count(base, override):
    result = compose([base, override])
    assert "2" in result.summary()
