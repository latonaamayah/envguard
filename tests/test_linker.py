import pytest
from envguard.linker import link, LinkEntry, LinkResult


@pytest.fixture
def env():
    return {
        "BASE_URL": "https://example.com",
        "API_URL": "${BASE_URL}/api",
        "CALLBACK": "${API_URL}/callback",
        "BROKEN_REF": "${MISSING_VAR}/path",
        "NO_REF": "plain-value",
        "DOUBLE_REF": "${BASE_URL}/${MISSING_ONE}",
    }


def test_returns_link_result(env):
    result = link(env)
    assert isinstance(result, LinkResult)


def test_entry_count_matches_env(env):
    result = link(env)
    assert len(result.entries) == len(env)


def test_no_ref_has_no_references(env):
    result = link(env)
    entry = next(e for e in result.entries if e.key == "NO_REF")
    assert entry.references == []
    assert entry.broken == []


def test_valid_reference_detected(env):
    result = link(env)
    entry = next(e for e in result.entries if e.key == "API_URL")
    assert "BASE_URL" in entry.references
    assert entry.broken == []


def test_broken_reference_detected(env):
    result = link(env)
    entry = next(e for e in result.entries if e.key == "BROKEN_REF")
    assert "MISSING_VAR" in entry.broken
    assert entry.has_broken is True


def test_has_broken_true_when_any_broken(env):
    result = link(env)
    assert result.has_broken is True


def test_has_broken_false_for_clean_env():
    clean = {"A": "hello", "B": "${A}-world"}
    result = link(clean)
    assert result.has_broken is False


def test_broken_keys_list(env):
    result = link(env)
    assert "BROKEN_REF" in result.broken_keys
    assert "DOUBLE_REF" in result.broken_keys


def test_double_broken_ref(env):
    result = link(env)
    entry = next(e for e in result.entries if e.key == "DOUBLE_REF")
    assert "MISSING_ONE" in entry.broken
    assert "BASE_URL" in entry.references
    assert "BASE_URL" not in entry.broken


def test_summary_string(env):
    result = link(env)
    s = result.summary()
    assert "6 entries checked" in s
    assert "broken" in s
