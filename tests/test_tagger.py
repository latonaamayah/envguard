"""Tests for envguard.tagger."""
import pytest
from envguard.tagger import tag, TagEntry, TagResult


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "s3cr3t",
        "APP_NAME": "envguard",
        "LOG_LEVEL": "INFO",
    }


@pytest.fixture
def rules():
    return {
        "database": ["DB_"],
        "cloud": ["AWS_"],
        "app": ["APP_", "LOG_"],
    }


def test_tagged_count(env, rules):
    result = tag(env, rules)
    assert len(result.tagged) == 6


def test_untagged_is_empty_when_all_match(env, rules):
    result = tag(env, rules)
    assert result.untagged_keys == []


def test_untagged_key_when_no_rule_matches(env, rules):
    env["UNKNOWN_VAR"] = "xyz"
    result = tag(env, rules)
    assert "UNKNOWN_VAR" in result.untagged_keys


def test_db_keys_tagged_database(env, rules):
    result = tag(env, rules)
    db_keys = result.keys_for_tag("database")
    assert "DB_HOST" in db_keys
    assert "DB_PORT" in db_keys


def test_aws_keys_tagged_cloud(env, rules):
    result = tag(env, rules)
    cloud_keys = result.keys_for_tag("cloud")
    assert "AWS_ACCESS_KEY" in cloud_keys
    assert "AWS_SECRET" in cloud_keys


def test_all_tags_returns_all_labels(env, rules):
    result = tag(env, rules)
    assert result.all_tags() == {"database", "cloud", "app"}


def test_has_tagged_true(env, rules):
    result = tag(env, rules)
    assert result.has_tagged() is True


def test_has_tagged_false_empty_env():
    result = tag({}, {"database": ["DB_"]})
    assert result.has_tagged() is False


def test_summary_contains_counts(env, rules):
    env["MYSTERY"] = "42"
    result = tag(env, rules)
    s = result.summary()
    assert "tagged" in s
    assert "untagged" in s


def test_empty_rules_all_untagged(env):
    result = tag(env, {})
    assert len(result.untagged_keys) == len(env)
    assert result.tagged == []


def test_key_case_insensitive_matching():
    env = {"db_host": "localhost"}
    result = tag(env, {"database": ["DB_"]})
    assert result.keys_for_tag("database") == ["db_host"]
