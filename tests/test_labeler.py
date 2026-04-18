import pytest
from envguard.labeler import label, LabelEntry, LabelResult


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY": "AKIA123",
        "APP_ENV": "production",
        "PORT": "8080",
    }


@pytest.fixture
def rules():
    return {
        "database": ["DB_*"],
        "sensitive": ["DB_PASSWORD", "AWS_ACCESS_KEY"],
        "cloud": ["AWS_*"],
        "config": ["APP_ENV", "PORT"],
    }


def test_returns_label_result(env, rules):
    result = label(env, rules)
    assert isinstance(result, LabelResult)


def test_entry_count_matches_env(env, rules):
    result = label(env, rules)
    assert len(result.entries) == len(env)


def test_has_labels_true(env, rules):
    result = label(env, rules)
    assert result.has_labels() is True


def test_has_labels_false_empty_rules(env):
    result = label(env, {})
    assert result.has_labels() is False


def test_database_label_applied(env, rules):
    result = label(env, rules)
    db_keys = result.keys_for_label("database")
    assert "DB_HOST" in db_keys
    assert "DB_PASSWORD" in db_keys
    assert "PORT" not in db_keys


def test_sensitive_label_applied(env, rules):
    result = label(env, rules)
    sensitive = result.keys_for_label("sensitive")
    assert "DB_PASSWORD" in sensitive
    assert "AWS_ACCESS_KEY" in sensitive
    assert "DB_HOST" not in sensitive


def test_cloud_label_applied(env, rules):
    result = label(env, rules)
    cloud = result.keys_for_label("cloud")
    assert "AWS_ACCESS_KEY" in cloud
    assert "DB_HOST" not in cloud


def test_multiple_labels_on_same_key(env, rules):
    result = label(env, rules)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert "database" in entry.labels
    assert "sensitive" in entry.labels


def test_has_label_method(env, rules):
    result = label(env, rules)
    entry = next(e for e in result.entries if e.key == "AWS_ACCESS_KEY")
    assert entry.has_label("sensitive") is True
    assert entry.has_label("database") is False


def test_all_labels_returns_unique(env, rules):
    result = label(env, rules)
    all_lbls = result.all_labels()
    assert len(all_lbls) == len(set(all_lbls))
    assert "database" in all_lbls
    assert "sensitive" in all_lbls


def test_summary_string(env, rules):
    result = label(env, rules)
    s = result.summary()
    assert "label" in s
