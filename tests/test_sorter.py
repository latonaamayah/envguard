"""Tests for envguard.sorter."""
import pytest
from envguard.sorter import sort, SortResult


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "APP_NAME": "myapp",
        "DB_PORT": "5432",
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
        "Z_LAST": "yes",
    }


def test_alpha_sort_returns_sorted_keys(env):
    result = sort(env, strategy="alpha")
    assert result.order == sorted(env.keys())


def test_alpha_sort_reverse(env):
    result = sort(env, strategy="alpha", reverse=True)
    assert result.order == sorted(env.keys(), reverse=True)


def test_sorted_vars_matches_order(env):
    result = sort(env, strategy="alpha")
    assert list(result.sorted_vars.keys()) == result.order


def test_sorted_vars_preserves_values(env):
    result = sort(env, strategy="alpha")
    for k, v in result.sorted_vars.items():
        assert env[k] == v


def test_has_changes_when_order_differs(env):
    result = sort(env, strategy="alpha")
    # original dict is not alphabetically sorted
    assert result.has_changes is True


def test_no_changes_when_already_sorted():
    already = {"A": "1", "B": "2", "C": "3"}
    result = sort(already, strategy="alpha")
    assert result.has_changes is False


def test_group_sort_clusters_by_prefix(env):
    result = sort(env, strategy="group", groups=["APP", "DB", "LOG"])
    order = result.order
    app_indices = [order.index(k) for k in order if k.startswith("APP_")]
    db_indices = [order.index(k) for k in order if k.startswith("DB_")]
    assert max(app_indices) < min(db_indices)


def test_length_sort_orders_by_key_length(env):
    result = sort(env, strategy="length")
    lengths = [len(k) for k in result.order]
    assert lengths == sorted(lengths)


def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown sort strategy"):
        sort({"A": "1"}, strategy="random")


def test_summary_no_changes():
    env = {"A": "1", "B": "2"}
    result = sort(env, strategy="alpha")
    assert "no changes" in result.summary.lower()


def test_summary_with_changes(env):
    result = sort(env, strategy="alpha")
    assert "sorted" in result.summary.lower()
    assert str(len(env)) in result.summary
