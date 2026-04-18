"""Tests for envguard.grouper."""
import pytest
from envguard.grouper import group, GroupResult


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "secret",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_groups_by_prefix(env):
    result = group(env)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_db_group_has_three_entries(env):
    result = group(env)
    keys = [k for k, _ in result.groups["DB"]]
    assert sorted(keys) == ["DB_HOST", "DB_NAME", "DB_PORT"]


def test_aws_group_has_two_entries(env):
    result = group(env)
    assert len(result.groups["AWS"]) == 2


def test_no_prefix_keys_go_to_ungrouped(env):
    result = group(env)
    ungrouped_keys = [k for k, _ in result.ungrouped]
    assert "PORT" in ungrouped_keys
    assert "DEBUG" in ungrouped_keys


def test_has_groups_true_when_groups_exist(env):
    result = group(env)
    assert result.has_groups is True


def test_has_groups_false_for_empty_env():
    result = group({})
    assert result.has_groups is False


def test_group_names_sorted(env):
    result = group(env)
    assert result.group_names == sorted(result.group_names)


def test_min_group_size_filters_small_groups():
    env = {"A_ONE": "1", "B_ONE": "1", "B_TWO": "2"}
    result = group(env, min_group_size=2)
    assert "B" in result.groups
    assert "A" not in result.groups
    ungrouped_keys = [k for k, _ in result.ungrouped]
    assert "A_ONE" in ungrouped_keys


def test_summary_contains_group_names(env):
    result = group(env)
    summary = result.summary()
    assert "DB" in summary
    assert "AWS" in summary


def test_summary_mentions_ungrouped(env):
    result = group(env)
    summary = result.summary()
    assert "ungrouped" in summary


def test_single_key_no_separator_goes_ungrouped():
    result = group({"NOPREFIX": "val"})
    assert result.ungrouped == [("NOPREFIX", "val")]
    assert not result.groups


def test_custom_separator():
    env = {"APP.HOST": "localhost", "APP.PORT": "80", "STANDALONE": "yes"}
    result = group(env, separator=".")
    assert "APP" in result.groups
    assert len(result.groups["APP"]) == 2


def test_group_result_total_grouped_count(env):
    """GroupResult should report the correct total number of grouped keys."""
    result = group(env)
    expected = sum(len(entries) for entries in result.groups.values())
    assert result.total_grouped == expected


def test_group_result_total_grouped_excludes_ungrouped(env):
    """total_grouped should not include ungrouped keys."""
    result = group(env)
    ungrouped_count = len(result.ungrouped)
    assert result.total_grouped + ungrouped_count == len(env)
