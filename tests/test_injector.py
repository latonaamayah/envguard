"""Tests for envguard.injector."""
import pytest
from envguard.injector import inject, InjectResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def env():
    return {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_inject_into_empty_target_injects_all(env):
    result = inject(env)
    assert len(result.injected) == 3
    assert result.has_injected()


def test_inject_returns_correct_values(env):
    result = inject(env)
    d = result.as_dict()
    assert d["APP_ENV"] == "production"
    assert d["PORT"] == "8080"


def test_inject_skips_existing_key_when_no_overwrite(env):
    target = {"PORT": "3000"}
    result = inject(env, target)
    assert "PORT" in result.skipped
    assert target["PORT"] == "3000"


def test_inject_overwrites_when_flag_set(env):
    target = {"PORT": "3000"}
    result = inject(env, target, overwrite=True)
    assert target["PORT"] == "8080"
    assert not result.skipped


def test_inject_overwritten_flag_set_correctly(env):
    target = {"PORT": "3000"}
    result = inject(env, target, overwrite=True)
    overwritten = [e for e in result.injected if e.key == "PORT"]
    assert overwritten[0].overwritten is True


def test_inject_new_key_not_marked_overwritten(env):
    result = inject(env)
    for entry in result.injected:
        assert entry.overwritten is False


def test_inject_empty_env_produces_no_injected():
    result = inject({})
    assert not result.has_injected()
    assert not result.has_skipped()


def test_summary_shows_injected_count(env):
    result = inject(env)
    assert "3 injected" in result.summary()


def test_summary_shows_skipped_when_present(env):
    target = {"PORT": "3000"}
    result = inject(env, target)
    assert "skipped" in result.summary()


def test_inject_modifies_target_in_place(env):
    target = {}
    inject(env, target)
    assert target["APP_ENV"] == "production"
