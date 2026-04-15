import pytest
from envguard.classifier import classify, ClassifyEntry


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY_ID": "AKIA123",
        "AWS_REGION": "us-east-1",
        "JWT_SECRET": "supersecret",
        "LOG_LEVEL": "INFO",
        "SMTP_HOST": "smtp.example.com",
        "FEATURE_DARK_MODE": "true",
        "APP_NAME": "myapp",
        "ENVIRONMENT": "production",
    }


def test_classify_returns_result(env):
    result = classify(env)
    assert result is not None


def test_database_category_detected(env):
    result = classify(env)
    assert "database" in result.categories
    keys = [e.key for e in result.categories["database"]]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_cloud_category_detected(env):
    result = classify(env)
    assert "cloud" in result.categories
    keys = [e.key for e in result.categories["cloud"]]
    assert "AWS_ACCESS_KEY_ID" in keys
    assert "AWS_REGION" in keys


def test_auth_category_detected(env):
    result = classify(env)
    assert "auth" in result.categories
    keys = [e.key for e in result.categories["auth"]]
    assert "JWT_SECRET" in keys


def test_logging_category_detected(env):
    result = classify(env)
    assert "logging" in result.categories
    keys = [e.key for e in result.categories["logging"]]
    assert "LOG_LEVEL" in keys


def test_email_category_detected(env):
    result = classify(env)
    assert "email" in result.categories
    keys = [e.key for e in result.categories["email"]]
    assert "SMTP_HOST" in keys


def test_feature_category_detected(env):
    result = classify(env)
    assert "feature" in result.categories
    keys = [e.key for e in result.categories["feature"]]
    assert "FEATURE_DARK_MODE" in keys


def test_uncategorized_keys(env):
    result = classify(env)
    uncategorized_keys = [e.key for e in result.uncategorized]
    assert "APP_NAME" in uncategorized_keys
    assert "ENVIRONMENT" in uncategorized_keys


def test_has_categories_true(env):
    result = classify(env)
    assert result.has_categories() is True


def test_has_categories_false_empty():
    result = classify({})
    assert result.has_categories() is False


def test_category_names_sorted(env):
    result = classify(env)
    names = result.category_names()
    assert names == sorted(names)


def test_summary_contains_counts(env):
    result = classify(env)
    summary = result.summary()
    assert "classified" in summary
    assert "uncategorized" in summary


def test_entry_fields(env):
    result = classify(env)
    entry = result.categories["database"][0]
    assert isinstance(entry, ClassifyEntry)
    assert entry.key
    assert entry.category == "database"
