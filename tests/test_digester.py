import pytest
from envguard.digester import digest, DigestResult, DigestEntry


@pytest.fixture
def env():
    return {
        "DB_PASSWORD": "secret123",
        "API_KEY": "myapikey",
        "HOST": "localhost",
    }


def test_returns_digest_result(env):
    result = digest(env)
    assert isinstance(result, DigestResult)


def test_entry_count_matches_env(env):
    result = digest(env)
    assert len(result.entries) == 3


def test_has_entries_true(env):
    result = digest(env)
    assert result.has_entries()


def test_has_entries_false_empty():
    result = digest({})
    assert not result.has_entries()


def test_sha256_digest_length(env):
    result = digest(env, algorithm="sha256")
    for entry in result.entries:
        assert len(entry.digest) == 64


def test_md5_digest_length(env):
    result = digest(env, algorithm="md5")
    for entry in result.entries:
        assert len(entry.digest) == 32


def test_sha1_digest_length(env):
    result = digest(env, algorithm="sha1")
    for entry in result.entries:
        assert len(entry.digest) == 40


def test_digest_is_deterministic(env):
    r1 = digest(env, algorithm="sha256")
    r2 = digest(env, algorithm="sha256")
    assert r1.as_dict() == r2.as_dict()


def test_selective_keys(env):
    result = digest(env, keys=["DB_PASSWORD"])
    assert len(result.entries) == 1
    assert result.entries[0].key == "DB_PASSWORD"


def test_missing_key_skipped(env):
    result = digest(env, keys=["NONEXISTENT"])
    assert len(result.entries) == 0


def test_as_dict_keys(env):
    result = digest(env)
    d = result.as_dict()
    assert set(d.keys()) == {"DB_PASSWORD", "API_KEY", "HOST"}


def test_summary_contains_algorithm(env):
    result = digest(env, algorithm="md5")
    assert "md5" in result.summary()


def test_entry_str(env):
    result = digest(env, keys=["HOST"])
    s = str(result.entries[0])
    assert "HOST" in s
    assert "sha256" in s
