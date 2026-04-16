import pytest
from envguard.scoper import scope, ScopeResult, ScopeEntry


@pytest.fixture
def env():
    return {
        "TEST_DB_URL": "sqlite://",
        "PROD_API_KEY": "secret",
        "DEV_DEBUG": "true",
        "STAGING_HOST": "staging.example.com",
        "APP_NAME": "envguard",
        "PORT": "8080",
    }


def test_returns_scope_result(env):
    result = scope(env)
    assert isinstance(result, ScopeResult)


def test_test_scope_detected(env):
    result = scope(env)
    assert "TEST_DB_URL" in result.keys_for_scope("test")


def test_prod_scope_detected(env):
    result = scope(env)
    assert "PROD_API_KEY" in result.keys_for_scope("production")


def test_dev_scope_detected(env):
    result = scope(env)
    assert "DEV_DEBUG" in result.keys_for_scope("development")


def test_staging_scope_detected(env):
    result = scope(env)
    assert "STAGING_HOST" in result.keys_for_scope("staging")


def test_unscoped_keys_populated(env):
    result = scope(env)
    assert "APP_NAME" in result.unscoped
    assert "PORT" in result.unscoped


def test_has_scoped_true(env):
    result = scope(env)
    assert result.has_scoped() is True


def test_has_scoped_false():
    result = scope({"HOST": "localhost", "PORT": "5432"})
    assert result.has_scoped() is False


def test_all_scopes_returns_set(env):
    result = scope(env)
    scopes = result.all_scopes()
    assert "test" in scopes
    assert "production" in scopes
    assert "development" in scopes
    assert "staging" in scopes


def test_summary_string(env):
    result = scope(env)
    s = result.summary()
    assert "scoped" in s or "/" in s


def test_empty_env():
    result = scope({})
    assert result.has_scoped() is False
    assert result.unscoped == []
