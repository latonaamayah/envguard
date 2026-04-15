"""Tests for envguard.cli_tag."""
import argparse
import json
import pytest
from unittest.mock import patch

from envguard.cli_tag import build_tag_parser, run_tag, _parse_rules, run_tag_logic


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content: str):
    path.write_text(content)
    return path


def _args(env_file, rules=None, as_json=False):
    ns = argparse.Namespace(
        env_file=str(env_file),
        rules=rules or [],
        as_json=as_json,
    )
    return ns


def test_run_tag_exits_zero(tmp_env):
    _write(tmp_env, "DB_HOST=localhost\nAPP_NAME=myapp\n")
    args = _args(tmp_env, rules=["database:DB_"])
    assert run_tag(args) == 0


def test_run_tag_missing_file_exits_two(tmp_path):
    args = _args(tmp_path / "nonexistent.env")
    assert run_tag(args) == 2


def test_run_tag_json_output(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\n")
    args = _args(tmp_env, rules=["database:DB_"], as_json=True)
    run_tag(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "tagged" in data
    assert "untagged" in data
    assert "summary" in data


def test_run_tag_text_output_contains_key(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\n")
    args = _args(tmp_env, rules=["database:DB_"])
    run_tag(args)
    captured = capsys.readouterr()
    assert "DB_HOST" in captured.out


def test_parse_rules_single():
    rules = _parse_rules(["database:DB_"])
    assert rules == {"database": ["DB_"]}


def test_parse_rules_multiple_same_label():
    rules = _parse_rules(["cloud:AWS_", "cloud:GCP_"])
    assert rules["cloud"] == ["AWS_", "GCP_"]


def test_parse_rules_ignores_malformed():
    rules = _parse_rules(["nodivider"])
    assert rules == {}


def test_untagged_shown_in_text_output(tmp_env, capsys):
    _write(tmp_env, "MYSTERY_VAR=42\n")
    args = _args(tmp_env, rules=["database:DB_"])
    run_tag(args)
    captured = capsys.readouterr()
    assert "Untagged" in captured.out
    assert "MYSTERY_VAR" in captured.out


def test_build_tag_parser_returns_parser():
    parser = build_tag_parser()
    assert isinstance(parser, argparse.ArgumentParser)
