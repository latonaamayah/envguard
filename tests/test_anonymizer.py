import pytest
from envguard.anonymizer import anonymize, AnonymizeResult, _is_sensitive


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "AUTH_TOKEN": "tok_xyz",
    }


def test_returns_anonymize_result(env):
    result = anonymize(env)
    assert isinstance(result, AnonymizeResult)


def test_sensitive_keys_anonymized(env):
    result = anonymize(env)
    d = result.as_dict()
    assert d["DB_PASSWORD"] == "***"
    assert d["API_KEY"] == "***"
    assert d["AUTH_TOKEN"] == "***"


def test_non_sensitive_keys_unchanged(env):
    result = anonymize(env)
    d = result.as_dict()
    assert d["DB_HOST"] == "localhost"
    assert d["APP_NAME"] == "myapp"


def test_has_anonymized_true(env):
    result = anonymize(env)
    assert result.has_anonymized is True


def test_has_anonymized_false():
    result = anonymize({"HOST": "localhost", "PORT": "5432"})
    assert result.has_anonymized is False


def test_anonymized_keys_list(env):
    result = anonymize(env)
    assert "DB_PASSWORD" in result.anonymized_keys
    assert "DB_HOST" not in result.anonymized_keys


def test_custom_placeholder(env):
    result = anonymize(env, placeholder="[REDACTED]")
    d = result.as_dict()
    assert d["DB_PASSWORD"] == "[REDACTED]"


def test_explicit_keys_override(env):
    result = anonymize(env, keys=["DB_HOST"])
    d = result.as_dict()
    assert d["DB_HOST"] == "***"
    assert d["DB_PASSWORD"] == "supersecret"


def test_summary_with_changes(env):
    result = anonymize(env)
    assert "anonymized" in result.summary()


def test_summary_no_changes():
    result = anonymize({"HOST": "localhost"})
    assert result.summary() == "No values anonymized."


def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("AUTH_TOKEN") is True


def test_is_not_sensitive_host():
    assert _is_sensitive("DB_HOST") is False
