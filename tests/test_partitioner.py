"""Tests for envguard.partitioner."""
import pytest
from envguard.partitioner import partition, PartitionEntry, PartitionResult


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET_KEY": "secret",
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
    }


def test_returns_partition_result(env):
    result = partition(env, {})
    assert isinstance(result, PartitionResult)


def test_entry_count_matches_env(env):
    result = partition(env, {})
    assert len(result.entries) == len(env)


def test_no_rules_puts_all_in_default(env):
    result = partition(env, {})
    assert result.bucket_names() == ["default"]
    assert len(result.keys_for_bucket("default")) == len(env)


def test_db_rule_creates_db_bucket(env):
    result = partition(env, {"database": r"^DB_"})
    assert "database" in result.bucket_names()
    assert set(result.keys_for_bucket("database")) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_aws_rule_creates_aws_bucket(env):
    result = partition(env, {"cloud": r"^AWS_"})
    assert "cloud" in result.bucket_names()
    assert set(result.keys_for_bucket("cloud")) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_multiple_rules_partition_correctly(env):
    rules = {"database": r"^DB_", "cloud": r"^AWS_"}
    result = partition(env, rules)
    assert "database" in result.bucket_names()
    assert "cloud" in result.bucket_names()
    assert "default" in result.bucket_names()


def test_default_bucket_contains_unmatched(env):
    rules = {"database": r"^DB_", "cloud": r"^AWS_"}
    result = partition(env, rules)
    default_keys = set(result.keys_for_bucket("default"))
    assert default_keys == {"APP_ENV", "LOG_LEVEL"}


def test_custom_default_bucket_name(env):
    result = partition(env, {}, default_bucket="misc")
    assert "misc" in result.bucket_names()
    assert "default" not in result.bucket_names()


def test_get_bucket_returns_key_value_map(env):
    result = partition(env, {"database": r"^DB_"})
    db = result.get_bucket("database")
    assert db["DB_HOST"] == "localhost"
    assert db["DB_PORT"] == "5432"


def test_has_buckets_true_with_rules(env):
    result = partition(env, {"database": r"^DB_"})
    assert result.has_buckets() is True


def test_has_buckets_false_empty_env():
    result = partition({}, {})
    assert result.has_buckets() is False


def test_summary_string(env):
    rules = {"database": r"^DB_", "cloud": r"^AWS_"}
    result = partition(env, rules)
    s = result.summary()
    assert "7" in s
    assert "3" in s


def test_entry_str_representation(env):
    result = partition({"DB_HOST": "localhost"}, {"database": r"^DB_"})
    entry = result.entries[0]
    assert "DB_HOST" in str(entry)
    assert "database" in str(entry)


def test_first_matching_rule_wins():
    env = {"DB_AWS_HOST": "host"}
    rules = {"database": r"^DB_", "cloud": r"AWS"}
    result = partition(env, rules)
    # first rule (database) should win
    assert result.keys_for_bucket("database") == ["DB_AWS_HOST"]
    assert result.keys_for_bucket("cloud") == []
