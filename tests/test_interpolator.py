"""Tests for envguard.interpolator."""
import pytest
from envguard.interpolator import interpolate, InterpolationResult


def test_no_references_returns_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = interpolate(env)
    assert result.resolved == {"HOST": "localhost", "PORT": "5432"}
    assert not result.has_warnings


def test_simple_brace_reference():
    env = {"BASE": "http://localhost", "URL": "${BASE}/api"}
    result = interpolate(env)
    assert result.resolved["URL"] == "http://localhost/api"


def test_simple_dollar_reference():
    env = {"USER": "admin", "DSN": "postgres://$USER@db"}
    result = interpolate(env)
    assert result.resolved["DSN"] == "postgres://admin@db"


def test_chained_references():
    env = {"SCHEME": "https", "HOST": "example.com", "BASE": "${SCHEME}://${HOST}"}
    result = interpolate(env)
    assert result.resolved["BASE"] == "https://example.com"


def test_nested_reference():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate(env)
    assert result.resolved["C"] == "hello_world!"


def test_undefined_reference_produces_warning_and_empty_string():
    env = {"URL": "${MISSING}/path"}
    result = interpolate(env)
    assert result.resolved["URL"] == "/path"
    assert result.has_warnings
    assert any("MISSING" in w.reference for w in result.warnings)


def test_circular_reference_produces_warning():
    env = {"A": "${B}", "B": "${A}"}
    result = interpolate(env)
    assert result.has_warnings
    messages = [w.message for w in result.warnings]
    assert any("Circular" in m for m in messages)


def test_self_reference_produces_warning():
    env = {"FOO": "${FOO}_bar"}
    result = interpolate(env)
    assert result.has_warnings
    assert any(w.variable == "FOO" for w in result.warnings)


def test_multiple_warnings_collected():
    env = {"X": "${MISSING1}", "Y": "${MISSING2}"}
    result = interpolate(env)
    assert len(result.warnings) == 2


def test_empty_env():
    result = interpolate({})
    assert result.resolved == {}
    assert not result.has_warnings
