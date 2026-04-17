import pytest
from envguard.pruner import prune, PruneResult


@pytest.fixture
def env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "",
        "API_KEY": "changeme",
        "DEBUG": "true",
        "SECRET": "placeholder",
        "PORT": "8080",
    }


def test_returns_prune_result(env):
    result = prune(env)
    assert isinstance(result, PruneResult)


def test_empty_value_pruned_by_default(env):
    result = prune(env)
    assert "DB_PASSWORD" in result.pruned_keys()


def test_placeholder_value_pruned_by_default(env):
    result = prune(env)
    assert "API_KEY" in result.pruned_keys()
    assert "SECRET" in result.pruned_keys()


def test_clean_values_kept(env):
    result = prune(env)
    assert "APP_NAME" in result.kept
    assert "DEBUG" in result.kept
    assert "PORT" in result.kept


def test_has_pruned_true(env):
    result = prune(env)
    assert result.has_pruned() is True


def test_has_pruned_false():
    result = prune({"HOST": "localhost", "PORT": "5432"})
    assert result.has_pruned() is False


def test_disable_empty_pruning(env):
    result = prune(env, empty=False)
    assert "DB_PASSWORD" not in result.pruned_keys()
    assert "DB_PASSWORD" in result.kept


def test_disable_placeholder_pruning(env):
    result = prune(env, placeholders=False)
    assert "API_KEY" not in result.pruned_keys()


def test_explicit_keys_pruned(env):
    result = prune(env, keys={"APP_NAME", "PORT"})
    assert "APP_NAME" in result.pruned_keys()
    assert "PORT" in result.pruned_keys()


def test_explicit_key_reason(env):
    result = prune(env, keys={"APP_NAME"})
    entry = next(e for e in result.pruned if e.key == "APP_NAME")
    assert entry.reason == "explicitly selected"


def test_summary_no_pruned():
    result = prune({"X": "y"})
    assert result.summary() == "No variables pruned."


def test_summary_with_pruned(env):
    result = prune(env)
    assert "Pruned" in result.summary()
