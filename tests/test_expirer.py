from datetime import datetime, timedelta
import pytest
from envguard.expirer import expire, ExpireResult


@pytest.fixture
def env():
    return {
        "API_KEY": "abc123",
        "DB_PASSWORD": "secret",
        "OAUTH_TOKEN": "tok_xyz",
        "APP_NAME": "myapp",
    }


NOW = datetime(2024, 6, 1, 12, 0, 0)
PAST = (NOW - timedelta(days=10)).isoformat()
SOON = (NOW + timedelta(days=3)).isoformat()
FUTURE = (NOW + timedelta(days=30)).isoformat()


def test_returns_expire_result(env):
    result = expire(env, {}, reference_date=NOW)
    assert isinstance(result, ExpireResult)


def test_no_expiry_map_no_expired(env):
    result = expire(env, {}, reference_date=NOW)
    assert not result.has_expired


def test_expired_key_detected(env):
    result = expire(env, {"API_KEY": PAST}, reference_date=NOW)
    assert result.has_expired
    assert "API_KEY" in result.expired_keys


def test_future_key_not_expired(env):
    result = expire(env, {"API_KEY": FUTURE}, reference_date=NOW)
    assert not result.has_expired
    assert "API_KEY" not in result.expired_keys


def test_expiring_soon_within_7_days(env):
    result = expire(env, {"API_KEY": SOON}, reference_date=NOW)
    assert "API_KEY" in result.expiring_soon


def test_future_not_in_expiring_soon(env):
    result = expire(env, {"API_KEY": FUTURE}, reference_date=NOW)
    assert "API_KEY" not in result.expiring_soon


def test_days_remaining_correct(env):
    result = expire(env, {"API_KEY": FUTURE}, reference_date=NOW)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert entry.days_remaining == 29


def test_no_expiry_entry_has_none_days(env):
    result = expire(env, {}, reference_date=NOW)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert entry.days_remaining is None
    assert entry.expires_at is None


def test_invalid_date_string_treated_as_no_expiry(env):
    result = expire(env, {"API_KEY": "not-a-date"}, reference_date=NOW)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert not entry.is_expired
    assert entry.expires_at is None


def test_summary_string(env):
    result = expire(env, {"API_KEY": PAST, "DB_PASSWORD": SOON}, reference_date=NOW)
    s = result.summary()
    assert "expired" in s
    assert "expiring soon" in s


def test_entry_message_expired(env):
    result = expire(env, {"API_KEY": PAST}, reference_date=NOW)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert "expired" in entry.message


def test_entry_message_days_remaining(env):
    result = expire(env, {"API_KEY": FUTURE}, reference_date=NOW)
    entry = next(e for e in result.entries if e.key == "API_KEY")
    assert "day(s)" in entry.message
