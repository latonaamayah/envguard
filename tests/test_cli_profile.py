"""Tests for envguard.cli_profile."""
import json
import os
import pytest

from envguard.cli_profile import build_profile_parser, run_profile


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(env_file: str, output_format: str = "text"):
    parser = build_profile_parser()
    return parser.parse_args([env_file, "--format", output_format])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_run_profile_exits_zero(tmp_env):
    path = _write(tmp_env, "APP=hello\nPORT=8080\n")
    code = run_profile(_args(path))
    assert code == 0


def test_run_profile_missing_file_exits_two(tmp_path):
    missing = str(tmp_path / "missing.env")
    code = run_profile(_args(missing))
    assert code == 2


def test_run_profile_text_output(tmp_env, capsys):
    path = _write(tmp_env, "APP=hello\nPORT=8080\n")
    run_profile(_args(path, "text"))
    out = capsys.readouterr().out
    assert "Total variables" in out
    assert "2" in out


def test_run_profile_json_output(tmp_env, capsys):
    path = _write(tmp_env, "APP=hello\nPORT=8080\n")
    run_profile(_args(path, "json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total"] == 2


def test_run_profile_json_keys_present(tmp_env, capsys):
    path = _write(tmp_env, "SECRET_KEY=abc123\nDEBUG=true\n")
    run_profile(_args(path, "json"))
    data = json.loads(capsys.readouterr().out)
    expected_keys = {
        "total", "empty_count", "sensitive_count",
        "long_value_count", "numeric_count", "boolean_count",
        "avg_key_length", "avg_value_length",
    }
    assert expected_keys == set(data.keys())


def test_run_profile_sensitive_detected(tmp_env, capsys):
    path = _write(tmp_env, "API_KEY=topsecret\nHOST=localhost\n")
    run_profile(_args(path, "json"))
    data = json.loads(capsys.readouterr().out)
    assert data["sensitive_count"] >= 1
