"""Tests for envguard.splitter."""
import pytest
from envguard.splitter import SplitResult, split


@pytest.fixture()
def env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "APP_ENV": "production",
        "PORT": "8080",
    }


def test_returns_split_result(env):
    result = split(env)
    assert isinstance(result, SplitResult)


def test_groups_by_prefix(env):
    result = split(env)
    assert "DB" in result.group_names()
    assert "AWS" in result.group_names()
    assert "APP" in result.group_names()


def test_db_group_has_three_keys(env):
    result = split(env)
    assert len(result.groups["DB"]) == 3


def test_aws_group_has_two_keys(env):
    result = split(env)
    assert len(result.groups["AWS"]) == 2


def test_no_prefix_key_goes_to_ungrouped(env):
    result = split(env)
    assert "PORT" in result.ungrouped


def test_has_groups_true_when_groups_exist(env):
    result = split(env)
    assert result.has_groups()


def test_has_groups_false_for_empty():
    result = split({})
    assert not result.has_groups()


def test_total_keys_matches_input(env):
    result = split(env)
    assert result.total_keys() == len(env)


def test_filter_by_explicit_prefixes(env):
    result = split(env, prefixes=["DB"])
    assert list(result.group_names()) == ["DB"]
    assert "AWS_KEY" in result.ungrouped
    assert "AWS_SECRET" in result.ungrouped


def test_non_matching_prefix_goes_to_ungrouped(env):
    result = split(env, prefixes=["DB"])
    assert "APP_ENV" in result.ungrouped


def test_summary_contains_group_names(env):
    result = split(env)
    s = result.summary()
    assert "DB" in s
    assert "AWS" in s


def test_summary_empty_env():
    result = split({})
    assert result.summary() == "no keys"


def test_values_preserved(env):
    result = split(env)
    assert result.groups["DB"]["DB_HOST"] == "localhost"
    assert result.groups["AWS"]["AWS_SECRET"] == "xyz"


def test_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "PLAIN": "val"}
    result = split(env, separator=".")
    assert "DB" in result.group_names()
    assert "PLAIN" in result.ungrouped
