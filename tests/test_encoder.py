"""Tests for envguard.encoder."""
import base64
import urllib.parse

import pytest

from envguard.encoder import EncodeFormat, encode


@pytest.fixture()
def env():
    return {
        "DATABASE_URL": "postgres://user:pass@localhost/db",
        "SECRET_KEY": "s3cr3t!",
        "PORT": "8080",
    }


def test_encode_base64_all_keys(env):
    result = encode(env, fmt=EncodeFormat.BASE64)
    assert result.has_entries
    assert len(result.entries) == len(env)


def test_encode_base64_value_correct(env):
    result = encode(env, fmt=EncodeFormat.BASE64)
    entry = next(e for e in result.entries if e.key == "SECRET_KEY")
    expected = base64.b64encode(b"s3cr3t!").decode()
    assert entry.encoded == expected


def test_encode_url_value_correct(env):
    result = encode(env, fmt=EncodeFormat.URL)
    entry = next(e for e in result.entries if e.key == "DATABASE_URL")
    expected = urllib.parse.quote(env["DATABASE_URL"], safe="")
    assert entry.encoded == expected


def test_encode_hex_value_correct(env):
    result = encode(env, fmt=EncodeFormat.HEX)
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.encoded == "8080".encode().hex()


def test_encode_subset_of_keys(env):
    result = encode(env, fmt=EncodeFormat.BASE64, keys=["PORT"])
    assert len(result.entries) == 1
    assert result.entries[0].key == "PORT"


def test_encode_missing_key_is_skipped(env):
    result = encode(env, fmt=EncodeFormat.BASE64, keys=["NONEXISTENT"])
    assert not result.has_entries


def test_as_dict_returns_mapping(env):
    result = encode(env, fmt=EncodeFormat.BASE64)
    d = result.as_dict
    assert set(d.keys()) == set(env.keys())
    for key, encoded in d.items():
        assert encoded == base64.b64encode(env[key].encode()).decode()


def test_summary_contains_count_and_format(env):
    result = encode(env, fmt=EncodeFormat.HEX)
    summary = result.summary()
    assert "3" in summary
    assert "hex" in summary


def test_original_preserved_in_entry(env):
    result = encode(env, fmt=EncodeFormat.BASE64)
    entry = next(e for e in result.entries if e.key == "SECRET_KEY")
    assert entry.original == "s3cr3t!"


def test_format_stored_on_result(env):
    result = encode(env, fmt=EncodeFormat.URL)
    assert result.format == EncodeFormat.URL
